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

@app.route('/generate-music', methods=['POST'])
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
            "audio_url": "https://example.com/generated-music.mp3"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)