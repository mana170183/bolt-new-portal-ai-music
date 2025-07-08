from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import traceback
from dotenv import load_dotenv
import numpy as np
import wave
import tempfile
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS properly
CORS(app, origins=[
    'http://localhost:3000', 
    'http://127.0.0.1:3000', 
    'https://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://localhost:3002',
    'http://127.0.0.1:3002',
    'http://localhost:5173',  # Vite dev server default
    'http://127.0.0.1:5173'
])

# Add error handling for startup
@app.errorhandler(500)
def internal_error(error):
    print(f"Internal server error: {str(error)}", file=sys.stderr)
    traceback.print_exc()
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

@app.before_request
def log_request_info():
    print(f"Request: {request.method} {request.url}", file=sys.stderr)
    try:
        if request.is_json and request.content_length and request.content_length > 0:
            print(f"Request data: {request.get_json()}", file=sys.stderr)
    except Exception as e:
        print(f"Error parsing request JSON: {e}", file=sys.stderr)

@app.route('/health', methods=['GET'])
def health_check():
    print("Health check requested", file=sys.stderr)
    return jsonify({
        "status": "healthy", 
        "message": "Backend is running",
        "success": True,
        "port": os.environ.get('PORT', 5000)
    })

@app.route('/api/auth/token', methods=['POST'])
def auth_token():
    try:
        print("Auth token request received", file=sys.stderr)
        # Get request data safely
        data = request.get_json() or {}
        print(f"Auth request data: {data}", file=sys.stderr)
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
        print(f"Auth response: {response}", file=sys.stderr)
        return jsonify(response)
    except Exception as e:
        print(f"Auth token error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/quota', methods=['GET'])
def user_quota():
    try:
        print("User quota request received", file=sys.stderr)
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
        print(f"Quota response: {response}", file=sys.stderr)
        return jsonify(response)
    except Exception as e:
        print(f"User quota error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/genres', methods=['GET'])
def get_genres():
    try:
        print("Genres request received", file=sys.stderr)
        # Enhanced music genres inspired by Beatoven.ai
        genres = [
            {"id": "cinematic", "name": "Cinematic", "description": "Epic orchestral and dramatic music"},
            {"id": "corporate", "name": "Corporate", "description": "Professional business-friendly music"},
            {"id": "ambient", "name": "Ambient", "description": "Atmospheric and background music"},
            {"id": "electronic", "name": "Electronic", "description": "Modern digital and synthesized sounds"},
            {"id": "pop", "name": "Pop", "description": "Catchy mainstream music"},
            {"id": "rock", "name": "Rock", "description": "Guitar-driven energetic music"},
            {"id": "jazz", "name": "Jazz", "description": "Smooth and sophisticated jazz"},
            {"id": "classical", "name": "Classical", "description": "Traditional orchestral music"},
            {"id": "hip-hop", "name": "Hip Hop", "description": "Urban beats and rhythms"},
            {"id": "folk", "name": "Folk", "description": "Acoustic and traditional music"},
            {"id": "indie", "name": "Indie", "description": "Independent alternative music"},
            {"id": "world", "name": "World", "description": "International and ethnic music"}
        ]
        
        response = {
            "success": True,
            "status": "success",
            "genres": genres
        }
        print(f"Genres response: {len(genres)} genres", file=sys.stderr)
        return jsonify(response)
    except Exception as e:
        print(f"Genres error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/moods', methods=['GET'])
def get_moods():
    try:
        print("Moods request received", file=sys.stderr)
        # Enhanced music moods inspired by Beatoven.ai
        moods = [
            {"id": "uplifting", "name": "Uplifting", "description": "Positive and inspiring energy"},
            {"id": "calm", "name": "Calm", "description": "Peaceful and relaxing"},
            {"id": "energetic", "name": "Energetic", "description": "High energy and motivating"},
            {"id": "dramatic", "name": "Dramatic", "description": "Intense and emotional"},
            {"id": "mysterious", "name": "Mysterious", "description": "Dark and intriguing"},
            {"id": "romantic", "name": "Romantic", "description": "Love and tender emotions"},
            {"id": "melancholic", "name": "Melancholic", "description": "Sad and reflective"},
            {"id": "triumphant", "name": "Triumphant", "description": "Victory and achievement"},
            {"id": "playful", "name": "Playful", "description": "Fun and lighthearted"},
            {"id": "suspenseful", "name": "Suspenseful", "description": "Tension and anticipation"},
            {"id": "nostalgic", "name": "Nostalgic", "description": "Reminiscent and wistful"},
            {"id": "meditative", "name": "Meditative", "description": "Contemplative and zen"}
        ]
        
        response = {
            "success": True,
            "status": "success",
            "moods": moods
        }
        print(f"Moods response: {len(moods)} moods", file=sys.stderr)
        return jsonify(response)
    except Exception as e:
        print(f"Moods error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-music', methods=['POST'])
def generate_music():
    try:
        print("Generate music request received", file=sys.stderr)
        data = request.get_json()
        if not data:
            print("No data provided in request", file=sys.stderr)
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
            
        prompt = data.get('prompt', '')
        duration = data.get('duration', 30)
        genre = data.get('genre', 'pop')
        mood = data.get('mood', 'upbeat')
        
        print(f"Generate music params: prompt='{prompt}', duration={duration}, genre={genre}, mood={mood}", file=sys.stderr)
        
        if not prompt.strip():
            print("Empty prompt provided", file=sys.stderr)
            return jsonify({
                "success": False,
                "error": "Prompt is required"
            }), 400
        
        # Placeholder for music generation logic
        # In a real implementation, this would integrate with AI music generation services
        
        # Generate realistic track data with working audio URLs
        import random
        import time
        
        # Simulate processing time
        time.sleep(2)  # 2 seconds to simulate generation
        
        # Generate track ID and title
        track_id = f"track_{int(time.time())}_{random.randint(1000, 9999)}"
        title_templates = [
            f"{genre.title()} {mood.title()} Track",
            f"{mood.title()} {genre.title()} Composition",
            f"AI Generated {genre.title()}",
            f"{prompt[:20]}..." if len(prompt) > 20 else prompt
        ]
        selected_title = random.choice(title_templates)
        
        # Generate audio file
        def generate_audio_file(frequency=440, duration_seconds=3, sample_rate=22050):
            """Generate a WAV audio file with sine wave audio"""
            # Generate sine wave samples
            num_samples = int(duration_seconds * sample_rate)
            t = np.linspace(0, duration_seconds, num_samples, False)
            
            # Create a more complex waveform for better sound
            # Primary frequency
            wave1 = 0.3 * np.sin(2 * np.pi * frequency * t)
            # Harmonic (octave)
            wave2 = 0.15 * np.sin(2 * np.pi * frequency * 2 * t)
            # Fifth harmonic
            wave3 = 0.1 * np.sin(2 * np.pi * frequency * 3 * t)
            
            # Combine waves
            audio_data = wave1 + wave2 + wave3
            
            # Apply fade in/out to prevent clicks
            fade_length = int(0.1 * sample_rate)  # 0.1 second fade
            fade_in = np.linspace(0, 1, fade_length)
            fade_out = np.linspace(1, 0, fade_length)
            
            audio_data[:fade_length] *= fade_in
            audio_data[-fade_length:] *= fade_out
            
            # Convert to 16-bit integers
            audio_data = np.int16(audio_data * 32767)
            
            # Create unique filename
            filename = f"{track_id}.wav"
            filepath = os.path.join('generated_audio', filename)
            
            # Write WAV file
            with wave.open(filepath, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            return filepath, filename
        
        # Generate different audio for each genre/mood combination
        genre_frequencies = {
            "cinematic": 220,  # Lower, dramatic
            "corporate": 440,  # Standard A4
            "ambient": 330,    # Soft, mid-range
            "electronic": 880, # Higher, digital
            "pop": 523,        # C5, catchy
            "rock": 659,       # E5, energetic
            "jazz": 370,       # F#4, smooth
            "classical": 494,  # B4, elegant
            "hip-hop": 277,    # C#4, urban
            "folk": 392,       # G4, acoustic
            "indie": 466,      # A#4, alternative
            "world": 349       # F4, diverse
        }
        
        # Mood affects duration and volume
        mood_duration = {
            "dramatic": 4,
            "energetic": 3,
            "calm": 5,
            "uplifting": 3,
            "mysterious": 4,
            "romantic": 5,
            "melancholic": 4,
            "triumphant": 3,
            "playful": 2,
            "suspenseful": 4,
            "nostalgic": 5,
            "meditative": 6
        }
        
        # Select frequency and duration based on genre and mood
        frequency = genre_frequencies.get(genre.lower(), 440)
        audio_duration = mood_duration.get(mood.lower(), 3)
        
        # Generate the audio file
        filepath, filename = generate_audio_file(frequency, audio_duration)
        
        # Create URLs for the frontend
        audio_url = f"/api/audio/{filename}"
        
        response = {
            "success": True,
            "status": "success",
            "track": {
                "id": track_id,
                "title": selected_title,
                "duration": duration,
                "genre": genre,
                "mood": mood,
                "url": audio_url,
                "download_url": audio_url,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "waveform_data": [random.randint(10, 50) for _ in range(50)]  # Mock waveform data
            }
        }
        print(f"Generate music response: {response}", file=sys.stderr)
        return jsonify(response)
    
    except Exception as e:
        print(f"Generate music error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    try:
        print(f"Serving audio file: {filename}", file=sys.stderr)
        filepath = os.path.join('generated_audio', filename)
        
        if not os.path.exists(filepath):
            print(f"Audio file not found: {filepath}", file=sys.stderr)
            return jsonify({
                "success": False,
                "error": "Audio file not found"
            }), 404
        
        return send_file(
            filepath,
            mimetype='audio/wav',
            as_attachment=False,
            download_name=filename
        )
    except Exception as e:
        print(f"Serve audio error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        print(f"🚀 Starting Flask server on port {port}...", file=sys.stderr)
        print(f"📍 Health check available at: http://localhost:{port}/health", file=sys.stderr)
        print(f"📡 API endpoints available at: http://localhost:{port}/api/", file=sys.stderr)
        print(f"🔧 CORS enabled for: http://localhost:3000, http://127.0.0.1:3000", file=sys.stderr)
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)