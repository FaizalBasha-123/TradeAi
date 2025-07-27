from http.server import BaseHTTPRequestHandler
import json
import base64
import cgi

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
            
            # Get uploaded file
            if 'file' not in form:
                raise Exception("No file uploaded")
            
            file_item = form['file']
            if not file_item.filename:
                raise Exception("No file selected")

            # Read and validate image
            image_data = file_item.file.read()
            
            if len(image_data) == 0:
                raise Exception("📁 The uploaded file is empty")
            
            if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
                raise Exception("📁 The uploaded image is too large. Please use an image smaller than 10MB.")

            # Convert to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Return success response
            response = {
                "success": True,
                "message": "✅ Image uploaded successfully! Ready for analysis.",
                "image_data": image_base64,
                "filename": file_item.filename
            }

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()