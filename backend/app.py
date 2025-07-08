from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# In production, these would come from environment variables
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING', 'your_azure_connection_string')
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'music-files')

# Mock data for demonstration
SAMPLE_TRACKS = [
    {
        'id': 'track_001',
        'title': 'Upbeat Pop Energy',
        'duration': 30,
        'genre': 'pop',
        'mood': 'upbeat',
        'url': 'https://example.com/sample1.mp3',
        'download_url': 'https://example.com/download/sample1.wav'
    },
    {
        'id': 'track_002', 
        'title': 'Calm Ambient Waves',
        'duration': 60,
        'genre': 'ambient',
        'mood': 'calm',
        'url': 'https://example.com/sample2.mp3',
        'download_url': 'https://example.com/download/sample2.wav'
    }
]

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Portal AI Music API'
    })

@app.route('/api/generate-music', methods=['POST'])
def generate_music():
    """Generate music based on text prompt and parameters"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        
        # Extract parameters with defaults
        prompt = data.get('prompt', '').strip()
        duration = data.get('duration', 30)
        genre = data.get('genre', 'pop')
        mood = data.get('mood', 'upbeat')
        
        # Validate inputs
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if not isinstance(duration, int) or duration < 10 or duration > 300:
            return jsonify({'error': 'Duration must be between 10 and 300 seconds'}), 400
        
        logger.info(f"Generating music: prompt='{prompt}', duration={duration}, genre={genre}, mood={mood}")
        
        # In a real implementation, this would:
        # 1. Use a model like MusicGen to generate audio
        # 2. Save the audio to Azure Blob Storage
        # 3. Return the actual download URL
        
        # For demo purposes, return mock data
        track_id = str(uuid.uuid4())
        track_title = f"{mood.title()} {genre.title()} Track"
        
        # Simulate processing time
        import time
        time.sleep(2)  # Remove this in production
        
        response_data = {
            'status': 'success',
            'track': {
                'id': track_id,
                'title': track_title,
                'duration': duration,
                'genre': genre,
                'mood': mood,
                'prompt': prompt,
                'url': f'https://example.com/tracks/{track_id}.mp3',
                'download_url': f'https://example.com/download/{track_id}.wav',
                'created_at': datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Successfully generated track: {track_id}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating music: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate music. Please try again.'
        }), 500

@app.route('/api/tracks', methods=['GET'])
def get_sample_tracks():
    """Get sample tracks for demonstration"""
    try:
        return jsonify({
            'status': 'success',
            'tracks': SAMPLE_TRACKS
        })
    except Exception as e:
        logger.error(f"Error fetching tracks: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch tracks'
        }), 500

@app.route('/api/genres', methods=['GET'])
def get_genres():
    """Get available music genres"""
    genres = [
        'pop', 'rock', 'electronic', 'classical', 'jazz', 'hip-hop',
        'country', 'folk', 'ambient', 'cinematic', 'blues', 'reggae'
    ]
    return jsonify({
        'status': 'success',
        'genres': genres
    })

@app.route('/api/moods', methods=['GET'])
def get_moods():
    """Get available music moods"""
    moods = [
        'upbeat', 'calm', 'energetic', 'melancholic', 'mysterious',
        'romantic', 'epic', 'peaceful', 'dramatic', 'playful'
    ]
    return jsonify({
        'status': 'success',
        'moods': moods
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Portal AI Music API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)