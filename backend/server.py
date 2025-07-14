import os
import json
import base64
import requests
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
import asyncio
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

app = FastAPI(title="Stock Analysis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys from environment with fallback system
CHART_IMG_API_KEY = os.getenv("CHART_IMG_API_KEY")  # Required for chart generation
GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY", "AIzaSyDmHWwaQgiqZqIjp8FngAOkyIWYB-a3gQA"),  # Primary
    "AIzaSyABxOKKuIJyZe0-0aw5GMgk-uPpTWuxcsM",  # Backup 1
    "AIzaSyCMzGNiZz8ncza2JNbot7Dz5sOp5i7S0DI"   # Backup 2
]
GEMINI_API_KEY = GEMINI_API_KEYS[0]  # For backward compatibility

# Request/Response models
class StockAnalysisRequest(BaseModel):
    symbol: str
    exchange: str
    image_data: Optional[str] = None  # Base64 encoded image data

class StockAnalysisResponse(BaseModel):
    symbol: str
    exchange: str
    chart_image: str
    analysis: str
    timestamp: str

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "active", "message": "Stock Analysis API is running"}

# Function to handle user-friendly error messages
def get_user_friendly_error(error_str: str) -> str:
    """Convert technical error messages to user-friendly messages"""
    error_lower = error_str.lower()
    
    if "503" in error_str or "overloaded" in error_lower or "unavailable" in error_lower:
        return "🔄 The AI service is currently busy. Please try again in a few moments."
    elif "401" in error_str or "unauthorized" in error_lower:
        return "🔐 Authentication issue with the AI service. Please contact support."
    elif "429" in error_str or "rate limit" in error_lower:
        return "⏳ Too many requests. Please wait a moment and try again."
    elif "timeout" in error_lower:
        return "⏱️ The analysis is taking longer than expected. Please try again."
    elif "network" in error_lower or "connection" in error_lower:
        return "🌐 Network connectivity issue. Please check your internet connection."
    elif "file" in error_lower and "size" in error_lower:
        return "📁 The uploaded image is too large. Please use a smaller image file."
    elif "invalid" in error_lower and "image" in error_lower:
        return "🖼️ Invalid image format. Please upload a valid chart image (PNG, JPG, or GIF)."
    else:
        return "⚠️ Something went wrong during analysis. Please try again or contact support."

# Function to try multiple API keys with fallback
async def analyze_with_fallback(symbol: str, exchange: str, chart_image_base64: str, use_legacy_prompt: bool = False) -> str:
    """Analyze stock using Gemini Pro Vision API with fallback support"""
    
    for i, api_key in enumerate(GEMINI_API_KEYS):
        try:
            print(f"🔄 Trying API key {i+1}/{len(GEMINI_API_KEYS)}...")
            
            # Create LLM chat instance
            chat = LlmChat(
                api_key=api_key,
                session_id=f"stock_analysis_{uuid.uuid4()}",
                system_message="You are a professional stock market analyst."
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Choose prompt based on flag
            if use_legacy_prompt:
                prompt = f"""
You are a professional stock market analyst. Generate a comprehensive stock analysis report based on this chart and stock information:

📊 **Stock Information:**
- Symbol: {symbol.upper()}
- Exchange: {exchange.upper()}
- Timeframe: 1 Day
- Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please provide a detailed analysis in the following structured format:

# 📈 STOCK ANALYSIS REPORT

## 📌 Stock Overview
- **Symbol:** {symbol.upper()}
- **Exchange:** {exchange.upper()}
- **Current Analysis:** 1-Day Chart Analysis

## 🔍 Technical Analysis
Based on the 1-day chart, analyze:
- **Price Movement:** Current price trends and patterns
- **Support/Resistance Levels:** Key price levels to watch
- **Volume Analysis:** Trading volume patterns
- **Technical Indicators:** Moving averages, momentum indicators
- **Chart Patterns:** Any notable formations

## 💹 Market Sentiment
- **Overall Sentiment:** Bullish/Bearish/Neutral assessment
- **Market Context:** How this stock fits in current market conditions
- **Volatility Assessment:** Price stability analysis

## 📊 Key Observations
- **Notable Price Movements:** Significant changes in the timeframe
- **Trading Activity:** Volume and liquidity assessment
- **Risk Factors:** Potential concerns or red flags

## 🎯 Trading Recommendations

### Short-Term (1-3 Days)
- **Recommendation:** Buy/Hold/Sell
- **Target Price:** If applicable
- **Stop Loss:** Risk management level
- **Rationale:** Brief explanation

### Medium-Term (1-4 Weeks)
- **Outlook:** Positive/Negative/Neutral
- **Key Levels:** Important price points to watch
- **Catalysts:** Events that might impact price

## ⚠️ Risk Assessment
- **Risk Level:** High/Medium/Low
- **Key Risks:** Major factors that could affect the stock
- **Diversification:** Portfolio considerations

## 📋 Summary
Provide a concise summary of your analysis and key takeaways for investors.

---
**Disclaimer:** This analysis is for educational purposes only and should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions.

Please analyze the provided chart image and provide this comprehensive report.
"""
            else:
                prompt = f"""You are a professional stock market analyst.

I will provide you:
1. A stock chart image (candlestick, 1D interval, last 30 days)
2. The stock symbol and exchange name

Based on the image and information, generate a full stock analysis report in this exact format:

📊 Stock Analysis Report

📌 Symbol: {symbol.upper()}
📅 Timeframe: Last 30 Days
🔍 Exchange: {exchange.upper()}

📊 Fundamental Analysis
• Revenue Growth YoY: ...
• Revenue Growth QoQ: ...
• EPS: ₹... | Projected: ₹...
• Debt-to-Equity: ... | Interest Coverage: ...

💬 Sentiment Analysis
• News Sentiment: 👍/👎 Positive/Negative
• Reason: ...
• Social Buzz: ...

📈 Technical Analysis
• CMP (Current Market Price): ₹...
• Breakout Detected: ✅/❌
• Breakout Date: YYYY-MM-DD
• RSI: ... | SMA Crossover: ✅/❌
• Reason: ...

🕒 Short-Term Recommendation
• Breakout Detected: ✅/❌
• Trend: Bullish/Bearish
• Entry: ₹... | CMP: ₹...
• Target 1: ₹... | Target 2: ₹...
• RSI: ... | SMA Crossover: ...
• 📉 Reason: ...

📆 Long-Term Recommendation
• Breakout Detected: ✅/❌
• Trend: Bullish/Bearish
• Entry: ₹... | CMP: ₹...
• Target 1: ₹... | Target 2: ₹...
• RSI: ... | SMA Crossover: ...
• 📉 Reason: ...

Only return the structured markdown-formatted report. Do not include explanations or extra notes.

Stock Symbol: {symbol.upper()}
Exchange: {exchange.upper()}

The chart image is attached below."""

            # Create image content from base64
            image_content = ImageContent(image_base64=chart_image_base64)
            
            # Create user message with prompt and image
            user_message = UserMessage(
                text=prompt,
                file_contents=[image_content]
            )
            
            # Send message to Gemini and get response
            response = await chat.send_message(user_message)
            
            print(f"✅ API key {i+1} successful!")
            return response
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ API key {i+1} failed: {error_str}")
            
            # If this is the last API key, raise the error
            if i == len(GEMINI_API_KEYS) - 1:
                user_friendly_error = get_user_friendly_error(error_str)
                raise HTTPException(
                    status_code=503, 
                    detail=user_friendly_error
                )
            
            # If it's a 503 error, try the next key
            if "503" in error_str or "overloaded" in error_str.lower():
                continue
            else:
                # For other errors, also try the next key
                continue
    
    # This should never be reached, but just in case
    raise HTTPException(
        status_code=503, 
        detail="🔄 All AI services are currently busy. Please try again in a few moments."
    )

# Function to handle uploaded image
async def process_uploaded_image(image_file: UploadFile) -> str:
    """Process uploaded image file and return as base64"""
    try:
        # Check file size (limit to 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        
        # Read image content
        image_content = await image_file.read()
        
        if len(image_content) > max_size:
            raise HTTPException(
                status_code=400, 
                detail="📁 The uploaded image is too large. Please use an image smaller than 10MB."
            )
        
        # Validate file type
        if not image_file.content_type or not image_file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="🖼️ Invalid file type. Please upload a valid image file (PNG, JPG, or GIF)."
            )
        
        # Validate file has content
        if len(image_content) == 0:
            raise HTTPException(
                status_code=400, 
                detail="📁 The uploaded file is empty. Please select a valid image file."
            )
        
        # Convert to base64
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        return image_base64
        
    except HTTPException as e:
        # Re-raise HTTPException as is
        raise e
    except Exception as e:
        print(f"Error processing uploaded image: {str(e)}")
        error_msg = get_user_friendly_error(str(e))
        raise HTTPException(status_code=500, detail=error_msg)

# Function to fetch chart image from Chart-Img API (DEPRECATED - will be removed)
async def fetch_chart_image(symbol: str, exchange: str) -> str:
    """Fetch stock chart image from Chart-Img API and return as base64"""
    try:
        headers = {
            "x-api-key": CHART_IMG_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Construct symbol in the format expected by Chart-Img API
        full_symbol = f"{exchange.upper()}:{symbol.upper()}"
        
        params = {
            "symbol": full_symbol,
            "interval": "1D",  # 1 day timeframe as requested
            "width": 800,
            "height": 400,
            "theme": "dark"
        }
        
        print(f"Fetching chart for {full_symbol} with params: {params}")
        
        response = requests.get(
            "https://api.chart-img.com/v1/tradingview/mini-chart",
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            # Convert image to base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            return image_base64
        else:
            print(f"Chart API error: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch chart: {response.text}"
            )
            
    except Exception as e:
        print(f"Error fetching chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chart fetch error: {str(e)}")

# Function to analyze stock using Gemini Pro Vision (Legacy version)
async def analyze_stock_with_gemini_legacy(symbol: str, exchange: str, chart_image_base64: str) -> str:
    """Legacy analysis using Gemini Pro Vision API with fallback support"""
    return await analyze_with_fallback(symbol, exchange, chart_image_base64, use_legacy_prompt=True)

# Function to analyze stock using Gemini Pro Vision (New Format)
async def analyze_stock_with_gemini(symbol: str, exchange: str, chart_image_base64: str) -> str:
    """Analyze stock using Gemini Pro Vision API with new prompt format and fallback support"""
    return await analyze_with_fallback(symbol, exchange, chart_image_base64, use_legacy_prompt=False)



# Image upload endpoint
@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload and process stock chart image"""
    try:
        # Process uploaded image
        image_base64 = await process_uploaded_image(file)
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "image_data": image_base64,
            "filename": file.filename
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Main endpoint for stock analysis (Updated for image uploads)
@app.post("/api/analyze-stock", response_model=StockAnalysisResponse)
async def analyze_stock(
    symbol: str = Form(...),
    exchange: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Analyze a stock using uploaded chart image and AI-powered analysis
    """
    try:
        print(f"Starting analysis for {symbol} on {exchange}")
        
        # Step 1: Process uploaded image
        chart_image_base64 = await process_uploaded_image(image)
        print("Chart image processed successfully")
        
        # Step 2: Analyze with Gemini (with fallback)
        analysis = await analyze_stock_with_gemini(
            symbol, 
            exchange, 
            chart_image_base64
        )
        print("Analysis completed successfully")
        
        # Step 3: Return comprehensive response
        return StockAnalysisResponse(
            symbol=symbol.upper(),
            exchange=exchange.upper(),
            chart_image=f"data:image/png;base64,{chart_image_base64}",
            analysis=analysis,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException as e:
        # Re-raise HTTPException as is (already user-friendly)
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        user_friendly_error = get_user_friendly_error(str(e))
        raise HTTPException(status_code=500, detail=user_friendly_error)

# Legacy endpoint for backward compatibility (DEPRECATED)
@app.post("/api/analyze-stock-legacy", response_model=StockAnalysisResponse)
async def analyze_stock_legacy(request: StockAnalysisRequest):
    """
    Legacy endpoint: Analyze a stock by fetching its chart and getting AI-powered analysis
    """
    try:
        print(f"Starting legacy analysis for {request.symbol} on {request.exchange}")
        
        # Step 1: Fetch chart image (using Chart-Img API for backward compatibility)
        chart_image_base64 = await fetch_chart_image(request.symbol, request.exchange)
        print("Chart image fetched successfully")
        
        # Step 2: Analyze with Gemini using old prompt format
        analysis = await analyze_stock_with_gemini_legacy(
            request.symbol, 
            request.exchange, 
            chart_image_base64
        )
        print("Analysis completed successfully")
        
        # Step 3: Return comprehensive response
        return StockAnalysisResponse(
            symbol=request.symbol.upper(),
            exchange=request.exchange.upper(),
            chart_image=f"data:image/png;base64,{chart_image_base64}",
            analysis=analysis,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Get popular stocks endpoint
@app.get("/api/popular-stocks")
async def get_popular_stocks():
    """Get a list of popular stocks for quick analysis"""
    return {
        "popular_stocks": [
            {"symbol": "AAPL", "exchange": "NASDAQ", "name": "Apple Inc."},
            {"symbol": "GOOGL", "exchange": "NASDAQ", "name": "Alphabet Inc."},
            {"symbol": "MSFT", "exchange": "NASDAQ", "name": "Microsoft Corporation"},
            {"symbol": "TSLA", "exchange": "NASDAQ", "name": "Tesla Inc."},
            {"symbol": "AMZN", "exchange": "NASDAQ", "name": "Amazon.com Inc."},
            {"symbol": "TCS", "exchange": "NSE", "name": "Tata Consultancy Services"},
            {"symbol": "RELIANCE", "exchange": "NSE", "name": "Reliance Industries"},
            {"symbol": "INFY", "exchange": "NSE", "name": "Infosys Limited"},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)