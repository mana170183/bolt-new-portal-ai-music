from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS properly
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# Add error handling for startup
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "Backend is running",
        "success": True
    })

@app.route('/api/auth/token', methods=['POST'])
def auth_token():
    try:
        # Get request data safely
        data = request.get_json() or {}
        user_id = data.get('user_id', 'demo_user')
        plan = data.get('plan', 'free')
        
        # Placeholder authentication - return a mock token
        return jsonify({
            "success": True,
            "token": "mock-jwt-token-12345",
            "user": {
                "id": user_id,
                "email": "user@example.com",
                "plan": plan
            }
        })
    except Exception as e:
        print(f"Auth token error: {str(e)}", file=sys.stderr)
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
                "plan": "free",
                "daily_limit": 10,
                "remaining_today": 5,
                "used_today": 5,
                "reset_date": "2024-02-01T00:00:00Z"
            }
        })
    except Exception as e:
        print(f"User quota error: {str(e)}", file=sys.stderr)
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
        print(f"Genres error: {str(e)}", file=sys.stderr)
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
        print(f"Moods error: {str(e)}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
            
        prompt = data.get('prompt', '')
        duration = data.get('duration', 30)
        genre = data.get('genre', 'pop')
        mood = data.get('mood', 'upbeat')
        
        if not prompt.strip():
            return jsonify({
                "success": False,
                "error": "Prompt is required"
            }), 400
        
        # Placeholder for music generation logic
        # In a real implementation, this would integrate with AI music generation services
        
        return jsonify({
            "success": True,
            "status": "success",
            "track": {
                "id": "track_12345",
                "title": f"AI Generated {genre.title()} Track",
                "duration": duration,
                "genre": genre,
                "mood": mood,
                "url": "https://example.com/generated-music.mp3",
                "download_url": "https://example.com/generated-music.wav",
                "created_at": "2024-01-01T00:00:00Z"
            }
        })
    
    except Exception as e:
        print(f"Generate music error: {str(e)}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        print(f"Starting Flask server on port {port}...")
        print(f"Health check available at: http://localhost:{port}/health")
        print(f"API endpoints available at: http://localhost:{port}/api/")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Failed to start server: {str(e)}", file=sys.stderr)
        sys.exit(1)