from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        genres = [
            {"id": "pop", "name": "Pop", "description": "Popular mainstream music"},
            {"id": "rock", "name": "Rock", "description": "Rock and alternative music"},
            {"id": "jazz", "name": "Jazz", "description": "Jazz and swing music"},
            {"id": "classical", "name": "Classical", "description": "Classical orchestral music"},
            {"id": "electronic", "name": "Electronic", "description": "Electronic and synth music"},
            {"id": "hip-hop", "name": "Hip-Hop", "description": "Hip-hop and rap music"},
            {"id": "ambient", "name": "Ambient", "description": "Atmospheric and ambient music"},
            {"id": "cinematic", "name": "Cinematic", "description": "Epic orchestral and dramatic music"}
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.end_headers()
        
        response = json.dumps({"success": True, "genres": genres})
        self.wfile.write(response.encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.end_headers()
