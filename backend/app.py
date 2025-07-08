from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import traceback
from dotenv import load_dotenv
import logging
import base64
import io
import numpy as np
from scipy.io.wavfile import write
import json
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Create output directory for generated audio
AUDIO_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'generated_audio')
if not os.path.exists(AUDIO_OUTPUT_DIR):
    os.makedirs(AUDIO_OUTPUT_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log')
    ]
)
logger = logging.getLogger(__name__)

def generate_simple_audio(duration=30, genre='pop', mood='upbeat'):
    """
    Generate simple audio based on parameters
    This is a basic implementation - in production, you'd use advanced AI models
    """
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create base frequencies based on genre
    genre_freqs = {
        'pop': [261.63, 329.63, 392.00, 523.25],  # C4, E4, G4, C5
        'rock': [196.00, 246.94, 293.66, 392.00],  # G3, B3, D4, G4
        'jazz': [220.00, 277.18, 329.63, 440.00],  # A3, C#4, E4, A4
        'classical': [261.63, 293.66, 329.63, 392.00],  # C4, D4, E4, G4
        'electronic': [130.81, 196.00, 261.63, 392.00],  # C3, G3, C4, G4
        'hip-hop': [82.41, 110.00, 146.83, 196.00],  # E2, A2, D3, G3
        'country': [196.00, 246.94, 293.66, 349.23],  # G3, B3, D4, F4
        'blues': [146.83, 174.61, 220.00, 261.63]  # D3, F3, A3, C4
    }
    
    # Create rhythm patterns based on mood
    mood_patterns = {
        'happy': {'tempo': 1.2, 'amplitude': 0.7, 'attack': 0.1},
        'sad': {'tempo': 0.6, 'amplitude': 0.4, 'attack': 0.3},
        'energetic': {'tempo': 1.5, 'amplitude': 0.8, 'attack': 0.05},
        'calm': {'tempo': 0.8, 'amplitude': 0.3, 'attack': 0.4},
        'romantic': {'tempo': 0.7, 'amplitude': 0.5, 'attack': 0.2},
        'mysterious': {'tempo': 0.9, 'amplitude': 0.6, 'attack': 0.25},
        'epic': {'tempo': 1.1, 'amplitude': 0.9, 'attack': 0.1},
        'nostalgic': {'tempo': 0.75, 'amplitude': 0.45, 'attack': 0.35}
    }
    
    freqs = genre_freqs.get(genre, genre_freqs['pop'])
    pattern = mood_patterns.get(mood, mood_patterns['happy'])
    
    # Generate audio waves
    audio = np.zeros_like(t)
    
    for i, freq in enumerate(freqs):
        # Create basic waveform with some harmonics
        wave = np.sin(2 * np.pi * freq * t * pattern['tempo'])
        wave += 0.3 * np.sin(2 * np.pi * freq * 2 * t * pattern['tempo'])  # Octave harmonic
        wave += 0.1 * np.sin(2 * np.pi * freq * 3 * t * pattern['tempo'])  # Fifth harmonic
        
        # Apply envelope (attack-decay-sustain-release)
        envelope = np.ones_like(t)
        attack_samples = int(pattern['attack'] * sample_rate)
        decay_samples = int(0.1 * sample_rate)
        release_samples = int(0.2 * sample_rate)
        
        # Attack phase
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase
        if decay_samples > 0 and attack_samples + decay_samples < len(envelope):
            envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, 0.7, decay_samples)
        
        # Release phase
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(envelope[-release_samples], 0, release_samples)
        
        # Apply rhythm pattern
        beat_length = int(sample_rate * 0.5 / pattern['tempo'])  # Half second beats adjusted by tempo
        for beat in range(0, len(t), beat_length):
            if beat + beat_length < len(envelope):
                if (beat // beat_length) % 4 == 0:  # Emphasis on every 4th beat
                    envelope[beat:beat + beat_length] *= 1.2
                elif (beat // beat_length) % 2 == 1:  # Softer on off-beats
                    envelope[beat:beat + beat_length] *= 0.7
        
        wave *= envelope * pattern['amplitude'] / len(freqs)
        audio += wave
    
    # Add some noise for texture (very subtle)
    noise = np.random.normal(0, 0.01, len(audio))
    audio += noise
    
    # Normalize to prevent clipping
    audio = np.clip(audio, -1, 1)
    
    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)
    
    return audio_int16, sample_rate

app = Flask(__name__)

# Configure CORS properly
CORS(app, origins=[
    'http://localhost:3000', 
    'http://127.0.0.1:3000', 
    'https://localhost:3000',
    'http://localhost:5173',  # Vite dev server default
    'http://127.0.0.1:5173'
])

# Add error handling for startup
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    traceback.print_exc()
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url}")
    if request.is_json:
        logger.info(f"Request data: {request.get_json()}")

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check requested")
    try:
        response = {
        "status": "healthy", 
        "message": "Backend is running",
        "success": True,
            "port": int(os.environ.get('PORT', 5000)),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        logger.info(f"Health check response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/auth/token', methods=['POST'])
def auth_token():
    try:
        logger.info("Auth token request received")
        # Get request data safely
        data = request.get_json() or {}
        logger.info(f"Auth request data: {data}")
        user_id = data.get('user_id', 'demo_user')
        plan = data.get('plan', 'free')
        
        # Placeholder authentication - return a mock token
        response = {
            "success": True,
            "token": "mock-jwt-token-12345",
            "user": {
                "id": user_id,
                "email": "user@example.com",
                "plan": plan
            }
        }
        logger.info(f"Auth response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Auth token error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/quota', methods=['GET'])
def user_quota():
    try:
        logger.info("User quota request received")
        # Placeholder quota information
        response = {
            "success": True,
            "quota": {
                "plan": "free",
                "daily_limit": 10,
                "remaining_today": 5,
                "used_today": 5,
                "reset_date": "2024-02-01T00:00:00Z"
            }
        }
        logger.info(f"Quota response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"User quota error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/genres', methods=['GET'])
def get_genres():
    try:
        logger.info("Genres request received")
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
        
        response = {
            "success": True,
            "genres": genres
        }
        logger.info(f"Genres response: {len(genres)} genres")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Genres error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/moods', methods=['GET'])
def get_moods():
    try:
        logger.info("Moods request received")
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
        
        response = {
            "success": True,
            "moods": moods
        }
        logger.info(f"Moods response: {len(moods)} moods")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Moods error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-music', methods=['POST'])
def generate_music():
    try:
        logger.info("Generate music request received")
        data = request.get_json()
        if not data:
            logger.warning("No data provided in request")
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
            
        prompt = data.get('prompt', '')
        duration = data.get('duration', 30)
        genre = data.get('genre', 'pop')
        mood = data.get('mood', 'upbeat')
        
        logger.info(f"Generate music params: prompt='{prompt}', duration={duration}, genre={genre}, mood={mood}")
        
        if not prompt.strip():
            logger.warning("Empty prompt provided")
            return jsonify({
                "success": False,
                "error": "Prompt is required"
            }), 400
        
        # Generate unique ID for this track
        track_id = str(uuid.uuid4())
        
        # Generate audio
        logger.info("Generating audio...")
        audio_data, sample_rate = generate_simple_audio(duration, genre, mood)
        
        # Save audio file
        filename = f"track_{track_id}.wav"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        write(filepath, sample_rate, audio_data)
        logger.info(f"Audio file saved: {filepath}")
        
        # Convert audio to base64 for inline streaming
        buffer = io.BytesIO()
        write(buffer, sample_rate, audio_data)
        buffer.seek(0)
        audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        response = {
            "success": True,
            "status": "success",
            "track": {
                "id": track_id,
                "title": f"AI Generated {genre.title()} - {mood.title()}",
                "duration": duration,
                "genre": genre,
                "mood": mood,
                "url": f"data:audio/wav;base64,{audio_base64}",
                "download_url": f"/api/download/{track_id}",
                "created_at": datetime.now().isoformat()
            }
        }
        logger.info(f"Generate music response: track generated successfully")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Generate music error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/download/<track_id>', methods=['GET'])
def download_track(track_id):
    try:
        filename = f"track_{track_id}.wav"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                "success": False,
                "error": "Track not found"
            }), 404
            
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"AI_Music_{track_id}.wav",
            mimetype="audio/wav"
        )
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"🚀 Starting Flask server on port {port}...")
        logger.info(f"📍 Health check available at: http://localhost:{port}/health")
        logger.info(f"📡 API endpoints available at: http://localhost:{port}/api/")
        logger.info(f"🔧 CORS enabled for multiple origins including localhost:3000 and localhost:5173")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        traceback.print_exc()
        sys.exit(1)