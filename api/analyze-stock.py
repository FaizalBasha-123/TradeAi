from http.server import BaseHTTPRequestHandler
import json
import base64
import os
import cgi
import io
from datetime import datetime
import uuid

# Import for Gemini API
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
except ImportError:
    # Fallback for Vercel environment
    pass

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()

            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' not in content_type:
                raise Exception("Invalid content type")

            # Get form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Extract form fields
            symbol = form.getvalue('symbol', '').upper()
            exchange = form.getvalue('exchange', '').upper()
            
            # Get uploaded file
            if 'image' not in form:
                raise Exception("No image file uploaded")
            
            file_item = form['image']
            if not file_item.filename:
                raise Exception("No image file selected")

            # Read and encode image
            image_data = file_item.file.read()
            if len(image_data) == 0:
                raise Exception("📁 The uploaded file is empty")
            
            if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
                raise Exception("📁 The uploaded image is too large. Please use an image smaller than 10MB.")

            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Get Gemini API key
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            if not gemini_api_key:
                raise Exception("🔐 Gemini API key not configured")

            # Analyze with Gemini (simplified for Vercel)
            try:
                analysis = self.analyze_with_gemini(symbol, exchange, image_base64, gemini_api_key)
            except Exception as e:
                analysis = f"⚠️ Analysis temporarily unavailable: {str(e)}\n\nThis is a demo response for the uploaded chart of {symbol} ({exchange})."

            # Return response
            response = {
                "symbol": symbol,
                "exchange": exchange,
                "chart_image": f"data:image/png;base64,{image_base64}",
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())

    def analyze_with_gemini(self, symbol, exchange, image_base64, api_key):
        """Analyze stock using Gemini Pro Vision API"""
        try:
            # Create LLM chat instance
            chat = LlmChat(
                api_key=api_key,
                session_id=f"stock_analysis_{uuid.uuid4()}",
                system_message="You are a professional stock market analyst."
            ).with_model("gemini", "gemini-2.0-flash")
            
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

            # Create image content and user message
            image_content = ImageContent(image_base64=image_base64)
            user_message = UserMessage(
                text=prompt,
                file_contents=[image_content]
            )
            
            # Send message and get response
            response = chat.send_message(user_message)
            return response
            
        except Exception as e:
            raise Exception(f"🔄 The AI service is currently busy. Please try again in a few moments. ({str(e)})")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()