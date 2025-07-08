from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"})

@app.route('/api/auth/token', methods=['POST'])
def auth_token():
    try:
        # Placeholder authentication - return a mock token
        return jsonify({
            "success": True,
            "token": "mock-jwt-token-12345",
            "user": {
                "id": "user123",
                "email": "user@example.com",
                "plan": "free"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/quota', methods=['GET'])
def user_quota():
    try:
        # Placeholder quota information
        return jsonify({
            "success": True,
            "quota": {
                "used": 5,
                "limit": 10,
                "remaining": 5,
                "reset_date": "2024-02-01T00:00:00Z"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/genres', methods=['GET'])
def get_genres():
    try:
        # Placeholder music genres
        genres = [
            {"id": "pop", "name": "Pop", "description": "Popular music"},
            {"id": "rock", "name": "Rock", "description": "Rock music"},
            {"id": "jazz", "name": "Jazz", "description": "Jazz music"},
            {"id": "classical", "name": "Classical", "description": "Classical music"},
            {"id": "electronic", "name": "Electronic", "description": "Electronic music"},
            {"id": "hip-hop", "name": "Hip Hop", "description": "Hip hop music"},
            {"id": "country", "name": "Country", "description": "Country music"},
            {"id": "blues", "name": "Blues", "description": "Blues music"}
        ]
        
        return jsonify({
            "success": True,
            "genres": genres
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/moods', methods=['GET'])
def get_moods():
    try:
        # Placeholder music moods
        moods = [
            {"id": "happy", "name": "Happy", "description": "Upbeat and joyful"},
            {"id": "sad", "name": "Sad", "description": "Melancholic and emotional"},
            {"id": "energetic", "name": "Energetic", "description": "High energy and motivating"},
            {"id": "calm", "name": "Calm", "description": "Peaceful and relaxing"},
            {"id": "romantic", "name": "Romantic", "description": "Love and romance"},
            {"id": "mysterious", "name": "Mysterious", "description": "Dark and intriguing"},
            {"id": "epic", "name": "Epic", "description": "Grand and cinematic"},
            {"id": "nostalgic", "name": "Nostalgic", "description": "Reminiscent and wistful"}
        ]
        
        return jsonify({
            "success": True,
            "moods": moods
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        # Placeholder for music generation logic
        # In a real implementation, this would integrate with AI music generation services
        
        return jsonify({
            "success": True,
            "message": "Music generation request received",
            "prompt": prompt,
            "audio_url": "https://example.com/generated-music.mp3",
            "generation_id": "gen_12345",
            "status": "completed"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)