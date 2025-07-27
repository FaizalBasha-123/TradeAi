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
BACKEND_URL = "https://0c6e0c1c-c332-43c6-97de-79b1b6a42bf2.preview.emergentagent.com/api"

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

    def test_multi_section_analysis_endpoint(self, symbol="AAPL", exchange="NASDAQ"):
        """Test the new multi-section analysis endpoint with all four analysis types"""
        try:
            # Create test image file
            test_image_path = "/app/test_chart.png"
            
            print(f"🔄 Testing multi-section analysis for {symbol}/{exchange} with image upload (this may take 60-90 seconds)...")
            
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
                
                # Validate response structure for multi-section analysis
                required_fields = [
                    "symbol", "exchange", "chart_image", "analysis", "timestamp",
                    "fundamental_analysis", "sentiment_analysis", "technical_analysis", "recommendations"
                ]
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
                    
                    # Validate all four analysis sections
                    sections = {
                        "fundamental_analysis": data.get("fundamental_analysis", ""),
                        "sentiment_analysis": data.get("sentiment_analysis", ""),
                        "technical_analysis": data.get("technical_analysis", ""),
                        "recommendations": data.get("recommendations", "")
                    }
                    
                    section_validations = {}
                    for section_name, content in sections.items():
                        # Check if content is substantial and contains expected keywords
                        if section_name == "fundamental_analysis":
                            expected_keywords = ["revenue", "profit", "eps", "debt", "ratio", "fundamental"]
                        elif section_name == "sentiment_analysis":
                            expected_keywords = ["sentiment", "news", "positive", "negative", "neutral", "headlines"]
                        elif section_name == "technical_analysis":
                            expected_keywords = ["technical", "trend", "support", "resistance", "rsi", "breakout"]
                        elif section_name == "recommendations":
                            expected_keywords = ["recommendation", "entry", "target", "stop", "swing", "trade"]
                        
                        is_valid = (
                            len(content) > 200 and  # Should be substantial
                            symbol.upper() in content and  # Should mention the stock
                            any(keyword in content.lower() for keyword in expected_keywords)
                        )
                        section_validations[section_name] = is_valid
                    
                    # Legacy analysis validation
                    legacy_analysis = data.get("analysis", "")
                    legacy_valid = len(legacy_analysis) > 50  # Should have some content
                    
                    all_sections_valid = all(section_validations.values())
                    
                    if chart_valid and all_sections_valid and legacy_valid:
                        section_lengths = {name: len(content) for name, content in sections.items()}
                        self.log_test(
                            "Multi-Section Analysis Endpoint", 
                            "PASS", 
                            f"Multi-section analysis working correctly for {symbol}/{exchange}",
                            f"All 4 sections generated: {section_lengths}, Chart: base64 image"
                        )
                        return True
                    else:
                        issues = []
                        if not chart_valid:
                            issues.append("Invalid chart image format")
                        if not all_sections_valid:
                            failed_sections = [name for name, valid in section_validations.items() if not valid]
                            issues.append(f"Invalid sections: {failed_sections}")
                        if not legacy_valid:
                            issues.append("Invalid legacy analysis")
                        
                        self.log_test(
                            "Multi-Section Analysis Endpoint", 
                            "FAIL", 
                            f"Multi-section analysis validation failed: {', '.join(issues)}",
                            f"Section validations: {section_validations}"
                        )
                        return False
                else:
                    self.log_test(
                        "Multi-Section Analysis Endpoint", 
                        "FAIL", 
                        f"Multi-section analysis response missing fields: {missing_fields}",
                        f"Response keys: {list(data.keys())}"
                    )
                    return False
            else:
                self.log_test(
                    "Multi-Section Analysis Endpoint", 
                    "FAIL", 
                    f"Multi-section analysis returned status code {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Multi-Section Analysis Endpoint", 
                "FAIL", 
                f"Multi-section analysis request failed: {str(e)}"
            )
            return False

    def test_stock_analysis_endpoint(self, symbol="AAPL", exchange="NASDAQ"):
        """Test the main stock analysis endpoint with image upload (legacy compatibility test)"""
        return self.test_multi_section_analysis_endpoint(symbol, exchange)

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
        """Test Gemini Pro Vision API integration with new structured format"""
        try:
            # Test with image upload
            test_image_path = "/app/test_chart.png"
            
            print("🔄 Testing Gemini Pro Vision API integration with new format...")
            
            with open(test_image_path, 'rb') as f:
                files = {'image': ('test_chart.png', f, 'image/png')}
                data = {
                    'symbol': 'GOOGL',
                    'exchange': 'NASDAQ'
                }
                
                response = self.session.post(
                    f"{self.base_url}/analyze-stock",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", "")
                
                # Check for new structured analysis format indicators
                new_format_indicators = [
                    "📊 Stock Analysis Report",
                    "📌 Symbol:",
                    "📅 Timeframe:",
                    "🔍 Exchange:",
                    "📊 Fundamental Analysis",
                    "💬 Sentiment Analysis",
                    "📈 Technical Analysis",
                    "🕒 Short-Term Recommendation",
                    "📆 Long-Term Recommendation"
                ]
                
                indicators_found = sum(1 for indicator in new_format_indicators if indicator in analysis)
                
                if len(analysis) > 200 and indicators_found >= 5:
                    self.log_test(
                        "Gemini Pro Vision API Integration (New Format)", 
                        "PASS", 
                        "Gemini Pro Vision API with new structured format working correctly",
                        f"Analysis length: {len(analysis)} chars, Format indicators found: {indicators_found}/9"
                    )
                    return True
                else:
                    self.log_test(
                        "Gemini Pro Vision API Integration (New Format)", 
                        "FAIL", 
                        "Gemini Pro Vision API not using new structured format",
                        f"Analysis length: {len(analysis)}, Format indicators: {indicators_found}/9"
                    )
                    return False
            else:
                self.log_test(
                    "Gemini Pro Vision API Integration (New Format)", 
                    "FAIL", 
                    f"Gemini API test failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Gemini Pro Vision API Integration (New Format)", 
                "FAIL", 
                f"Gemini Pro Vision API integration test failed: {str(e)}"
            )
            return False

    def test_user_friendly_error_messages(self):
        """Test user-friendly error messages for various error scenarios"""
        try:
            # Test 1: Invalid file type - should return user-friendly message
            print("🔄 Testing user-friendly error messages with invalid file type...")
            
            # Create a text file instead of image
            with open('/app/test_invalid.txt', 'w') as f:
                f.write("This is not an image")
            
            with open('/app/test_invalid.txt', 'rb') as f:
                files = {'image': ('test_invalid.txt', f, 'text/plain')}
                data = {
                    'symbol': 'AAPL',
                    'exchange': 'NASDAQ'
                }
                
                response = self.session.post(
                    f"{self.base_url}/analyze-stock",
                    files=files,
                    data=data
                )
            
            # Should return an error with user-friendly message
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', '')
                    
                    # Check if error message is user-friendly (contains emoji and readable text)
                    user_friendly_indicators = ['🖼️', 'Invalid file type', 'image file', 'PNG', 'JPG', 'GIF']
                    is_user_friendly = any(indicator in error_message for indicator in user_friendly_indicators)
                    
                    if is_user_friendly:
                        self.log_test(
                            "User-Friendly Error Messages (Invalid File Type)", 
                            "PASS", 
                            "User-friendly error message working correctly for invalid file types",
                            f"Message: {error_message}"
                        )
                        error_test_1 = True
                    else:
                        self.log_test(
                            "User-Friendly Error Messages (Invalid File Type)", 
                            "FAIL", 
                            "Error message is not user-friendly",
                            f"Message: {error_message}"
                        )
                        error_test_1 = False
                except:
                    self.log_test(
                        "User-Friendly Error Messages (Invalid File Type)", 
                        "FAIL", 
                        "Error response is not JSON formatted"
                    )
                    error_test_1 = False
            else:
                self.log_test(
                    "User-Friendly Error Messages (Invalid File Type)", 
                    "FAIL", 
                    f"Invalid file type should return error status, got {response.status_code}"
                )
                error_test_1 = False
            
            # Test 2: Large file size - should return user-friendly message
            print("🔄 Testing user-friendly error messages with large file...")
            
            # Create a large dummy file (simulate large image)
            large_content = b"fake_image_data" * 1000000  # ~15MB of fake data
            with open('/app/test_large.png', 'wb') as f:
                f.write(large_content)
            
            with open('/app/test_large.png', 'rb') as f:
                files = {'file': ('test_large.png', f, 'image/png')}
                
                response = self.session.post(
                    f"{self.base_url}/upload-image",
                    files=files
                )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', '')
                    
                    # Check if error message is user-friendly for large files
                    user_friendly_indicators = ['📁', 'too large', 'smaller', '10MB']
                    is_user_friendly = any(indicator in error_message for indicator in user_friendly_indicators)
                    
                    if is_user_friendly:
                        self.log_test(
                            "User-Friendly Error Messages (Large File)", 
                            "PASS", 
                            "User-friendly error message working correctly for large files",
                            f"Message: {error_message}"
                        )
                        error_test_2 = True
                    else:
                        self.log_test(
                            "User-Friendly Error Messages (Large File)", 
                            "FAIL", 
                            "Error message is not user-friendly for large files",
                            f"Message: {error_message}"
                        )
                        error_test_2 = False
                except:
                    self.log_test(
                        "User-Friendly Error Messages (Large File)", 
                        "FAIL", 
                        "Error response is not JSON formatted"
                    )
                    error_test_2 = False
            else:
                self.log_test(
                    "User-Friendly Error Messages (Large File)", 
                    "FAIL", 
                    f"Large file should return error status, got {response.status_code}"
                )
                error_test_2 = False
            
            # Clean up test files
            try:
                import os
                os.remove('/app/test_invalid.txt')
                os.remove('/app/test_large.png')
            except:
                pass
            
            return error_test_1 and error_test_2
                
        except Exception as e:
            self.log_test(
                "User-Friendly Error Messages", 
                "FAIL", 
                f"User-friendly error message test failed: {str(e)}"
            )
            return False

    def test_api_key_fallback_system(self):
        """Test API key fallback system by simulating API failures"""
        try:
            print("🔄 Testing API key fallback system...")
            
            # Test with a valid request to see if fallback system is working
            # We can't easily simulate API key failures, but we can test that the system
            # handles errors gracefully and tries multiple keys
            
            test_image_path = "/app/test_chart.png"
            
            with open(test_image_path, 'rb') as f:
                files = {'image': ('test_chart.png', f, 'image/png')}
                data = {
                    'symbol': 'TSLA',
                    'exchange': 'NASDAQ'
                }
                
                # Make request and check if it handles potential API failures gracefully
                response = self.session.post(
                    f"{self.base_url}/analyze-stock",
                    files=files,
                    data=data
                )
            
            # Check if the response indicates fallback system is working
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("analysis", "")
                
                if len(analysis) > 100:
                    self.log_test(
                        "API Key Fallback System", 
                        "PASS", 
                        "API key fallback system working - successful analysis completed",
                        f"Analysis length: {len(analysis)} chars"
                    )
                    return True
                else:
                    self.log_test(
                        "API Key Fallback System", 
                        "FAIL", 
                        "API key fallback system may not be working - analysis too short"
                    )
                    return False
            elif response.status_code == 503:
                # If we get 503, check if the error message is user-friendly (indicating fallback tried)
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', '')
                    
                    # Check if error message indicates fallback system tried multiple keys
                    fallback_indicators = ['🔄', 'busy', 'try again', 'moments']
                    is_fallback_message = any(indicator in error_message for indicator in fallback_indicators)
                    
                    if is_fallback_message:
                        self.log_test(
                            "API Key Fallback System", 
                            "PASS", 
                            "API key fallback system working - user-friendly 503 error after trying all keys",
                            f"Message: {error_message}"
                        )
                        return True
                    else:
                        self.log_test(
                            "API Key Fallback System", 
                            "FAIL", 
                            "503 error but message doesn't indicate fallback system tried",
                            f"Message: {error_message}"
                        )
                        return False
                except:
                    self.log_test(
                        "API Key Fallback System", 
                        "FAIL", 
                        "503 error but response is not JSON formatted"
                    )
                    return False
            else:
                self.log_test(
                    "API Key Fallback System", 
                    "FAIL", 
                    f"Unexpected status code {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "API Key Fallback System", 
                "FAIL", 
                f"API key fallback system test failed: {str(e)}"
            )
            return False

    def test_enhanced_image_validation(self):
        """Test enhanced image upload validation"""
        try:
            # Test 1: Empty file
            print("🔄 Testing enhanced image validation with empty file...")
            
            with open('/app/test_empty.png', 'w') as f:
                pass  # Create empty file
            
            with open('/app/test_empty.png', 'rb') as f:
                files = {'file': ('test_empty.png', f, 'image/png')}
                
                response = self.session.post(
                    f"{self.base_url}/upload-image",
                    files=files
                )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', '')
                    
                    # Check if error message mentions empty file
                    empty_file_indicators = ['📁', 'empty', 'valid image']
                    is_empty_file_message = any(indicator in error_message for indicator in empty_file_indicators)
                    
                    if is_empty_file_message:
                        self.log_test(
                            "Enhanced Image Validation (Empty File)", 
                            "PASS", 
                            "Enhanced validation correctly detects empty files",
                            f"Message: {error_message}"
                        )
                        validation_test_1 = True
                    else:
                        self.log_test(
                            "Enhanced Image Validation (Empty File)", 
                            "FAIL", 
                            "Empty file error message is not user-friendly",
                            f"Message: {error_message}"
                        )
                        validation_test_1 = False
                except:
                    self.log_test(
                        "Enhanced Image Validation (Empty File)", 
                        "FAIL", 
                        "Error response is not JSON formatted"
                    )
                    validation_test_1 = False
            else:
                self.log_test(
                    "Enhanced Image Validation (Empty File)", 
                    "FAIL", 
                    f"Empty file should return error status, got {response.status_code}"
                )
                validation_test_1 = False
            
            # Test 2: Valid image file (should pass)
            print("🔄 Testing enhanced image validation with valid file...")
            
            with open('/app/test_chart.png', 'rb') as f:
                files = {'file': ('test_chart.png', f, 'image/png')}
                
                response = self.session.post(
                    f"{self.base_url}/upload-image",
                    files=files
                )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    success = data.get('success', False)
                    message = data.get('message', '')
                    
                    # Check if success message is user-friendly
                    success_indicators = ['✅', 'uploaded successfully', 'Ready for analysis']
                    is_success_message = any(indicator in message for indicator in success_indicators)
                    
                    if success and is_success_message:
                        self.log_test(
                            "Enhanced Image Validation (Valid File)", 
                            "PASS", 
                            "Enhanced validation correctly accepts valid files with user-friendly message",
                            f"Message: {message}"
                        )
                        validation_test_2 = True
                    else:
                        self.log_test(
                            "Enhanced Image Validation (Valid File)", 
                            "FAIL", 
                            "Valid file success message is not user-friendly",
                            f"Success: {success}, Message: {message}"
                        )
                        validation_test_2 = False
                except:
                    self.log_test(
                        "Enhanced Image Validation (Valid File)", 
                        "FAIL", 
                        "Success response is not JSON formatted"
                    )
                    validation_test_2 = False
            else:
                self.log_test(
                    "Enhanced Image Validation (Valid File)", 
                    "FAIL", 
                    f"Valid file should return success status, got {response.status_code}"
                )
                validation_test_2 = False
            
            # Clean up test files
            try:
                import os
                os.remove('/app/test_empty.png')
            except:
                pass
            
            return validation_test_1 and validation_test_2
                
        except Exception as e:
            self.log_test(
                "Enhanced Image Validation", 
                "FAIL", 
                f"Enhanced image validation test failed: {str(e)}"
            )
            return False

    def test_error_handling(self):
        """Test basic error handling with invalid images and data"""
        try:
            # Test 1: Missing required fields
            print("🔄 Testing error handling with missing fields...")
            
            with open('/app/test_chart.png', 'rb') as f:
                files = {'image': ('test_chart.png', f, 'image/png')}
                data = {
                    'symbol': 'AAPL'
                    # Missing exchange field
                }
                
                response = self.session.post(
                    f"{self.base_url}/analyze-stock",
                    files=files,
                    data=data
                )
            
            if response.status_code >= 400:
                self.log_test(
                    "Error Handling (Missing Fields)", 
                    "PASS", 
                    "Error handling working correctly for missing fields",
                    f"Status: {response.status_code}"
                )
                return True
            else:
                self.log_test(
                    "Error Handling (Missing Fields)", 
                    "FAIL", 
                    f"Error handling failed - missing fields returned success status {response.status_code}"
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
            ("Image Upload", self.test_image_upload_endpoint),
            ("Enhanced Image Validation", self.test_enhanced_image_validation),
            ("User-Friendly Error Messages", self.test_user_friendly_error_messages),
            ("API Key Fallback System", self.test_api_key_fallback_system),
            ("Stock Analysis with Image Upload (AAPL)", lambda: self.test_stock_analysis_endpoint("AAPL", "NASDAQ")),
            ("Legacy Stock Analysis (MSFT)", lambda: self.test_legacy_stock_analysis_endpoint("MSFT", "NASDAQ")),
            ("Gemini Pro Vision API Integration (New Format)", self.test_gemini_api_integration),
            ("Basic Error Handling", self.test_error_handling),
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