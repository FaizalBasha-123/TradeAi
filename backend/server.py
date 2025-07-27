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
    os.getenv("GEMINI_API_KEY", "AIzaSyCMzGNiZz8ncza2JNbot7Dz5sOp5i7S0DI"),  # Primary - Your working key
    "AIzaSyDmHWwaQgiqZqIjp8FngAOkyIWYB-a3gQA",  # Backup 1
    "AIzaSyABxOKKuIJyZe0-0aw5GMgk-uPpTWuxcsM",  # Backup 2
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

# Multi-section analysis functions
async def analyze_with_gemini_api(api_key: str, prompt: str, chart_image_base64: str = None) -> str:
    """Generic function to analyze with Gemini API"""
    try:
        # Create LLM chat instance
        chat = LlmChat(
            api_key=api_key,
            session_id=f"stock_analysis_{uuid.uuid4()}",
            system_message="You are a professional stock market analyst."
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Create user message
        if chart_image_base64:
            # With image
            image_content = ImageContent(image_base64=chart_image_base64)
            user_message = UserMessage(
                text=prompt,
                file_contents=[image_content]
            )
        else:
            # Text only
            user_message = UserMessage(text=prompt)
        
        # Send message to Gemini and get response
        response = await chat.send_message(user_message)
        return response
        
    except Exception as e:
        raise e

async def get_fundamental_analysis(symbol: str, exchange: str) -> str:
    """Generate fundamental analysis using Gemini AI"""
    prompt = f"""You are a professional financial analyst. Based on your knowledge of {symbol.upper()} listed on {exchange.upper()}, provide a detailed fundamental analysis in this exact format:

📊 Fundamental Analysis
1. Revenue & Profitability
Revenue Growth (YoY): ₹2,49,386 Cr → ₹2,59,188 Cr (↑ ~3.9%)

Net Profit (YoY): ₹38,327 Cr → ₹42,303 Cr (↑ ~10.4%)

EBITDA Margin: ~25.0%

Net Profit Margin: ~16.3%

2. Earnings Per Share (EPS)
TTM EPS: ₹115.5

EPS Growth (YoY): 9.5%

Projected EPS FY26: ₹126 – ₹130

3. Return Ratios
ROE (Return on Equity): ~47%

ROCE (Return on Capital Employed): ~54%

ROA (Return on Assets): ~30%

4. Valuation Metrics
P/E Ratio (TTM): ~31.5x

Industry P/E: ~27x (Slightly overvalued)

P/B Ratio: ~14.7

PEG Ratio: ~2.2 (moderate)

5. Debt Analysis
Debt to Equity: 0.04 (Almost debt-free)

Interest Coverage Ratio: > 100 (Excellent)

6. Cash Flow Health
Operating Cash Flow: ₹61,728 Cr (healthy)

Free Cash Flow: ₹48,000 Cr

FCF Yield: ~3.3%

7. Dividend Track Record
Dividend Yield: ~3.16%

5-Year Dividend CAGR: 17%

Payout Ratio: ~75% (consistent high payouts)

8. Promoter & Institutional Holding
Promoter Holding: 72.3% (Stable)

FII Holding: 12.6%

DII Holding: 10.9%

9. Moat & Business Outlook
Strong Moat: Brand trust, client retention, and industry leadership

Client Base: >1200 global clients including multiple Fortune 500 companies

Order Book: Robust TCV of ~$42.7B

Future Outlook: Expanding in cloud, AI, and digital transformation segments

✅ Summary (Fundamentals Only)
Strengths:

Consistent revenue & profit growth

Debt-free with high cash reserves

High ROE and strong dividend policy

Leader in IT services with a global footprint

Risks:

Rich valuation (high P/E vs peers)

FX fluctuations due to high USD exposure

Dependency on global IT demand cycles

Verdict:
✔️ Strong fundamentals for long-term holding
⚠️ For swing trading, check earnings dates, corporate actions, and news events impacting short-term sentiment.

Replace the example data with actual estimates for {symbol.upper()}. Provide realistic numbers based on your knowledge of this company and its recent performance. Use appropriate currency symbols (₹ for Indian stocks, $ for US stocks). Only return the formatted analysis, no explanations."""
    
    # Try with multiple API keys
    for i, api_key in enumerate(GEMINI_API_KEYS):
        try:
            print(f"🔄 Fundamental Analysis - Trying API key {i+1}/{len(GEMINI_API_KEYS)}...")
            result = await analyze_with_gemini_api(api_key, prompt)
            print(f"✅ Fundamental Analysis - API key {i+1} successful!")
            return result
        except Exception as e:
            print(f"❌ Fundamental Analysis - API key {i+1} failed: {str(e)}")
            if i == len(GEMINI_API_KEYS) - 1:
                raise HTTPException(
                    status_code=503,
                    detail=get_user_friendly_error(str(e))
                )
            continue

async def get_sentiment_analysis(symbol: str, exchange: str) -> str:
    """Generate sentiment analysis using Gemini AI (AI reasoning mode)"""
    prompt = f"""You are an AI financial analyst with access to recent market data. Based on your knowledge and reasoning about {symbol.upper()} listed on {exchange.upper()}, simulate recent news sentiment analysis in this exact format:

💬 Sentiment Analysis – AI Mode (Based on Recent News)
✅ 1. What We Must Check
To generate reliable Sentiment Analysis, your AI prompt should guide Gemini to analyze recent news headlines, events, and trends. Here's what it should check:

Metric	Description
🔴 Positive/Negative/Neutral	Overall sentiment polarity
📰 Recent News Summary	Key headlines and events in the past 30 days
🔄 Impact on Stock	Interpretation of how news affects investor behavior
🏦 Sector Trend	Sentiment of the overall IT sector if available
🗣️ Public/Media Tone	Investor confidence, trust, or panic signals
🔎 Keywords	Words like "growth", "fraud", "expansion", "layoffs" etc.
🕵️ AI Reasoning	AI should extract sentiment context from multiple stories

💬 Stock Sentiment Report  
📌 Symbol: {symbol.upper()}  
📅 Timeframe: Last 30 Days  
🔍 Source: News Headlines & Market Events

📢 News-Based Summary  
- Headline 1: [Simulate realistic recent headline]
- Headline 2: [Simulate realistic recent headline]
- Headline 3: [Simulate realistic recent headline]

📈 Sentiment Overview  
- Overall Sentiment: Positive / Neutral / Negative  
- Investor Mood: Cautious / Bullish / Panic Driven  
- Sector Sentiment: Strong / Weak / Mixed  

🔎 Keyword Highlights  
- Positive Mentions: (e.g., "New client deals", "Cloud expansion")  
- Negative Mentions: (e.g., "Attrition", "IT slowdown", "Layoffs")  

🧠 AI Reasoning  
- Based on the news above, the sentiment is [verdict] because... (explain in 2–3 lines).

✅ Verdict:  
(Example: Slightly bullish due to consistent deal wins and sector recovery.)

Replace all placeholders with realistic simulated data for {symbol.upper()}. Use your knowledge of the company, industry trends, and typical market dynamics. Only return the formatted analysis, no explanations."""
    
    # Try with multiple API keys
    for i, api_key in enumerate(GEMINI_API_KEYS):
        try:
            print(f"🔄 Sentiment Analysis - Trying API key {i+1}/{len(GEMINI_API_KEYS)}...")
            result = await analyze_with_gemini_api(api_key, prompt)
            print(f"✅ Sentiment Analysis - API key {i+1} successful!")
            return result
        except Exception as e:
            print(f"❌ Sentiment Analysis - API key {i+1} failed: {str(e)}")
            if i == len(GEMINI_API_KEYS) - 1:
                raise HTTPException(
                    status_code=503,
                    detail=get_user_friendly_error(str(e))
                )
            continue

async def get_technical_analysis(symbol: str, exchange: str, chart_image_base64: str) -> str:
    """Generate technical analysis using Gemini AI with chart image"""
    prompt = f"""You are a professional technical analyst. Based on the attached 1-day timeframe chart of {symbol.upper()} (6-month or 1-year view), provide a detailed Technical Analysis Report in this exact format:

📈 Technical Analysis Report  
📌 Symbol: {symbol.upper()}  
📅 Timeframe: 1-Day Chart (Last 6 Months)  
🖼️ Chart: [analyzed image attached]

📊 Trend Analysis  
- Overall trend: Uptrend / Downtrend / Sideways  
- Support Zone: ₹xxx – ₹xxx  
- Resistance Zone: ₹xxx – ₹xxx

🔺 Breakout/Breakdown  
- Breakout Detected: Yes / No  
- Level: ₹xxx  
- Volume Confirmation: Yes / No

📐 Chart Patterns  
- Pattern Detected: (e.g., Ascending Triangle, Cup & Handle, Double Bottom)  
- Pattern Validity: Strong / Weak

📉 Indicators  
- RSI: xxx (Overbought / Oversold / Neutral)  
- SMA/EMA Crossover: (e.g., 50-SMA crossed 200-SMA → Golden Cross)  
- MACD Signal: Bullish / Bearish  
- Bollinger Band Status: Price near Upper / Lower band?

🎯 Entry/Exit Recommendation  
- Suggested Entry Range: ₹xxx – ₹xxx  
- Stop-Loss: ₹xxx  
- Target 1: ₹xxx  
- Target 2: ₹xxx

🧠 AI Summary  
(Explain the chart-based analysis in 2–3 sentences in natural language.)

✅ Verdict:  
(Example: Bullish setup with strong breakout from resistance + RSI supportive.)

Analyze the attached chart image and provide realistic price levels and technical indicators. Use appropriate currency symbols (₹ for Indian stocks, $ for US stocks). Only return the formatted analysis, no explanations."""
    
    # Try with multiple API keys
    for i, api_key in enumerate(GEMINI_API_KEYS):
        try:
            print(f"🔄 Technical Analysis - Trying API key {i+1}/{len(GEMINI_API_KEYS)}...")
            result = await analyze_with_gemini_api(api_key, prompt, chart_image_base64)
            print(f"✅ Technical Analysis - API key {i+1} successful!")
            return result
        except Exception as e:
            print(f"❌ Technical Analysis - API key {i+1} failed: {str(e)}")
            if i == len(GEMINI_API_KEYS) - 1:
                raise HTTPException(
                    status_code=503,
                    detail=get_user_friendly_error(str(e))
                )
            continue

async def get_recommendations(symbol: str, exchange: str) -> str:
    """Generate recommendations using Gemini AI"""
    prompt = f"""You are a professional stock analyst. Based on your combined analysis knowledge of {symbol.upper()} listed on {exchange.upper()}, provide a comprehensive recommendation in this exact format:

📌 Recommendation Summary  
📍 Stock: {symbol.upper()}  
📆 Timeframe: Swing (2–10 days)  
📈 Market View: Bullish / Bearish / Cautious

🧩 Combined Outlook  
- 🧠 Fundamentals: Strong / Weak / Neutral (reason)
- 💬 Sentiment: Positive / Negative / Neutral (reason)
- 📈 Technical: Bullish / Bearish / Neutral (reason)

🎯 Swing Trade Recommendation  
- Entry Range: ₹xxx – ₹xxx  
- Stop-Loss: ₹xxx  
- Target 1: ₹xxx  
- Target 2: ₹xxx  
- Risk Level: Low / Medium / High  
- Confidence Score: 80–90% (AI-estimated based on alignment of signals)

📆 Holding Period Suggestion: 5–7 trading days (can vary)

🔎 Reasoning:  
(Explain why this trade setup is favorable or risky based on combined analysis)

✅ Final Verdict:  
✔️ Action: Consider Entering / Wait & Watch / Avoid  
📢 Notes: (Earnings approaching / Sector uncertainty / Confirm on volume tomorrow etc.)

Provide realistic analysis based on your knowledge of {symbol.upper()}. Use appropriate currency symbols (₹ for Indian stocks, $ for US stocks). Only return the formatted recommendation, no explanations."""
    
    # Try with multiple API keys
    for i, api_key in enumerate(GEMINI_API_KEYS):
        try:
            print(f"🔄 Recommendations - Trying API key {i+1}/{len(GEMINI_API_KEYS)}...")
            result = await analyze_with_gemini_api(api_key, prompt)
            print(f"✅ Recommendations - API key {i+1} successful!")
            return result
        except Exception as e:
            print(f"❌ Recommendations - API key {i+1} failed: {str(e)}")
            if i == len(GEMINI_API_KEYS) - 1:
                raise HTTPException(
                    status_code=503,
                    detail=get_user_friendly_error(str(e))
                )
            continue

# Function to try multiple API keys with fallback (Legacy support)
async def analyze_with_fallback(symbol: str, exchange: str, chart_image_base64: str, use_legacy_prompt: bool = False) -> str:
    """Analyze stock using Gemini Pro Vision API with fallback support"""
    
    for i, api_key in enumerate(GEMINI_API_KEYS):
        try:
            print(f"🔄 Trying API key {i+1}/{len(GEMINI_API_KEYS)}...")
            
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

            # Use the generic analyze function
            result = await analyze_with_gemini_api(api_key, prompt, chart_image_base64)
            print(f"✅ API key {i+1} successful!")
            return result
            
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
            "message": "✅ Image uploaded successfully! Ready for analysis.",
            "image_data": image_base64,
            "filename": file.filename
        }
        
    except HTTPException as e:
        # Re-raise HTTPException as is (already user-friendly)
        raise e
    except Exception as e:
        print(f"Upload error: {str(e)}")
        user_friendly_error = get_user_friendly_error(str(e))
        raise HTTPException(status_code=500, detail=user_friendly_error)

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
        
        # Step 2: Analyze with Gemini using legacy prompt format (with fallback)
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
        # Re-raise HTTPException as is (already user-friendly)
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        user_friendly_error = get_user_friendly_error(str(e))
        raise HTTPException(status_code=500, detail=user_friendly_error)

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