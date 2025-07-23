from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "emergency backend running", "timestamp": "2025-07-22 20:58:00"})

@app.route('/health')
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/check')
def check():
    return jsonify({"status": "healthy"})

@app.route('/api/initialize')
def initialize():
    return jsonify({"status": "success", "initialized": True})

@app.route('/api/genres')
def genres():
    return jsonify({"success": True, "genres": ["Pop", "Rock", "Jazz", "Classical", "Electronic"]})

@app.route('/api/moods')
def moods():
    return jsonify({"success": True, "moods": ["Happy", "Calm", "Energetic", "Sad", "Relaxing"]})

@app.route('/api/quota')
def quota():
    return jsonify({"success": True, "quota": {"limit": 100, "remaining": 100, "used": 0}})

@app.route('/api/generate', methods=['GET', 'POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        "success": True,
        "id": "emergency_track_123",
        "audioUrl": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "message": "Emergency backend - Generated successfully!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
