from flask import Flask, jsonify, request, make_response, Response
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

# CORS helper
def cors_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Global CORS
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return cors_response({})

# Health endpoints
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return generate()
    return cors_response({"status": "ok", "message": "Portal AI Music Backend", "version": "2.1"})

@app.route('/health')
@app.route('/api/health')
def health():
    return cors_response({"status": "healthy"})

@app.route('/api/check')
def check():
    return cors_response({"status": "healthy"})

@app.route('/api/initialize')
def initialize():
    return cors_response({"status": "success", "initialized": True})

@app.route('/api/genres')
def genres():
    return cors_response({
        "success": True,
        "genres": ["Pop", "Rock", "Jazz", "Classical", "Electronic", "Hip Hop", "Country", "Blues"]
    })

@app.route('/api/moods')
def moods():
    return cors_response({
        "success": True,
        "moods": ["Happy", "Calm", "Energetic", "Sad", "Mysterious", "Upbeat", "Relaxing", "Intense"]
    })

@app.route('/api/quota')
@app.route('/api/user/quota')
def quota():
    return cors_response({
        "success": True,
        "quota": {"limit": 100, "remaining": 95, "used": 5}
    })

# AUDIO PROXY ENDPOINT
@app.route('/api/audio/proxy')
def audio_proxy():
    """Proxy audio files to avoid CORS issues"""
    url = request.args.get('url')
    if not url:
        return cors_response({"error": "No URL provided"}, 400)
    
    try:
        # Fetch the audio file
        audio_response = requests.get(url, stream=True, timeout=10)
        audio_response.raise_for_status()
        
        # Stream the audio back
        def generate():
            for chunk in audio_response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        
        response = Response(generate(), mimetype='audio/mpeg')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Content-Type'] = 'audio/mpeg'
        response.headers['Accept-Ranges'] = 'bytes'
        return response
        
    except Exception as e:
        return cors_response({"error": str(e)}, 500)

# UPDATED GENERATE ENDPOINT
@app.route('/generate', methods=['POST'])
@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json() if request.is_json else {}
        
        prompt = data.get('prompt', 'AI music')
        genre = data.get('genre', 'Pop')
        mood = data.get('mood', 'Happy')
        duration = data.get('duration', 30)
        
        # Music samples
        samples = {
            ("Pop", "Happy"): "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            ("Rock", "Energetic"): "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            ("Jazz", "Relaxing"): "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            ("Classical", "Calm"): "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
            ("Electronic", "Upbeat"): "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3"
        }
        
        # Get the external audio URL
        external_url = samples.get((genre, mood), samples[("Pop", "Happy")])
        
        # Create proxied URL with HTTPS for Azure Container Apps
        host = request.headers.get('host', request.host)
        proxied_url = f"https://{host}/api/audio/proxy?url={external_url}"
        
        result = {
            "success": True,
            "id": f"track_{int(datetime.now().timestamp() * 1000)}",
            "audioUrl": proxied_url,  # Use proxied URL
            "url": proxied_url,
            "download_url": external_url,  # Original for download
            "message": "Music generated successfully!",
            "title": f"{genre} {mood} - AI Generated",
            "duration": duration,
            "metadata": {
                "prompt": prompt,
                "genre": genre,
                "mood": mood,
                "duration": duration
            }
        }
        
        return cors_response(result)
        
    except Exception as e:
        return cors_response({"success": False, "error": str(e)}, 500)

# Other endpoints...
@app.route('/api/instruments')
def instruments():
    return cors_response({"success": True, "instruments": ["Piano", "Guitar", "Drums", "Bass", "Violin", "Saxophone", "Synthesizer", "Flute"]})

@app.route('/api/templates')
def templates():
    return cors_response({
        "success": True,
        "templates": [
            {"id": "1", "name": "Pop Template", "genre": "Pop"},
            {"id": "2", "name": "Rock Template", "genre": "Rock"}
        ]
    })

# Catch all 404s
@app.errorhandler(404)
def not_found(e):
    # If it's a POST to any unknown path, assume it's meant for generate
    if request.method == 'POST':
        return generate()
    return cors_response({"error": "Not found", "path": request.path}, 404)

# Handle 405 Method Not Allowed
@app.errorhandler(405)
def method_not_allowed(e):
    # If it's a POST, redirect to generate
    if request.method == 'POST':
        return generate()
    return cors_response({"error": "Method not allowed"}, 405)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
