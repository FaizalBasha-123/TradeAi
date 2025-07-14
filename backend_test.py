#!/usr/bin/env python3
"""
Backend API Testing Suite for Stock Analysis Tool
Tests all backend endpoints and external API integrations
"""

import requests
import json
import base64
import time
from datetime import datetime
import sys

# Backend URL from frontend .env
BACKEND_URL = "https://5fdbd83b-9dd6-464a-897e-e267fe0789f2.preview.emergentagent.com/api"

class StockAnalysisAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 60  # 60 second timeout for API calls
        
    def log_test(self, test_name, status, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "active":
                    self.log_test(
                        "Health Endpoint", 
                        "PASS", 
                        "Health endpoint working correctly",
                        f"Response: {data}"
                    )
                    return True
                else:
                    self.log_test(
                        "Health Endpoint", 
                        "FAIL", 
                        "Health endpoint returned unexpected status",
                        f"Expected status 'active', got: {data.get('status')}"
                    )
                    return False
            else:
                self.log_test(
                    "Health Endpoint", 
                    "FAIL", 
                    f"Health endpoint returned status code {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Health Endpoint", 
                "FAIL", 
                f"Health endpoint request failed: {str(e)}"
            )
            return False

    def test_popular_stocks_endpoint(self):
        """Test the popular stocks endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/popular-stocks")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "popular_stocks" in data and isinstance(data["popular_stocks"], list):
                    stocks = data["popular_stocks"]
                    
                    # Check if we have stocks and they have required fields
                    if len(stocks) > 0:
                        sample_stock = stocks[0]
                        required_fields = ["symbol", "exchange", "name"]
                        
                        if all(field in sample_stock for field in required_fields):
                            self.log_test(
                                "Popular Stocks Endpoint", 
                                "PASS", 
                                f"Popular stocks endpoint working correctly with {len(stocks)} stocks",
                                f"Sample stock: {sample_stock}"
                            )
                            return True
                        else:
                            self.log_test(
                                "Popular Stocks Endpoint", 
                                "FAIL", 
                                "Popular stocks missing required fields",
                                f"Required: {required_fields}, Sample: {sample_stock}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Popular Stocks Endpoint", 
                            "FAIL", 
                            "Popular stocks endpoint returned empty list"
                        )
                        return False
                else:
                    self.log_test(
                        "Popular Stocks Endpoint", 
                        "FAIL", 
                        "Popular stocks endpoint returned invalid structure",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Popular Stocks Endpoint", 
                    "FAIL", 
                    f"Popular stocks endpoint returned status code {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Popular Stocks Endpoint", 
                "FAIL", 
                f"Popular stocks endpoint request failed: {str(e)}"
            )
            return False

    def test_image_upload_endpoint(self):
        """Test the image upload endpoint"""
        try:
            # Create test image file
            test_image_path = "/app/test_chart.png"
            
            with open(test_image_path, 'rb') as f:
                files = {'file': ('test_chart.png', f, 'image/png')}
                
                print("🔄 Testing image upload endpoint...")
                
                response = self.session.post(
                    f"{self.base_url}/upload-image",
                    files=files
                )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["success", "message", "image_data", "filename"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields and data.get("success") == True:
                    # Validate image_data is base64
                    image_data = data.get("image_data", "")
                    try:
                        base64.b64decode(image_data)
                        self.log_test(
                            "Image Upload Endpoint", 
                            "PASS", 
                            "Image upload endpoint working correctly",
                            f"Filename: {data.get('filename')}, Image data length: {len(image_data)} chars"
                        )
                        return True
                    except Exception:
                        self.log_test(
                            "Image Upload Endpoint", 
                            "FAIL", 
                            "Image upload returned invalid base64 data"
                        )
                        return False
                else:
                    self.log_test(
                        "Image Upload Endpoint", 
                        "FAIL", 
                        f"Image upload response missing fields or failed: {missing_fields}",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Image Upload Endpoint", 
                    "FAIL", 
                    f"Image upload returned status code {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Image Upload Endpoint", 
                "FAIL", 
                f"Image upload request failed: {str(e)}"
            )
            return False

    def test_stock_analysis_endpoint(self, symbol="AAPL", exchange="NASDAQ"):
        """Test the main stock analysis endpoint with image upload"""
        try:
            # Create test image file
            test_image_path = "/app/test_chart.png"
            
            print(f"🔄 Testing stock analysis for {symbol}/{exchange} with image upload (this may take 30-60 seconds)...")
            
            with open(test_image_path, 'rb') as f:
                files = {'image': ('test_chart.png', f, 'image/png')}
                data = {
                    'symbol': symbol,
                    'exchange': exchange
                }
                
                response = self.session.post(
                    f"{self.base_url}/analyze-stock",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["symbol", "exchange", "chart_image", "analysis", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Validate chart image is base64
                    chart_image = data.get("chart_image", "")
                    if chart_image.startswith("data:image/png;base64,"):
                        base64_data = chart_image.split(",")[1]
                        try:
                            # Try to decode base64 to validate
                            base64.b64decode(base64_data)
                            chart_valid = True
                        except Exception:
                            chart_valid = False
                    else:
                        chart_valid = False
                    
                    # Validate analysis content
                    analysis = data.get("analysis", "")
                    analysis_valid = (
                        len(analysis) > 100 and  # Should be substantial
                        symbol.upper() in analysis and  # Should mention the stock
                        any(keyword in analysis.lower() for keyword in [
                            "technical", "analysis", "price", "stock", "trading", "recommendation"
                        ])
                    )
                    
                    if chart_valid and analysis_valid:
                        self.log_test(
                            "Stock Analysis Endpoint", 
                            "PASS", 
                            f"Stock analysis working correctly for {symbol}/{exchange}",
                            f"Analysis length: {len(analysis)} chars, Chart: base64 image"
                        )
                        return True
                    else:
                        issues = []
                        if not chart_valid:
                            issues.append("Invalid chart image format")
                        if not analysis_valid:
                            issues.append("Invalid analysis content")
                        
                        self.log_test(
                            "Stock Analysis Endpoint", 
                            "FAIL", 
                            f"Stock analysis validation failed: {', '.join(issues)}",
                            f"Chart starts with: {chart_image[:50]}..., Analysis length: {len(analysis)}"
                        )
                        return False
                else:
                    self.log_test(
                        "Stock Analysis Endpoint", 
                        "FAIL", 
                        f"Stock analysis response missing fields: {missing_fields}",
                        f"Response keys: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_test(
                    "Stock Analysis Endpoint", 
                    "FAIL", 
                    f"Stock analysis returned status code {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Stock Analysis Endpoint", 
                "FAIL", 
                f"Stock analysis request failed: {str(e)}"
            )
            return False

    def test_legacy_stock_analysis_endpoint(self, symbol="AAPL", exchange="NASDAQ"):
        """Test the legacy stock analysis endpoint"""
        try:
            payload = {
                "symbol": symbol,
                "exchange": exchange
            }
            
            print(f"🔄 Testing legacy stock analysis for {symbol}/{exchange} (this may take 30-60 seconds)...")
            
            response = self.session.post(
                f"{self.base_url}/analyze-stock-legacy",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["symbol", "exchange", "chart_image", "analysis", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Validate chart image is base64
                    chart_image = data.get("chart_image", "")
                    if chart_image.startswith("data:image/png;base64,"):
                        base64_data = chart_image.split(",")[1]
                        try:
                            # Try to decode base64 to validate
                            base64.b64decode(base64_data)
                            chart_valid = True
                        except Exception:
                            chart_valid = False
                    else:
                        chart_valid = False
                    
                    # Validate analysis content
                    analysis = data.get("analysis", "")
                    analysis_valid = (
                        len(analysis) > 100 and  # Should be substantial
                        symbol.upper() in analysis and  # Should mention the stock
                        any(keyword in analysis.lower() for keyword in [
                            "technical", "analysis", "price", "stock", "trading", "recommendation"
                        ])
                    )
                    
                    if chart_valid and analysis_valid:
                        self.log_test(
                            "Legacy Stock Analysis Endpoint", 
                            "PASS", 
                            f"Legacy stock analysis working correctly for {symbol}/{exchange}",
                            f"Analysis length: {len(analysis)} chars, Chart: base64 image"
                        )
                        return True
                    else:
                        issues = []
                        if not chart_valid:
                            issues.append("Invalid chart image format")
                        if not analysis_valid:
                            issues.append("Invalid analysis content")
                        
                        self.log_test(
                            "Legacy Stock Analysis Endpoint", 
                            "FAIL", 
                            f"Legacy stock analysis validation failed: {', '.join(issues)}",
                            f"Chart starts with: {chart_image[:50]}..., Analysis length: {len(analysis)}"
                        )
                        return False
                else:
                    self.log_test(
                        "Legacy Stock Analysis Endpoint", 
                        "FAIL", 
                        f"Legacy stock analysis response missing fields: {missing_fields}",
                        f"Response keys: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_test(
                    "Legacy Stock Analysis Endpoint", 
                    "FAIL", 
                    f"Legacy stock analysis returned status code {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Legacy Stock Analysis Endpoint", 
                "FAIL", 
                f"Legacy stock analysis request failed: {str(e)}"
            )
            return False

    def test_gemini_api_integration(self):
        """Test Gemini Pro Vision API integration specifically"""
        try:
            # Test with a simple stock
            payload = {"symbol": "GOOGL", "exchange": "NASDAQ"}
            
            print("🔄 Testing Gemini Pro Vision API integration...")
            
            response = self.session.post(
                f"{self.base_url}/analyze-stock",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", "")
                
                # Check for structured analysis content that indicates Gemini is working
                gemini_indicators = [
                    "technical analysis",
                    "stock analysis",
                    "recommendation",
                    "market sentiment",
                    "price movement",
                    "trading",
                    "GOOGL" in analysis.upper()
                ]
                
                indicators_found = sum(1 for indicator in gemini_indicators if 
                                     (indicator if isinstance(indicator, bool) else indicator.lower() in analysis.lower()))
                
                if len(analysis) > 200 and indicators_found >= 4:
                    self.log_test(
                        "Gemini Pro Vision API Integration", 
                        "PASS", 
                        "Gemini Pro Vision API integration working correctly",
                        f"Analysis length: {len(analysis)} chars, Indicators found: {indicators_found}/7"
                    )
                    return True
                else:
                    self.log_test(
                        "Gemini Pro Vision API Integration", 
                        "FAIL", 
                        "Gemini Pro Vision API returned insufficient analysis",
                        f"Analysis length: {len(analysis)}, Indicators: {indicators_found}/7"
                    )
                    return False
            else:
                self.log_test(
                    "Gemini Pro Vision API Integration", 
                    "FAIL", 
                    f"Gemini API test failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Gemini Pro Vision API Integration", 
                "FAIL", 
                f"Gemini Pro Vision API integration test failed: {str(e)}"
            )
            return False

    def test_error_handling(self):
        """Test error handling with invalid stock symbols"""
        try:
            # Test with invalid stock symbol
            payload = {"symbol": "INVALID123", "exchange": "NASDAQ"}
            
            print("🔄 Testing error handling with invalid stock symbol...")
            
            response = self.session.post(
                f"{self.base_url}/analyze-stock",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return an error status code (4xx or 5xx)
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        self.log_test(
                            "Error Handling", 
                            "PASS", 
                            "Error handling working correctly for invalid symbols",
                            f"Status: {response.status_code}, Error: {error_data['detail']}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Error Handling", 
                            "WARN", 
                            "Error handling works but response format could be improved",
                            f"Status: {response.status_code}, Response: {response.text}"
                        )
                        return True
                except:
                    self.log_test(
                        "Error Handling", 
                        "WARN", 
                        "Error handling works but response is not JSON",
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return True
            else:
                self.log_test(
                    "Error Handling", 
                    "FAIL", 
                    f"Error handling failed - invalid symbol returned success status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Error Handling", 
                "FAIL", 
                f"Error handling test failed: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Testing Suite")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test results tracking
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Popular Stocks", self.test_popular_stocks_endpoint),
            ("Stock Analysis (AAPL)", lambda: self.test_stock_analysis_endpoint("AAPL", "NASDAQ")),
            ("Chart-Img API Integration", self.test_chart_img_api_integration),
            ("Gemini Pro Vision API Integration", self.test_gemini_api_integration),
            ("Error Handling", self.test_error_handling),
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Test execution failed: {str(e)}")
                failed += 1
        
        # Count warnings
        warnings = sum(1 for result in self.test_results if result["status"] == "WARN")
        
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
        
        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "total": passed + failed,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = StockAnalysisAPITester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)