from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)

# Ultra-aggressive CORS configuration
CORS(app, 
     origins="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["*"],
     supports_credentials=True,
     resources={r"/*": {"origins": "*"}})

# Sample music catalog
MUSIC_CATALOG = [
    {"track_id": "1", "genre": "Pop", "mood": "Happy", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"},
    {"track_id": "2", "genre": "Rock", "mood": "Energetic", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"},
    {"track_id": "3", "genre": "Classical", "mood": "Calm", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"},
    {"track_id": "4", "genre": "Electronic", "mood": "Energetic", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"},
    {"track_id": "5", "genre": "Jazz", "mood": "Relaxing", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3"}
]

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        return response

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

@app.route('/')
def home():
    return jsonify({"message": "Portal AI Music Backend - Ultra CORS", "status": "running"})

@app.route('/health')
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/check')
def check():
    return jsonify({"status": "healthy"})

@app.route('/api/genres')
def genres():
    return jsonify({
        "success": True,
        "genres": ["Pop", "Rock", "Jazz", "Classical", "Electronic", "Hip Hop", "Country", "Blues"]
    })

@app.route('/api/moods')
def moods():
    return jsonify({
        "success": True,
        "moods": ["Happy", "Calm", "Energetic", "Sad", "Mysterious", "Upbeat", "Relaxing", "Intense"]
    })

@app.route('/api/quota')
@app.route('/api/user/quota')
def quota():
    return jsonify({
        "success": True,
        "quota": {"limit": 100, "remaining": 100, "used": 0}
    })

@app.route('/api/templates')
def templates():
    return jsonify({"success": True, "templates": []})

@app.route('/api/presets')
def presets():
    return jsonify({"success": True, "presets": []})

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Get request data
        data = request.get_json() if request.is_json else {}
        
        prompt = data.get('prompt', 'AI generated music')
        genre = data.get('genre', 'Pop')
        mood = data.get('mood', 'Happy')
        duration = data.get('duration', 30)
        
        # Find matching track
        selected = MUSIC_CATALOG[0]
        for track in MUSIC_CATALOG:
            if track.get('genre') == genre or track.get('mood') == mood:
                selected = track
                break
        
        # Generate response
        result = {
            "success": True,
            "id": f"track_{int(datetime.now().timestamp() * 1000)}",
            "audioUrl": selected['url'],
            "url": selected['url'],
            "message": "Music generated successfully!",
            "metadata": {
                "prompt": prompt,
                "genre": genre,
                "mood": mood,
                "duration": duration
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
