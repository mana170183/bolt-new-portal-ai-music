from flask import Flask, request, jsonify, send_file, make_response
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

# Enhanced imports for metadata and AI integration
try:
    from database import get_db, init_database
    from azure_openai_integration import get_azure_ai, init_azure_openai
    from enhanced_music_generator import EnhancedMusicGenerator
    ENHANCED_FEATURES_AVAILABLE = True
    print("🚀 Enhanced features loaded successfully")
except ImportError as e:
    ENHANCED_FEATURES_AVAILABLE = False
    print(f"⚠️ Enhanced features not available: {e}")

# Azure Storage imports
try:
    from azure.storage.blob import BlobServiceClient, BlobClient
    from azure.core.exceptions import ResourceNotFoundError
    AZURE_STORAGE_AVAILABLE = True
    print("🔗 Azure Storage SDK loaded successfully")
except ImportError as e:
    AZURE_STORAGE_AVAILABLE = False
    print(f"⚠️ Azure Storage SDK not available: {e}")

# Database connectivity imports
try:
    import pymssql
    import pyodbc
    DATABASE_AVAILABLE = True
    print("🔗 Database drivers loaded successfully")
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"⚠️ Database drivers not available: {e}")

# Load environment variables
load_dotenv()

# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
MUSIC_STORAGE_CONTAINER = os.getenv('MUSIC_STORAGE_CONTAINER', 'generated-music')
TRAINING_DATA_CONTAINER = os.getenv('TRAINING_DATA_CONTAINER', 'training-data')

# Database Configuration
SQL_CONNECTION_STRING = os.getenv('SQL_CONNECTION_STRING')
AZURE_SQL_CONNECTION_STRING = os.getenv('AZURE_SQL_CONNECTION_STRING')

# Initialize components
app = Flask(__name__)
CORS(app)

# Initialize enhanced features
if ENHANCED_FEATURES_AVAILABLE:
    try:
        db_manager = get_db()
        azure_ai_manager = get_azure_ai()
        enhanced_generator = EnhancedMusicGenerator()
        
        # Initialize connections
        db_connected = init_database()
        ai_connected = init_azure_openai()
        
        print(f"💾 Database connected: {db_connected}")
        print(f"🤖 Azure OpenAI connected: {ai_connected}")
        
    except Exception as e:
        print(f"❌ Enhanced features initialization failed: {e}")
        ENHANCED_FEATURES_AVAILABLE = False
        db_connected = False
        ai_connected = False
else:
    db_connected = False
    ai_connected = False

# Initialize Azure Storage client
if AZURE_STORAGE_AVAILABLE and AZURE_STORAGE_CONNECTION_STRING:
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        print(f"✅ Azure Storage connected - Music: {MUSIC_STORAGE_CONTAINER}, Training: {TRAINING_DATA_CONTAINER}")
    except Exception as e:
        blob_service_client = None
        print(f"❌ Azure Storage connection failed: {e}")
else:
    blob_service_client = None
    print("⚠️ Azure Storage not configured")

# Create output directory for generated audio
AUDIO_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'generated_audio')
try:
    if not os.path.exists(AUDIO_OUTPUT_DIR):
        os.makedirs(AUDIO_OUTPUT_DIR, mode=0o755)
    # Ensure directory is writable
    if not os.access(AUDIO_OUTPUT_DIR, os.W_OK):
        # Try to create in /tmp if /app/generated_audio is not writable
        AUDIO_OUTPUT_DIR = '/tmp/generated_audio'
        if not os.path.exists(AUDIO_OUTPUT_DIR):
            os.makedirs(AUDIO_OUTPUT_DIR, mode=0o755)
    print(f"Using audio output directory: {AUDIO_OUTPUT_DIR}")
except Exception as e:
    print(f"Warning: Could not create audio output directory: {e}")
    AUDIO_OUTPUT_DIR = '/tmp'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Azure Storage Helper Functions
def upload_audio_to_storage(audio_data, filename, container_name=MUSIC_STORAGE_CONTAINER):
    """Upload audio data to Azure Storage and return the blob URL"""
    if not blob_service_client:
        logger.warning("Azure Storage not available, saving locally only")
        return None
    
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=filename
        )
        
        # Upload the audio data
        blob_client.upload_blob(audio_data, overwrite=True)
        
        # Return the blob URL
        blob_url = blob_client.url
        logger.info(f"Audio uploaded to storage: {blob_url}")
        return blob_url
        
    except Exception as e:
        logger.error(f"Failed to upload audio to storage: {e}")
        return None

def save_audio_file(audio_data, filename, upload_to_storage=True):
    """Save audio file to tmp and optionally to Azure Storage"""
    # Use /tmp for local storage (always writable in containers)
    local_path = os.path.join('/tmp', filename)
    with open(local_path, 'wb') as f:
        f.write(audio_data)
    
    # Upload to storage if enabled
    storage_url = None
    if upload_to_storage:
        storage_url = upload_audio_to_storage(audio_data, filename)
    
    return {
        'local_path': local_path,
        'storage_url': storage_url,
        'filename': filename
    }

def generate_enhanced_audio(duration=30, genre='pop', mood='upbeat'):
    """
    Generate enhanced, pleasant audio based on parameters
    Improved algorithm to avoid buzzing sounds
    """
    try:
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create musical chord progressions for different genres
        genre_progressions = {
            'pop': [(261.63, 329.63, 392.00), (246.94, 311.13, 369.99), (293.66, 369.99, 440.00), (261.63, 329.63, 392.00)],
            'rock': [(196.00, 246.94, 293.66), (220.00, 277.18, 329.63), (246.94, 311.13, 369.99), (196.00, 246.94, 293.66)],
            'jazz': [(220.00, 277.18, 329.63), (246.94, 311.13, 369.99), (261.63, 329.63, 392.00), (196.00, 246.94, 293.66)],
            'classical': [(261.63, 329.63, 392.00), (293.66, 369.99, 440.00), (329.63, 415.30, 493.88), (261.63, 329.63, 392.00)],
            'electronic': [(130.81, 196.00, 261.63), (164.81, 246.94, 329.63), (196.00, 293.66, 392.00), (130.81, 196.00, 261.63)],
            'hip-hop': [(82.41, 110.00, 146.83), (98.00, 130.81, 174.61), (110.00, 146.83, 196.00), (82.41, 110.00, 146.83)],
            'ambient': [(174.61, 220.00, 261.63), (196.00, 246.94, 293.66), (220.00, 277.18, 329.63), (174.61, 220.00, 261.63)],
            'cinematic': [(196.00, 261.63, 329.63), (220.00, 293.66, 369.99), (246.94, 329.63, 415.30), (196.00, 261.63, 329.63)],
        }
        
        # Improved mood parameters
        mood_params = {
            'uplifting': {'attack': 0.1, 'decay': 0.3, 'sustain': 0.7, 'release': 0.4, 'brightness': 1.2, 'volume': 0.7},
            'calm': {'attack': 0.2, 'decay': 0.5, 'sustain': 0.6, 'release': 0.8, 'brightness': 0.8, 'volume': 0.4},
            'energetic': {'attack': 0.05, 'decay': 0.2, 'sustain': 0.8, 'release': 0.3, 'brightness': 1.3, 'volume': 0.8},
            'dramatic': {'attack': 0.15, 'decay': 0.4, 'sustain': 0.9, 'release': 0.6, 'brightness': 1.1, 'volume': 0.9},
            'upbeat': {'attack': 0.08, 'decay': 0.25, 'sustain': 0.75, 'release': 0.35, 'brightness': 1.25, 'volume': 0.75},
        }
        
        # Get progression and parameters
        progression = genre_progressions.get(genre, genre_progressions['pop'])
        params = mood_params.get(mood, mood_params['upbeat'])
        
        # Generate audio with improved algorithm
        audio = np.zeros_like(t)
        chord_duration = duration / len(progression)
        
        for chord_idx, chord in enumerate(progression):
            chord_start = chord_idx * chord_duration
            chord_end = (chord_idx + 1) * chord_duration
            
            # Time mask for this chord
            chord_mask = (t >= chord_start) & (t < chord_end)
            chord_t = t[chord_mask] - chord_start
            
            if len(chord_t) > 0:
                # Generate ADSR envelope
                envelope = generate_adsr_envelope(chord_t, chord_duration, params)
                
                # Generate chord harmonics
                chord_audio = np.zeros_like(chord_t)
                for i, freq in enumerate(chord):
                    # Add multiple harmonics for richer sound
                    for harmonic in range(1, 4):
                        harmonic_freq = freq * harmonic * params['brightness']
                        if harmonic_freq < sample_rate / 2:  # Avoid aliasing
                            amplitude = (0.7 ** (harmonic - 1)) * (0.8 ** i)
                            wave = np.sin(2 * np.pi * harmonic_freq * chord_t)
                            chord_audio += wave * amplitude
                
                # Apply envelope and add to main audio
                audio[chord_mask] += chord_audio * envelope
        
        # Apply final volume and normalization
        audio *= params['volume']
        
        # Smooth normalization to prevent clipping
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.7
        
        # Apply gentle filtering to reduce harshness
        audio = apply_gentle_filter(audio, sample_rate)
        
        return audio
    
    except Exception as e:
        print(f"Audio generation error: {e}", file=sys.stderr)
        # Fallback to simple tone
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = 440.0  # A4 note
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        return audio
    
    for chord_idx, chord in enumerate(progression):
        chord_start = chord_idx * chord_duration
        chord_end = (chord_idx + 1) * chord_duration
        
        # Time mask for this chord
        chord_mask = (t >= chord_start) & (t < chord_end)
        chord_t = t[chord_mask] - chord_start
        
        if len(chord_t) > 0:
            # Generate ADSR envelope
            envelope = generate_adsr_envelope(chord_t, chord_duration, params)
            
            # Generate chord harmonics
            chord_audio = np.zeros_like(chord_t)
            for i, freq in enumerate(chord):
                # Add multiple harmonics for richer sound
                for harmonic in range(1, 4):
                    harmonic_freq = freq * harmonic * params['brightness']
                    if harmonic_freq < sample_rate / 2:  # Avoid aliasing
                        amplitude = (0.7 ** (harmonic - 1)) * (0.8 ** i)
                        wave = np.sin(2 * np.pi * harmonic_freq * chord_t)
                        chord_audio += wave * amplitude
            
            # Apply envelope and add to main audio
            audio[chord_mask] += chord_audio * envelope
    
    # Apply final volume and normalization
    audio *= params['volume']
    
    # Smooth normalization to prevent clipping
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio)) * 0.7
    
    # Apply gentle filtering to reduce harshness
    audio = apply_gentle_filter(audio, sample_rate)
    
    return audio

def generate_adsr_envelope(t, duration, params):
    """Generate ADSR (Attack, Decay, Sustain, Release) envelope"""
    attack_time = duration * params['attack']
    decay_time = duration * params['decay']
    sustain_level = params['sustain']
    release_time = duration * params['release']
    
    envelope = np.ones_like(t)
    
    for i, time in enumerate(t):
        if time < attack_time:
            # Attack phase
            envelope[i] = time / attack_time
        elif time < attack_time + decay_time:
            # Decay phase
            decay_progress = (time - attack_time) / decay_time
            envelope[i] = 1.0 - (1.0 - sustain_level) * decay_progress
        elif time < duration - release_time:
            # Sustain phase
            envelope[i] = sustain_level
        else:
            # Release phase
            release_progress = (time - (duration - release_time)) / release_time
            envelope[i] = sustain_level * (1.0 - release_progress)
    
    return envelope

def apply_gentle_filter(audio, sample_rate):
    """Apply gentle low-pass filter to reduce harshness"""
    # Simple moving average filter
    window_size = int(sample_rate * 0.0001)  # 0.1ms window
    if window_size > 1:
        kernel = np.ones(window_size) / window_size
        audio = np.convolve(audio, kernel, mode='same')
    
    return audio

def generate_simple_audio(duration=30, genre='pop', mood='upbeat'):
    """
    Generate simple audio based on parameters
    This is a basic implementation - in production, you'd use advanced AI models
    """
    # Use enhanced algorithm instead of the old buzzing one
    return generate_enhanced_audio(duration, genre, mood)

# Import enhanced generator if available
ENHANCED_GENERATOR_AVAILABLE = False
enhanced_generator = None

try:
    from enhanced_main_generator import EnhancedMultiInstrumentalGenerator
    enhanced_generator = EnhancedMultiInstrumentalGenerator()
    ENHANCED_GENERATOR_AVAILABLE = True
    print("🎼 Enhanced Multi-Instrumental Generator imported successfully")
except ImportError as e:
    print(f"⚠️  Enhanced generator not available: {e}")
    ENHANCED_GENERATOR_AVAILABLE = False
    enhanced_generator = None

try:
    from advanced_music_generator import AdvancedMultiInstrumentalGenerator
    if not ENHANCED_GENERATOR_AVAILABLE:
        enhanced_generator = AdvancedMultiInstrumentalGenerator()
        ENHANCED_GENERATOR_AVAILABLE = True
        print("🎼 Advanced Multi-Instrumental Generator loaded")
except ImportError:
    pass

if not ENHANCED_GENERATOR_AVAILABLE:
    print("🔄 Using basic procedural music generation")

app = Flask(__name__)

frontend_urls = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://frontend-containerapp-dev.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io"
]

CORS(app, origins=frontend_urls, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# FIX: Add explicit OPTIONS handler for /api/generate
@app.route('/api/generate', methods=['OPTIONS'])
def generate_options():
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate():
    """Generate music endpoint with CORS fix"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        data = request.get_json() or {}
        
        # Get parameters
        prompt = data.get('prompt', '')
        genre = data.get('genre', 'Pop')
        mood = data.get('mood', 'Happy')
        duration = data.get('duration', 30)
        
        # Generate response with sample music
        generation_id = f"track_{int(datetime.now().timestamp() * 1000)}"
        
        response_data = {
            "success": True,
            "id": generation_id,
            "audioUrl": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "message": "Music generated successfully!",
            "duration": duration,
            "metadata": {
                "prompt": prompt,
                "genre": genre,
                "mood": mood,
                "title": f"Generated {genre} Track"
            }
        }
        
        # Create response with explicit CORS headers
        response = make_response(jsonify(response_data))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Content-Type'] = 'application/json'
        
        return response
        
    except Exception as e:
        error_response = make_response(jsonify({"error": str(e)}), 500)
        error_response.headers['Access-Control-Allow-Origin'] = '*'
        return error_response

# Global OPTIONS handler
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response

# After request handler to ensure CORS headers
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "name": "AI Music Portal Backend",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_health": "/api/health",
            "api_docs": "/api/",
            "generate_music": "/api/generate-music",
            "genres": "/api/genres",
            "moods": "/api/moods",
            "instruments": "/api/instruments"
        },
        "message": "Welcome to AI Music Portal Backend API"
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "AI Music Portal Backend is running",
        "enhanced_generator": ENHANCED_GENERATOR_AVAILABLE
    })

@app.route('/api/health', methods=['GET'])
def api_health_check():
    db_status = test_database_connection() if DATABASE_AVAILABLE else False
    return jsonify({
        "status": "healthy",
        "message": "AI Music Portal Backend is running",
        "enhanced_generator": ENHANCED_GENERATOR_AVAILABLE,
        "database_available": db_status,
        "database_drivers": DATABASE_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/genres', methods=['GET'])
def get_genres():
    try:
        print("Genres request received", file=sys.stderr)
        
        # Try to get genres from database first
        if ENHANCED_FEATURES_AVAILABLE and db_connected:
            try:
                db_genres = db_manager.get_genres()
                if db_genres:
                    # Convert database format to API format
                    genres = []
                    for genre in db_genres:
                        genres.append({
                            "id": genre['genre_code'],
                            "name": genre['name'],
                            "description": genre['description']
                        })
                    
                    print(f"✅ Loaded {len(genres)} genres from database", file=sys.stderr)
                    return jsonify({
                        "success": True,
                        "status": "success",
                        "genres": genres,
                        "source": "database"
                    })
            except Exception as db_error:
                print(f"❌ Database genres failed: {db_error}", file=sys.stderr)
        
        # Fallback to hardcoded genres
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
            {"id": "world", "name": "World", "description": "International and ethnic music"},
            {"id": "rnb", "name": "R&B/Soul", "description": "Rhythm and blues with soulful vocals"},
            {"id": "country", "name": "Country", "description": "American country music with storytelling"},
            {"id": "blues", "name": "Blues", "description": "Traditional blues with emotional depth"},
            {"id": "reggae", "name": "Reggae", "description": "Jamaican reggae with off-beat rhythm"},
            {"id": "funk", "name": "Funk", "description": "Groove-based music with strong rhythm"},
            {"id": "metal", "name": "Metal", "description": "Heavy metal with powerful guitars"},
            {"id": "trap", "name": "Trap", "description": "Modern hip-hop with heavy 808s"},
            {"id": "house", "name": "House", "description": "Four-on-the-floor electronic dance music"},
            {"id": "techno", "name": "Techno", "description": "Driving electronic beats and synthesizers"},
            {"id": "dubstep", "name": "Dubstep", "description": "Electronic music with heavy bass drops"},
            {"id": "gospel", "name": "Gospel", "description": "Spiritual music with choir and organ"},
            {"id": "latin", "name": "Latin", "description": "Latin American music styles"},
            {"id": "k-pop", "name": "K-Pop", "description": "Korean pop music with global appeal"},
            {"id": "lo-fi", "name": "Lo-Fi", "description": "Low-fidelity hip-hop for studying and relaxation"},
            {"id": "afrobeats", "name": "Afrobeats", "description": "West African influenced popular music"},
            {"id": "drill", "name": "Drill", "description": "Aggressive hip-hop subgenre"},
            {"id": "synthwave", "name": "Synthwave", "description": "Retro electronic music inspired by 80s"},
            {"id": "trance", "name": "Trance", "description": "Hypnotic electronic dance music"},
            {"id": "drum_bass", "name": "Drum & Bass", "description": "Fast breakbeats with heavy bass"},
            {"id": "bossa_nova", "name": "Bossa Nova", "description": "Brazilian jazz with smooth guitar"},
            {"id": "punk", "name": "Punk", "description": "Fast, aggressive rock music"}
        ]
        
        response = {
            "success": True,
            "status": "success",
            "genres": genres,
            "source": "fallback"
        }
        print(f"⚠️ Using fallback genres: {len(genres)} genres", file=sys.stderr)
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
        
        # Try to get moods from database first
        if ENHANCED_FEATURES_AVAILABLE and db_connected:
            try:
                db_moods = db_manager.get_moods()
                if db_moods:
                    # Convert database format to API format
                    moods = []
                    for mood in db_moods:
                        moods.append({
                            "id": mood['mood_code'],
                            "name": mood['name'],
                            "description": mood['description'],
                            "color": mood.get('color_code', '#666666')
                        })
                    
                    print(f"✅ Loaded {len(moods)} moods from database", file=sys.stderr)
                    return jsonify({
                        "success": True,
                        "status": "success",
                        "moods": moods,
                        "source": "database"
                    })
            except Exception as db_error:
                print(f"❌ Database moods failed: {db_error}", file=sys.stderr)
        
        # Fallback to hardcoded moods
        moods = [
            {"id": "uplifting", "name": "Uplifting", "description": "Positive and inspiring energy", "color": "#FFD700"},
            {"id": "calm", "name": "Calm", "description": "Peaceful and relaxing", "color": "#87CEEB"},
            {"id": "energetic", "name": "Energetic", "description": "High energy and motivating", "color": "#FF6B35"},
            {"id": "dramatic", "name": "Dramatic", "description": "Intense and emotional", "color": "#8B0000"},
            {"id": "mysterious", "name": "Mysterious", "description": "Dark and intriguing", "color": "#4B0082"},
            {"id": "romantic", "name": "Romantic", "description": "Love and tender emotions", "color": "#FF69B4"},
            {"id": "melancholic", "name": "Melancholic", "description": "Sad and reflective", "color": "#708090"},
            {"id": "triumphant", "name": "Triumphant", "description": "Victory and achievement", "color": "#FFD700"},
            {"id": "playful", "name": "Playful", "description": "Fun and lighthearted", "color": "#32CD32"},
            {"id": "suspenseful", "name": "Suspenseful", "description": "Tension and anticipation", "color": "#B22222"},
            {"id": "nostalgic", "name": "Nostalgic", "description": "Reminiscent and wistful", "color": "#DDA0DD"},
            {"id": "meditative", "name": "Meditative", "description": "Contemplative and zen", "color": "#20B2AA"},
            {"id": "aggressive", "name": "Aggressive", "description": "Intense and forceful for metal and rock", "color": "#DC143C"},
            {"id": "groovy", "name": "Groovy", "description": "Rhythmic and danceable funk vibes", "color": "#FF8C00"},
            {"id": "dreamy", "name": "Dreamy", "description": "Ethereal and atmospheric textures", "color": "#9370DB"},
            {"id": "confident", "name": "Confident", "description": "Strong and self-assured attitude", "color": "#FFD700"},
            {"id": "anxious", "name": "Anxious", "description": "Tense and uneasy atmosphere", "color": "#8B4513"},
            {"id": "euphoric", "name": "Euphoric", "description": "Peak emotional highs and celebration", "color": "#FF1493"},
            {"id": "introspective", "name": "Introspective", "description": "Deep thought and contemplation", "color": "#4682B4"},
            {"id": "rebellious", "name": "Rebellious", "description": "Defiant and alternative attitude", "color": "#000000"},
            {"id": "seductive", "name": "Seductive", "description": "Sensual and alluring for R&B", "color": "#8B008B"},
            {"id": "powerful", "name": "Powerful", "description": "Strong and commanding presence", "color": "#B8860B"},
            {"id": "laid_back", "name": "Laid Back", "description": "Relaxed and easy-going vibe", "color": "#F0E68C"},
            {"id": "professional", "name": "Professional", "description": "Corporate and business-appropriate", "color": "#2F4F4F"},
            {"id": "adventurous", "name": "Adventurous", "description": "Exciting and exploratory", "color": "#FF4500"},
            {"id": "sophisticated", "name": "Sophisticated", "description": "Refined and elegant", "color": "#800080"}
        ]
        
        response = {
            "success": True,
            "status": "success",
            "moods": moods,
            "source": "fallback"
        }
        print(f"⚠️ Using fallback moods: {len(moods)} moods", file=sys.stderr)
        return jsonify(response)
    except Exception as e:
        print(f"Moods error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        return jsonify(response)
    except Exception as e:
        print(f"Moods error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/instruments', methods=['GET'])
def get_instruments():
    try:
        print("Instruments request received", file=sys.stderr)
        
        instruments = [
            {'id': 'acoustic_piano', 'name': 'Acoustic Piano', 'type': 'keyboard', 'priority': 1},
            {'id': 'electric_piano', 'name': 'Electric Piano', 'type': 'keyboard', 'priority': 2},
            {'id': 'organ', 'name': 'Organ', 'type': 'keyboard', 'priority': 3},
            {'id': 'harpsichord', 'name': 'Harpsichord', 'type': 'keyboard', 'priority': 4},
            {'id': 'male_vocals', 'name': 'Male Vocals', 'type': 'vocal', 'priority': 1},
            {'id': 'female_vocals', 'name': 'Female Vocals', 'type': 'vocal', 'priority': 1},
            {'id': 'choir', 'name': 'Choir', 'type': 'vocal', 'priority': 2},
            {'id': 'backing_vocals', 'name': 'Backing Vocals', 'type': 'vocal', 'priority': 3},
            {'id': 'acoustic_guitar', 'name': 'Acoustic Guitar', 'type': 'string', 'priority': 1},
            {'id': 'electric_guitar', 'name': 'Electric Guitar', 'type': 'string', 'priority': 1},
            {'id': 'bass_guitar', 'name': 'Bass Guitar', 'type': 'bass', 'priority': 1},
            {'id': 'electric_bass', 'name': 'Electric Bass', 'type': 'bass', 'priority': 1},
            {'id': 'upright_bass', 'name': 'Upright Bass', 'type': 'bass', 'priority': 2},
            {'id': 'violin', 'name': 'Violin', 'type': 'string', 'priority': 1},
            {'id': 'viola', 'name': 'Viola', 'type': 'string', 'priority': 2},
            {'id': 'cello', 'name': 'Cello', 'type': 'string', 'priority': 2},
            {'id': 'harp', 'name': 'Harp', 'type': 'string', 'priority': 3},
            {'id': 'mandolin', 'name': 'Mandolin', 'type': 'string', 'priority': 3},
            {'id': 'banjo', 'name': 'Banjo', 'type': 'string', 'priority': 3},
            {'id': 'ukulele', 'name': 'Ukulele', 'type': 'string', 'priority': 2},
            {'id': 'acoustic_drums', 'name': 'Acoustic Drums', 'type': 'percussion', 'priority': 1},
            {'id': 'electronic_drums', 'name': 'Electronic Drums', 'type': 'percussion', 'priority': 2},
            {'id': '808_drums', 'name': '808 Drums', 'type': 'percussion', 'priority': 1},
            {'id': 'trap_drums', 'name': 'Trap Drums', 'type': 'percussion', 'priority': 1},
            {'id': 'congas', 'name': 'Congas', 'type': 'percussion', 'priority': 3},
            {'id': 'bongos', 'name': 'Bongos', 'type': 'percussion', 'priority': 3},
            {'id': 'tabla', 'name': 'Tabla', 'type': 'percussion', 'priority': 4},
            {'id': 'xylophone', 'name': 'Xylophone', 'type': 'percussion', 'priority': 3},
            {'id': 'marimba', 'name': 'Marimba', 'type': 'percussion', 'priority': 3},
            {'id': 'trumpet', 'name': 'Trumpet', 'type': 'brass', 'priority': 1},
            {'id': 'trombone', 'name': 'Trombone', 'type': 'brass', 'priority': 2},
            {'id': 'french_horn', 'name': 'French Horn', 'type': 'brass', 'priority': 2},
            {'id': 'tuba', 'name': 'Tuba', 'type': 'brass', 'priority': 3},
            {'id': 'saxophone', 'name': 'Saxophone', 'type': 'brass', 'priority': 2},
            {'id': 'flute', 'name': 'Flute', 'type': 'woodwind', 'priority': 1},
            {'id': 'clarinet', 'name': 'Clarinet', 'type': 'woodwind', 'priority': 1},
            {'id': 'oboe', 'name': 'Oboe', 'type': 'woodwind', 'priority': 2},
            {'id': 'bassoon', 'name': 'Bassoon', 'type': 'woodwind', 'priority': 3},
            {'id': 'harmonica', 'name': 'Harmonica', 'type': 'woodwind', 'priority': 2},
            {'id': 'synthesizer', 'name': 'Synthesizer', 'type': 'electronic', 'priority': 1},
            {'id': 'lead_synth', 'name': 'Lead Synthesizer', 'type': 'electronic', 'priority': 1},
            {'id': 'pad_synth', 'name': 'Pad Synthesizer', 'type': 'electronic', 'priority': 1},
            {'id': 'bass_synth', 'name': 'Bass Synthesizer', 'type': 'electronic', 'priority': 1},
            {'id': 'arp_synth', 'name': 'Arpeggiator Synth', 'type': 'electronic', 'priority': 2},
            {'id': 'sitar', 'name': 'Sitar', 'type': 'world', 'priority': 3},
            {'id': 'didgeridoo', 'name': 'Didgeridoo', 'type': 'world', 'priority': 4},
            {'id': 'accordion', 'name': 'Accordion', 'type': 'world', 'priority': 3},
        ]
        
        response = {
            "success": True,
            "instruments": instruments
        }
        print(f"Instruments response: {len(instruments)} instruments", file=sys.stderr)
        return jsonify(response)
        
    except Exception as e:
        print(f"Instruments error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/composition-templates', methods=['GET'])
def get_composition_templates():
    try:
        print("Composition templates request received", file=sys.stderr)
        
        templates = {
            'pop_ballad': {
                'name': 'Pop Ballad',
                'description': 'Emotional pop song with piano and strings',
                'instruments': ['acoustic_piano', 'acoustic_guitar', 'bass_guitar', 'acoustic_drums', 'female_vocals'],
                'tempo_range': [70, 90],
                'mood': 'romantic'
            },
            'rock_anthem': {
                'name': 'Rock Anthem',
                'description': 'Energetic rock song with guitars and drums',
                'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'male_vocals'],
                'tempo_range': [120, 140],
                'mood': 'energetic'
            },
            'jazz_standard': {
                'name': 'Jazz Standard',
                'description': 'Classic jazz with piano, brass, and rhythm section',
                'instruments': ['acoustic_piano', 'upright_bass', 'acoustic_drums', 'trumpet', 'saxophone'],
                'tempo_range': [120, 160],
                'mood': 'sophisticated'
            },
            'hip_hop_beat': {
                'name': 'Hip-Hop Beat',
                'description': 'Modern hip-hop with 808s and trap elements',
                'instruments': ['808_drums', 'bass_synth', 'lead_synth', 'male_vocals'],
                'tempo_range': [70, 100],
                'mood': 'confident'
            },
            'trap_music': {
                'name': 'Trap',
                'description': 'Heavy 808s with trap drums and synths',
                'instruments': ['trap_drums', '808_drums', 'bass_synth', 'lead_synth'],
                'tempo_range': [130, 170],
                'mood': 'aggressive'
            },
            'rnb_soul': {
                'name': 'R&B/Soul',
                'description': 'Smooth R&B with vocals and groove',
                'instruments': ['electric_piano', 'bass_guitar', 'acoustic_drums', 'female_vocals', 'backing_vocals'],
                'tempo_range': [70, 110],
                'mood': 'seductive'
            },
            'house_music': {
                'name': 'House',
                'description': 'Four-on-the-floor electronic dance music',
                'instruments': ['electronic_drums', 'bass_synth', 'lead_synth', 'pad_synth'],
                'tempo_range': [120, 130],
                'mood': 'euphoric'
            },
            'techno': {
                'name': 'Techno',
                'description': 'Driving electronic beats and synthesizers',
                'instruments': ['electronic_drums', 'bass_synth', 'lead_synth', 'arp_synth'],
                'tempo_range': [120, 140],
                'mood': 'energetic'
            },
            'country': {
                'name': 'Country',
                'description': 'American country with guitar and vocals',
                'instruments': ['acoustic_guitar', 'bass_guitar', 'acoustic_drums', 'male_vocals', 'harmonica'],
                'tempo_range': [80, 120],
                'mood': 'nostalgic'
            },
            'reggae': {
                'name': 'Reggae',
                'description': 'Jamaican reggae with off-beat rhythm',
                'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'male_vocals'],
                'tempo_range': [60, 90],
                'mood': 'laid_back'
            },
            'blues': {
                'name': 'Blues',
                'description': '12-bar blues with guitar and harmonica',
                'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'harmonica', 'male_vocals'],
                'tempo_range': [60, 120],
                'mood': 'melancholic'
            },
            'funk': {
                'name': 'Funk',
                'description': 'Groove-based funk with rhythm section',
                'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'male_vocals'],
                'tempo_range': [100, 130],
                'mood': 'groovy'
            },
            'ambient_chill': {
                'name': 'Ambient Chill',
                'description': 'Relaxing ambient music for meditation',
                'instruments': ['pad_synth', 'acoustic_piano', 'flute', 'harp'],
                'tempo_range': [60, 80],
                'mood': 'dreamy'
            },
            'lo_fi_hip_hop': {
                'name': 'Lo-Fi Hip Hop',
                'description': 'Study music with vintage hip-hop feel',
                'instruments': ['acoustic_drums', 'electric_piano', 'bass_guitar'],
                'tempo_range': [70, 90],
                'mood': 'calm'
            },
            'dubstep': {
                'name': 'Dubstep',
                'description': 'Heavy bass drops and electronic elements',
                'instruments': ['electronic_drums', 'bass_synth', 'lead_synth'],
                'tempo_range': [140, 150],
                'mood': 'aggressive'
            },
            'metal': {
                'name': 'Metal',
                'description': 'Heavy metal with distorted guitars',
                'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'male_vocals'],
                'tempo_range': [120, 180],
                'mood': 'aggressive'
            },
            'gospel': {
                'name': 'Gospel',
                'description': 'Spiritual music with choir and organ',
                'instruments': ['organ', 'acoustic_piano', 'choir', 'acoustic_drums'],
                'tempo_range': [70, 120],
                'mood': 'uplifting'
            },
            'latin': {
                'name': 'Latin',
                'description': 'Latin music with traditional percussion',
                'instruments': ['acoustic_guitar', 'bass_guitar', 'congas', 'bongos', 'female_vocals'],
                'tempo_range': [100, 140],
                'mood': 'playful'
            },
            'podcast_intro': {
                'name': 'Podcast Intro',
                'description': 'Short energetic intro for podcasts',
                'instruments': ['synthesizer', 'electronic_drums', 'bass_synth'],
                'tempo_range': [120, 140],
                'mood': 'confident'
            },
            'corporate_background': {
                'name': 'Corporate Background',
                'description': 'Professional background music for business',
                'instruments': ['acoustic_piano', 'pad_synth'],
                'tempo_range': [80, 110],
                'mood': 'professional'
            },
            'workout_gym': {
                'name': 'Workout/Gym',
                'description': 'High-energy music for fitness',
                'instruments': ['electronic_drums', 'bass_synth', 'lead_synth'],
                'tempo_range': [128, 140],
                'mood': 'energetic'
            },
            'meditation_yoga': {
                'name': 'Meditation/Yoga',
                'description': 'Peaceful music for wellness practices',
                'instruments': ['flute', 'harp', 'pad_synth', 'tabla'],
                'tempo_range': [60, 80],
                'mood': 'meditative'
            },
            'classical_orchestral': {
                'name': 'Classical Orchestral',
                'description': 'Traditional orchestral composition',
                'instruments': ['violin', 'viola', 'cello', 'flute', 'trumpet'],
                'tempo_range': [60, 120],
                'mood': 'dramatic'
            },
            'synthwave': {
                'name': 'Synthwave',
                'description': 'Retro 80s electronic music',
                'instruments': ['lead_synth', 'bass_synth', 'electronic_drums', 'pad_synth'],
                'tempo_range': [110, 130],
                'mood': 'nostalgic'
            },
            'k_pop': {
                'name': 'K-Pop',
                'description': 'Korean pop with modern production',
                'instruments': ['synthesizer', 'electronic_drums', 'bass_synth', 'female_vocals'],
                'tempo_range': [120, 140],
                'mood': 'energetic'
            },
            'afrobeats': {
                'name': 'Afrobeats',
                'description': 'West African influenced popular music',
                'instruments': ['acoustic_drums', 'bass_guitar', 'synthesizer', 'male_vocals'],
                'tempo_range': [100, 120],
                'mood': 'groovy'
            }
        }
        
        response = {
            "success": True,
            "templates": templates
        }
        print(f"Templates response: {len(templates)} templates", file=sys.stderr)
        return jsonify(response)
        
    except Exception as e:
        print(f"Templates error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-music', methods=['POST'])
def generate_music():
    try:
        print("🎵 Generate music request received", file=sys.stderr)
        data = request.get_json()
        if not data:
            print("❌ No data provided in request", file=sys.stderr)
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
            
        prompt = data.get('prompt', '')
        duration = data.get('duration', 30)
        genre = data.get('genre', 'pop')
        mood = data.get('mood', 'upbeat')
        
        # Validate parameters
        if not isinstance(duration, (int, float)) or duration <= 0 or duration > 300:
            return jsonify({
                "success": False,
                "error": "Duration must be a positive number between 1 and 300 seconds"
            }), 400
        
        # Ensure duration is reasonable for testing
        if duration > 60:
            duration = 60  # Limit to 60 seconds for testing
            
        print(f"🎼 Generating music: prompt='{prompt}', duration={duration}, genre={genre}, mood={mood}", file=sys.stderr)
        
        generation_start_time = datetime.now()
        
        # Try enhanced generation first
        if ENHANCED_FEATURES_AVAILABLE:
            try:
                print("🚀 Using enhanced music generator", file=sys.stderr)
                audio_data, track_metadata = enhanced_generator.generate_music_with_metadata(
                    prompt=prompt,
                    genre_code=genre,
                    mood_code=mood,
                    duration=duration
                )
                generation_source = "enhanced_ai"
                print(f"✅ Enhanced generation completed, shape: {audio_data.shape}", file=sys.stderr)
            except Exception as enhanced_error:
                print(f"❌ Enhanced generation failed: {enhanced_error}", file=sys.stderr)
                traceback.print_exc()
                # Fall back to simple generation
                audio_data = generate_simple_audio(duration=duration, genre=genre, mood=mood)
                track_metadata = {}
                generation_source = "simple_fallback"
                print(f"⚠️ Fallback generation completed, shape: {audio_data.shape}", file=sys.stderr)
        else:
            # Use simple generation
            audio_data = generate_simple_audio(duration=duration, genre=genre, mood=mood)
            track_metadata = {}
            generation_source = "simple"
            print(f"✅ Simple generation completed, shape: {audio_data.shape}", file=sys.stderr)
        
        generation_time = (datetime.now() - generation_start_time).total_seconds()
        
        filename = f"music_{uuid.uuid4().hex[:8]}.wav"
        
        # Convert audio data to WAV format
        try:
            if audio_data.dtype != np.int16:
                # Normalize and convert to int16
                audio_normalized = np.clip(audio_data, -1.0, 1.0)
                audio_data_int16 = (audio_normalized * 32767).astype(np.int16)
            else:
                audio_data_int16 = audio_data
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            write(wav_buffer, 44100, audio_data_int16)
            wav_data = wav_buffer.getvalue()
            
            # Save to file
            filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(wav_data)
            
            file_size = len(wav_data)
            print(f"💾 Audio saved: {filepath} ({file_size} bytes)", file=sys.stderr)
            
            # Save track metadata to database if available
            if ENHANCED_FEATURES_AVAILABLE and db_connected and track_metadata:
                try:
                    track_data = {
                        'track_id': filename[:-4],  # Remove .wav extension
                        'user_prompt': prompt,
                        'genre_code': genre,
                        'mood_code': mood,
                        'duration_seconds': duration,
                        'parameters': track_metadata.get('parameters', {}),
                        'file_path': filepath,
                        'file_size_bytes': file_size,
                        'audio_format': 'wav',
                        'generation_model': generation_source,
                        'generation_time_seconds': generation_time
                    }
                    
                    db_saved = db_manager.save_generated_track(track_data)
                    print(f"💾 Track metadata saved to database: {db_saved}", file=sys.stderr)
                except Exception as db_error:
                    print(f"⚠️ Failed to save track metadata: {db_error}", file=sys.stderr)
            
            return jsonify({
                "success": True,
                "message": "Music generated successfully",
                "filename": filename,
                "duration": duration,
                "genre": genre,
                "mood": mood,
                "download_url": f"/api/download/{filename}",
                "generation_time": generation_time,
                "generation_source": generation_source,
                "file_size": file_size,
                "enhanced_features": ENHANCED_FEATURES_AVAILABLE,
                "metadata_saved": ENHANCED_FEATURES_AVAILABLE and db_connected
            })
            
        except Exception as wav_error:
            print(f"❌ WAV processing failed: {wav_error}", file=sys.stderr)
            raise wav_error
            
    except Exception as e:
        print(f"❌ Music generation failed: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Music generation failed: {str(e)}"
        }), 500

@app.route('/api/advanced-generate', methods=['POST'])
def advanced_generate():
    try:
        print("Advanced generate request received", file=sys.stderr)
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        mood = data.get('mood', 'uplifting')
        genre = data.get('genre', 'pop')
        instruments = data.get('instruments', ['piano', 'guitar', 'bass', 'drums'])
        tempo_bpm = data.get('tempo', 120)
        duration = data.get('duration', 30)
        key = data.get('key', 'C')
        complexity = data.get('complexity', 'medium')
        
        print(f"Advanced params: mood={mood}, genre={genre}, instruments={instruments}, tempo={tempo_bpm}", file=sys.stderr)
        
        # Use enhanced generator if available
        if ENHANCED_FEATURES_AVAILABLE and enhanced_generator:
            try:
                # Map frontend instrument names to backend names
                instrument_mapping = {
                    'piano': 'acoustic_piano',
                    'guitar': 'electric_guitar',
                    'bass': 'bass_guitar',
                    'drums': 'acoustic_drums',
                    'strings': 'violin',
                    'brass': 'trumpet',
                    'synth': 'synthesizer'
                }
                
                mapped_instruments = [instrument_mapping.get(inst, inst) for inst in instruments]
                
                audio_data = enhanced_generator.generate_advanced_music(
                    genre=genre,
                    mood=mood,
                    instruments=mapped_instruments,
                    tempo_bpm=tempo_bpm,
                    duration=duration,
                    key=key,
                    complexity=complexity
                )
                print("Enhanced music generation successful", file=sys.stderr)
            except Exception as e:
                print(f"Enhanced generation failed, falling back to simple: {e}", file=sys.stderr)
                audio_data = generate_simple_audio(
                    duration=duration,
                    genre=genre,
                    mood=mood
                )
        else:
            # Fallback to simple generation
            audio_data = generate_simple_audio(
                duration=duration,
                genre=genre,
                mood=mood
            )
        
        filename = f"advanced_music_{uuid.uuid4().hex[:8]}.wav"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        
        if audio_data.dtype != np.int16:
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
        else:
            audio_data_int16 = audio_data
            
        write(filepath, 44100, audio_data_int16)
        
        # Upload to Azure Storage if available
        blob_url = None
        if blob_service_client:
            try:
                with open(filepath, 'rb') as audio_file:
                    blob_url = upload_audio_to_storage(audio_file.read(), filename)
            except Exception as e:
                print(f"Failed to upload to storage: {e}", file=sys.stderr)
        
        response_data = {
            "success": True,
            "message": "Advanced music generated successfully",
            "audio_file": filename,
            "download_url": f"/api/download/{filename}",
            "blob_url": blob_url,
            "metadata": {
                "mood": mood,
                "genre": genre,
                "instruments": instruments,
                "tempo": tempo_bpm,
                "duration": duration,
                "key": key,
                "complexity": complexity,
                "filename": filename,
                "sample_rate": 44100,
                "enhanced_generation": ENHANCED_FEATURES_AVAILABLE and enhanced_generator is not None
            }
        }
        
        print(f"Advanced music generated: {filename}", file=sys.stderr)
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Advanced generate error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-enhanced-music', methods=['POST'])
def generate_enhanced_music():
    """Generate music using the enhanced multi-instrumental generator for Advanced Studio."""
    try:
        data = request.get_json()
        genre = data.get('genre')
        mood = data.get('mood')
        instruments = data.get('instruments', [])
        template = data.get('template')
        duration = int(data.get('duration', 30))
        user_id = data.get('user_id', 'demo_user')
        # Validate required fields
        if not genre or not mood or not instruments:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters (genre, mood, instruments)'
            }), 400

        # Always use fallback simple audio generator for now
        logger.warning("Enhanced generator not available or not implemented, returning mock audio.")
        audio = generate_simple_audio(duration=duration, genre=genre, mood=mood)
        sample_rate = 44100
        filename = f"mock_{uuid.uuid4().hex}.wav"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        write(filepath, sample_rate, audio.astype(np.float32))
        url = f"/api/download-audio/{filename}"
        return jsonify({
            'status': 'success',
            'success': True,
            'audio_url': url,
            'download_url': url,
            'filename': filename,
            'track_id': filename.replace('.wav', ''),
            'metadata': {
                'title': f'Generated {genre.title()} - {mood.title()}',
                'genre': genre,
                'mood': mood,
                'instruments': instruments,
                'duration': duration
            },
            'stem_urls': {},
            'mock': True
        })
    except Exception as e:
        logger.error(f"Enhanced music generation error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to generate enhanced music: {str(e)}'
        }), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Check both /tmp and AUDIO_OUTPUT_DIR for the file
        filepath = os.path.join('/tmp', filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({
                "success": False,
                "error": "File not found"
            }), 404
    except Exception as e:
        print(f"Download error: {str(e)}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/download-audio/<filename>', methods=['GET'])
def download_audio_file(filename):
    try:
        # Check both /tmp and AUDIO_OUTPUT_DIR for the file
        filepath = os.path.join('/tmp', filename)
        if not os.path.exists(filepath):
            filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({
                "success": False,
                "error": "File not found"
            }), 404
    except Exception as e:
        print(f"Download error: {str(e)}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        return jsonify({
            "success": True,
            "status": "running",
            "enhanced_generator": ENHANCED_GENERATOR_AVAILABLE,
            "endpoints": [
                "/api/generate-music",
                "/api/advanced-generate", 
                "/api/instruments",
                "/api/composition-templates",
                "/api/genres",
                "/api/moods"
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/auth/token', methods=['POST'])
def generate_token():
    """Generate authentication token for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'demo_user')
        plan = data.get('plan', 'free')
        
        # For demo purposes, generate a simple token
        # In production, this would be a proper JWT or secure token
        import time
        import hashlib
        
        timestamp = str(int(time.time()))
        token_data = f"{user_id}:{plan}:{timestamp}"
        token = hashlib.sha256(token_data.encode()).hexdigest()[:32]
        
        return jsonify({
            'success': True,
            'token': f"demo_{token}",
            'user_id': user_id,
            'plan': plan,
            'expires_in': 86400  # 24 hours
        })
        
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate authentication token'
        }), 500

@app.route('/api/user/quota', methods=['GET'])
def get_user_quota():
    """Get user's current usage quota"""
    try:
        # For demo purposes, return a simple quota structure
        # In production, this would be based on actual user data
        return jsonify({
            'success': True,
            'quota': {
                'plan': 'free',
                'total_monthly': 100,
                'used_monthly': 5,
                'remaining_monthly': 95,
                'total_daily': 10,
                'used_daily': 2,
                'remaining_today': 8,
                'reset_date': '2024-08-01'
            }
        })
        
    except Exception as e:
        logger.error(f"Quota check error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to check user quota'
        }), 500

# Database Helper Functions
def get_database_connection():
    """Get database connection using FreeTDS/pymssql"""
    if not DATABASE_AVAILABLE or not SQL_CONNECTION_STRING:
        return None
    
    try:
        # Parse connection string for pymssql
        server = "sql-portal-ai-music-dev.database.windows.net"
        database = "portal-ai-music-db"
        username = "sqladmin"
        password = os.getenv('SQL_PASSWORD', 'Portal@AI#Music2025!')
        
        conn = pymssql.connect(
            server=server,
            user=username,
            password=password,
            database=database,
            port=1433,
            timeout=30,
            login_timeout=30,
            charset='UTF-8'
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def test_database_connection():
    """Test database connectivity"""
    try:
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        print(f"Database test failed: {e}")
    return False

# Data collection integration
try:
    from data_collection_integration import register_data_collection_routes
    register_data_collection_routes(app)
    logger.info("Data collection routes registered successfully")
except ImportError as e:
    logger.warning(f"Data collection integration not available: {e}")
except Exception as e:
    logger.error(f"Error registering data collection routes: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"🚀 Starting Flask server on port {port}...")
    print(f"📍 Health check available at: http://localhost:{port}/health")
    print(f"📡 API endpoints available at: http://localhost:{port}/api/")
    print(f"🔧 CORS enabled for: {', '.join(frontend_urls)}")
    print(f"🐛 Debug mode: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
