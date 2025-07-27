from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        popular_stocks = {
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
        
        self.wfile.write(json.dumps(popular_stocks).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()