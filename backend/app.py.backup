from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import traceback
from dotenv import load_dotenv
import numpy as np
import tempfile
import uuid
import time
import threading
import warnings
import wave
import random
import soundfile as sf
warnings.filterwarnings("ignore")

# Advanced Music Generation imports (MusicGen)
try:
    import torch
    import torchaudio
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write
    MUSICGEN_AVAILABLE = True
    print("🎵 MusicGen successfully imported", file=sys.stderr)
except ImportError as e:
    MUSICGEN_AVAILABLE = False
    print(f"⚠️  MusicGen not available: {e}", file=sys.stderr)
    print("🔄 Using enhanced procedural music generation", file=sys.stderr)

# Enhanced Music Generation imports
try:
    from enhanced_main_generator import EnhancedMultiInstrumentalGenerator
    ENHANCED_GENERATOR_AVAILABLE = True
    print("🎼 Enhanced Multi-Instrumental Generator imported successfully", file=sys.stderr)
    enhanced_generator = EnhancedMultiInstrumentalGenerator()
except ImportError as e:
    ENHANCED_GENERATOR_AVAILABLE = False
    enhanced_generator = None
    print(f"⚠️  Enhanced generator not available: {e}", file=sys.stderr)

# Import advanced multi-instrumental generator
try:
    from advanced_music_generator import AdvancedMultiInstrumentalGenerator
    ADVANCED_GENERATOR_AVAILABLE = True
    print("🎼 Advanced Multi-Instrumental Generator loaded", file=sys.stderr)
except ImportError as e:
    ADVANCED_GENERATOR_AVAILABLE = False
    print(f"⚠️  Advanced generator not available: {e}", file=sys.stderr)

# Import the advanced AI music core
from ai_music_core import get_composer, MusicGenerationRequest

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
    'http://localhost:3003',
    'http://127.0.0.1:3003',
    'http://localhost:3004',
    'http://127.0.0.1:3004',
    'http://localhost:3005',  # Current frontend port
    'http://127.0.0.1:3005',
    'http://localhost:5173',  # Vite dev server default
    'http://127.0.0.1:5173'
])

# Global MusicGen model variable
musicgen_model = None
model_lock = threading.Lock()

def initialize_musicgen():
    """Initialize MusicGen model (lazy loading)"""
    global musicgen_model
    with model_lock:
        if musicgen_model is None and MUSICGEN_AVAILABLE:
            try:
                print("🔄 Loading MusicGen model (this may take a few minutes)...", file=sys.stderr)
                # Use the small model for faster inference
                musicgen_model = MusicGen.get_pretrained('facebook/musicgen-small')
                musicgen_model.set_generation_params(duration=30)  # Default 30 seconds
                print("✅ MusicGen model loaded successfully", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to load MusicGen model: {e}", file=sys.stderr)
                traceback.print_exc()
    return musicgen_model is not None

# Create necessary directories
os.makedirs('generated_audio', exist_ok=True)

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
        "port": os.environ.get('PORT', 5000),
        "musicgen_available": MUSICGEN_AVAILABLE,
        "model_loaded": musicgen_model is not None
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
        # Comprehensive genre list - Industry Standard 25+ genres
        genres = [
            # Existing genres (enhanced)
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
            
            # NEW CRITICAL GENRES
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
        # Comprehensive mood list - Industry Standard 20+ moods
        moods = [
            # Existing moods (enhanced)
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
            {"id": "meditative", "name": "Meditative", "description": "Contemplative and zen"},
            
            # NEW CRITICAL MOODS
            {"id": "aggressive", "name": "Aggressive", "description": "Intense and forceful for metal and rock"},
            {"id": "groovy", "name": "Groovy", "description": "Rhythmic and danceable funk vibes"},
            {"id": "dreamy", "name": "Dreamy", "description": "Ethereal and atmospheric textures"},
            {"id": "confident", "name": "Confident", "description": "Strong and self-assured attitude"},
            {"id": "anxious", "name": "Anxious", "description": "Tense and uneasy atmosphere"},
            {"id": "euphoric", "name": "Euphoric", "description": "Peak emotional highs and celebration"},
            {"id": "introspective", "name": "Introspective", "description": "Deep thought and contemplation"},
            {"id": "rebellious", "name": "Rebellious", "description": "Defiant and alternative attitude"},
            {"id": "seductive", "name": "Seductive", "description": "Sensual and alluring for R&B"},
            {"id": "powerful", "name": "Powerful", "description": "Strong and commanding presence"},
            {"id": "laid_back", "name": "Laid Back", "description": "Relaxed and easy-going vibe"},
            {"id": "professional", "name": "Professional", "description": "Corporate and business-appropriate"},
            {"id": "adventurous", "name": "Adventurous", "description": "Exciting and exploratory"},
            {"id": "sophisticated", "name": "Sophisticated", "description": "Refined and elegant"}
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
        
        # Generate track ID and title
        import random
        track_id = f"track_{int(time.time())}_{random.randint(1000, 9999)}"
        title_templates = [
            f"{genre.title()} {mood.title()} Track",
            f"{mood.title()} {genre.title()} Composition",
            f"AI Generated {genre.title()}",
            f"{prompt[:20]}..." if len(prompt) > 20 else prompt
        ]
        selected_title = random.choice(title_templates)
        
        # Create enhanced prompt for better AI generation
        enhanced_prompt = f"{prompt}, {genre} style, {mood} mood"
        
        # Generate audio file using MusicGen or fallback
        filepath, filename = generate_ai_music(enhanced_prompt, duration, track_id)
        
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

def generate_ai_music(prompt, duration, track_id):
    """Generate music using MusicGen AI or fallback to simple audio"""
    filename = f"{track_id}.wav"
    filepath = os.path.join('generated_audio', filename)
    
    if MUSICGEN_AVAILABLE:
        try:
            # Initialize model if not already loaded
            if not initialize_musicgen():
                raise Exception("Failed to initialize MusicGen model")
            
            print(f"🎵 Generating AI music for prompt: '{prompt}' (duration: {duration}s)", file=sys.stderr)
            
            # Set generation parameters
            musicgen_model.set_generation_params(duration=min(duration, 30))  # Max 30 seconds for small model
            
            # Generate music using MusicGen
            descriptions = [prompt]
            wav = musicgen_model.generate(descriptions)
            
            # Save the generated audio
            for idx, one_wav in enumerate(wav):
                # Convert to CPU and save
                audio_write(filepath[:-4], one_wav.cpu().squeeze(0), musicgen_model.sample_rate, strategy="loudness")
                print(f"✅ AI music generated successfully: {filename}", file=sys.stderr)
                break
            
            return filepath, filename
            
        except Exception as e:
            print(f"❌ MusicGen generation failed: {e}", file=sys.stderr)
            print("🔄 Falling back to simple audio generation", file=sys.stderr)
            traceback.print_exc()
    
    # Fallback to simple audio generation
    return generate_fallback_audio(prompt, duration, track_id)

def generate_fallback_audio(prompt, duration, track_id):
    """Generate advanced procedural music based on prompt analysis"""
    filename = f"{track_id}.wav"
    filepath = os.path.join('generated_audio', filename)
    
    sample_rate = 44100  # Higher quality audio
    audio_duration = min(duration, 30)  # Limit to 30 seconds
    
    # Analyze prompt for musical characteristics
    prompt_lower = prompt.lower()
    
    # Determine key and scale
    key_frequencies = {
        'c': 261.63, 'c#': 277.18, 'd': 293.66, 'd#': 311.13,
        'e': 329.63, 'f': 349.23, 'f#': 369.99, 'g': 392.00,
        'g#': 415.30, 'a': 440.00, 'a#': 466.16, 'b': 493.88
    }
    
    # Choose key based on mood
    if any(word in prompt_lower for word in ['happy', 'bright', 'joyful', 'upbeat']):
        root_freq = key_frequencies['c']  # C major
        scale = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]  # Major scale
        tempo = 120
    elif any(word in prompt_lower for word in ['sad', 'melancholic', 'dark', 'minor']):
        root_freq = key_frequencies['a']  # A minor
        scale = [1, 9/8, 6/5, 4/3, 3/2, 8/5, 9/5]  # Natural minor scale
        tempo = 80
    elif any(word in prompt_lower for word in ['energetic', 'rock', 'fast', 'aggressive']):
        root_freq = key_frequencies['e']  # E major
        scale = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]
        tempo = 140
    elif any(word in prompt_lower for word in ['calm', 'peaceful', 'ambient', 'soft']):
        root_freq = key_frequencies['f']  # F major
        scale = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]
        tempo = 60
    # else:
        root_freq = key_frequencies['g']  # G major (default)
        scale = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]
        tempo = 100
    
    # Generate chord progression
    def generate_chord_progression():
        if 'rock' in prompt_lower or 'aggressive' in prompt_lower:
            return [1, 6, 4, 5]  # vi-IV-I-V (rock progression)
        elif 'jazz' in prompt_lower:
            return [1, 6, 2, 5]  # ii-V-I-vi (jazz progression)
        elif 'pop' in prompt_lower:
            return [1, 5, 6, 4]  # I-V-vi-IV (pop progression)
        # else:
            return [1, 4, 5, 1]  # I-IV-V-I (classic progression)
    
    progression = generate_chord_progression()
    
    # Generate time array
    num_samples = int(audio_duration * sample_rate)
    t = np.linspace(0, audio_duration, num_samples, False)
    
    # Initialize audio buffer
    audio_data = np.zeros(num_samples)
    
    # Generate bass line
    beats_per_second = tempo / 60
    chord_duration = 2.0  # Each chord lasts 2 seconds
    
    for i, chord_degree in enumerate(progression):
        start_time = i * chord_duration
        end_time = min((i + 1) * chord_duration, audio_duration)
        
        if start_time >= audio_duration:
            break
            
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        # Bass frequency (root of chord)
        bass_freq = root_freq * scale[chord_degree - 1] / 2  # One octave down
        
        # Generate bass line with rhythm
        t_segment = t[start_sample:end_sample]
        bass_wave = 0.3 * np.sin(2 * np.pi * bass_freq * t_segment)
        
        # Add rhythm (emphasize beats)
        rhythm_freq = beats_per_second
        rhythm_envelope = 0.7 + 0.3 * np.sin(2 * np.pi * rhythm_freq * t_segment)
        bass_wave *= rhythm_envelope
        
        audio_data[start_sample:end_sample] += bass_wave
    
    # Generate melody line
    melody_notes = [1, 3, 5, 3, 2, 4, 6, 5]  # Scale degrees
    note_duration = 0.5  # Each note lasts 0.5 seconds
    
    for i, note_degree in enumerate(melody_notes * int(audio_duration / (len(melody_notes) * note_duration) + 1)):
        start_time = i * note_duration
        end_time = min((i + 1) * note_duration, audio_duration)
        
        if start_time >= audio_duration:
            break
            
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        # Melody frequency
        melody_freq = root_freq * scale[(note_degree - 1) % len(scale)] * 2  # One octave up
        
        t_segment = t[start_sample:end_sample]
        
        # Generate melody with attack and decay
        envelope = np.exp(-5 * (t_segment - start_time))
        melody_wave = 0.2 * envelope * np.sin(2 * np.pi * melody_freq * t_segment)
        
        # Add some harmonics for richness
        melody_wave += 0.1 * envelope * np.sin(2 * np.pi * melody_freq * 2 * t_segment)
        melody_wave += 0.05 * envelope * np.sin(2 * np.pi * melody_freq * 3 * t_segment)
        
        audio_data[start_sample:end_sample] += melody_wave
    
    # Add chord harmonies
    for i, chord_degree in enumerate(progression):
        start_time = i * chord_duration
        end_time = min((i + 1) * chord_duration, audio_duration)
        
        if start_time >= audio_duration:
            break
            
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        t_segment = t[start_sample:end_sample]
        
        # Triad (root, third, fifth)
        for j, interval in enumerate([1, 3, 5]):
            harmony_freq = root_freq * scale[(chord_degree + interval - 2) % len(scale)]
            harmony_wave = 0.1 * np.sin(2 * np.pi * harmony_freq * t_segment)
            
            # Add subtle amplitude modulation for movement
            mod_freq = 0.5 + j * 0.2
            modulation = 0.8 + 0.2 * np.sin(2 * np.pi * mod_freq * t_segment)
            harmony_wave *= modulation
            
            audio_data[start_sample:end_sample] += harmony_wave
    
    # Add percussion/rhythm track
    if 'rock' in prompt_lower or 'energetic' in prompt_lower:
        kick_freq = 60  # Kick drum frequency
        for beat in np.arange(0, audio_duration, 60/tempo):
            if beat >= audio_duration:
                break
            start_sample = int(beat * sample_rate)
            end_sample = min(start_sample + int(0.1 * sample_rate), num_samples)
            
            t_drum = np.linspace(0, 0.1, end_sample - start_sample, False)
            kick_wave = 0.3 * np.exp(-20 * t_drum) * np.sin(2 * np.pi * kick_freq * t_drum)
            audio_data[start_sample:end_sample] += kick_wave
    
    # Apply filters based on genre
    if 'ambient' in prompt_lower or 'soft' in prompt_lower:
        # Low-pass filter effect (simple moving average)
        window_size = int(sample_rate * 0.001)  # 1ms window
        audio_data = np.convolve(audio_data, np.ones(window_size)/window_size, mode='same')
    
    # Apply dynamic range and normalization
    audio_data = np.tanh(audio_data)  # Soft clipping
    max_amplitude = np.max(np.abs(audio_data))
    if max_amplitude > 0:
        audio_data = audio_data * 0.8 / max_amplitude  # Normalize to 80% of max
    
    # Apply fade in/out
    fade_length = int(0.2 * sample_rate)  # 0.2 second fade
    fade_in = np.linspace(0, 1, fade_length)
    fade_out = np.linspace(1, 0, fade_length)
    
    audio_data[:fade_length] *= fade_in
    audio_data[-fade_length:] *= fade_out
    
    # Convert to 16-bit integers
    audio_data = np.int16(audio_data * 32767)
    
    # Write WAV file
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"🎼 Advanced procedural music generated: {filename}", file=sys.stderr)
    return filepath, filename

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

@app.route('/api/generate-advanced-music', methods=['POST'])
def generate_advanced_music():
    """
    Generate advanced multi-instrumental music composition
    
    Expected JSON payload:
    {
        "lyrics": "optional lyrics text",
        "mood": "upbeat|sad|energetic|calm|etc",
        "genre": "pop|rock|jazz|blues|folk|etc", 
        "instruments": ["piano", "guitar", "bass", "drums", "strings"],
        "tempo_bpm": 120,
        "duration": 30,
        "output_format": "wav|mp3|midi",
        "export_stems": false
    }
    """
    try:
        print("Advanced music generation request received", file=sys.stderr)
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Extract parameters with defaults
        lyrics = data.get('lyrics', '')
        mood = data.get('mood', 'upbeat')
        genre = data.get('genre', 'pop')
        instruments = data.get('instruments', ['piano', 'guitar', 'bass', 'drums'])
        tempo_bpm = data.get('tempo_bpm', 120)
        duration = data.get('duration', 30)
        output_format = data.get('output_format', 'wav')
        export_stems = data.get('export_stems', False)
        
        print(f"Advanced params: mood={mood}, genre={genre}, instruments={instruments}, tempo={tempo_bpm}", file=sys.stderr)
        
        # Generate track ID
        track_id = f"advanced_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Check if advanced generator is available
        if ADVANCED_GENERATOR_AVAILABLE:
            try:
                # Initialize generator
                generator = AdvancedMultiInstrumentalGenerator()
                
                # Prepare generation parameters
                params = {
                    'lyrics': lyrics,
                    'mood': mood,
                    'genre': genre,
                    'instruments': instruments,
                    'tempo_bpm': tempo_bpm,
                    'duration': duration
                }
                
                # Generate composition
                audio_data, metadata = generator.generate_composition(params)
                
                # Save main composition
                filename = f"{track_id}.wav"
                filepath = os.path.join('generated_audio', filename)
                sf.write(filepath, audio_data, 44100)
                
                # Export stems if requested
                stem_files = {}
                if export_stems and hasattr(generator, 'export_stems'):
                    # This would require modification to return individual tracks
                    print("Stem export requested but not yet implemented", file=sys.stderr)
                
                # Create response
                track_info = {
                    "id": track_id,
                    "title": f"{genre.title()} {mood.title()} Composition",
                    "url": f"/api/audio/{filename}",
                    "download_url": f"/api/audio/{filename}",
                    "duration": duration,
                    "genre": genre,
                    "mood": mood,
                    "instruments": instruments,
                    "tempo_bpm": tempo_bpm,
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "metadata": metadata,
                    "stems": stem_files if export_stems else {},
                    "waveform_data": generate_waveform_data(audio_data)
                }
                
                print(f"Advanced music generated successfully: {track_id}", file=sys.stderr)
                return jsonify({
                    "status": "success",
                    "success": True,
                    "track": track_info
                })
                
            except Exception as e:
                print(f"Advanced generation failed: {e}", file=sys.stderr)
                traceback.print_exc()
                # Fall back to regular generation
                return generate_music()
        
        # else:
            # Fall back to regular generation if advanced not available
            print("Advanced generator not available, falling back to regular generation", file=sys.stderr)
            return generate_music()
            
    except Exception as e:
        print(f"Advanced music generation error: {e}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Music generation failed: {str(e)}"
        }), 500

@app.route('/api/instruments', methods=['GET'])
def get_instruments():
    """Get available instruments for the enhanced generator"""
    try:
        print("Instruments request received", file=sys.stderr)
        
        # FORCE USE COMPREHENSIVE LIST - if ENHANCED_GENERATOR_AVAILABLE and enhanced_generator:
        # instruments = enhanced_generator.get_available_instruments()
        # else:
        # Comprehensive instrument list - Industry Standard 40+ instruments
        instruments = [
                # Keyboard Instruments
                {'id': 'acoustic_piano', 'name': 'Acoustic Piano', 'type': 'keyboard', 'priority': 1},
                {'id': 'electric_piano', 'name': 'Electric Piano', 'type': 'keyboard', 'priority': 2},
                {'id': 'organ', 'name': 'Organ', 'type': 'keyboard', 'priority': 3},
                {'id': 'harpsichord', 'name': 'Harpsichord', 'type': 'keyboard', 'priority': 4},
                
                # Vocal Instruments - CRITICAL ADDITION
                {'id': 'male_vocals', 'name': 'Male Vocals', 'type': 'vocal', 'priority': 1},
                {'id': 'female_vocals', 'name': 'Female Vocals', 'type': 'vocal', 'priority': 1},
                {'id': 'choir', 'name': 'Choir', 'type': 'vocal', 'priority': 2},
                {'id': 'backing_vocals', 'name': 'Backing Vocals', 'type': 'vocal', 'priority': 3},
                
                # String Instruments
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
                
                # Percussion Instruments
                {'id': 'acoustic_drums', 'name': 'Acoustic Drums', 'type': 'percussion', 'priority': 1},
                {'id': 'electronic_drums', 'name': 'Electronic Drums', 'type': 'percussion', 'priority': 2},
                {'id': '808_drums', 'name': '808 Drums', 'type': 'percussion', 'priority': 1},
                {'id': 'trap_drums', 'name': 'Trap Drums', 'type': 'percussion', 'priority': 1},
                {'id': 'congas', 'name': 'Congas', 'type': 'percussion', 'priority': 3},
                {'id': 'bongos', 'name': 'Bongos', 'type': 'percussion', 'priority': 3},
                {'id': 'tabla', 'name': 'Tabla', 'type': 'percussion', 'priority': 4},
                {'id': 'xylophone', 'name': 'Xylophone', 'type': 'percussion', 'priority': 3},
                {'id': 'marimba', 'name': 'Marimba', 'type': 'percussion', 'priority': 3},
                
                # Brass Instruments
                {'id': 'trumpet', 'name': 'Trumpet', 'type': 'brass', 'priority': 1},
                {'id': 'trombone', 'name': 'Trombone', 'type': 'brass', 'priority': 2},
                {'id': 'french_horn', 'name': 'French Horn', 'type': 'brass', 'priority': 2},
                {'id': 'tuba', 'name': 'Tuba', 'type': 'brass', 'priority': 3},
                {'id': 'saxophone', 'name': 'Saxophone', 'type': 'brass', 'priority': 2},
                
                # Woodwind Instruments
                {'id': 'flute', 'name': 'Flute', 'type': 'woodwind', 'priority': 1},
                {'id': 'clarinet', 'name': 'Clarinet', 'type': 'woodwind', 'priority': 1},
                {'id': 'oboe', 'name': 'Oboe', 'type': 'woodwind', 'priority': 2},
                {'id': 'bassoon', 'name': 'Bassoon', 'type': 'woodwind', 'priority': 3},
                {'id': 'harmonica', 'name': 'Harmonica', 'type': 'woodwind', 'priority': 2},
                
                # Electronic Instruments
                {'id': 'synthesizer', 'name': 'Synthesizer', 'type': 'electronic', 'priority': 1},
                {'id': 'lead_synth', 'name': 'Lead Synthesizer', 'type': 'electronic', 'priority': 1},
                {'id': 'pad_synth', 'name': 'Pad Synthesizer', 'type': 'electronic', 'priority': 1},
                {'id': 'bass_synth', 'name': 'Bass Synthesizer', 'type': 'electronic', 'priority': 1},
                {'id': 'arp_synth', 'name': 'Arpeggiator Synth', 'type': 'electronic', 'priority': 2},
                
                # World Instruments
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
    """Get available composition templates"""
    try:
        print("Composition templates request received", file=sys.stderr)
        
        # FORCE USE COMPREHENSIVE LIST - if ENHANCED_GENERATOR_AVAILABLE and enhanced_generator:
        # templates = enhanced_generator.get_composition_templates()
        # else:
        # Comprehensive templates - Industry Standard 25+ templates
        templates = {
                # Existing Templates (Enhanced)
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
                
                # NEW CRITICAL TEMPLATES
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
                    'instruments': ['acoustic_drums', 'electric_piano', 'bass_guitar', 'vinyl_crackle'],
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
                
                # CONTENT CREATION TEMPLATES
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
                    'instruments': ['acoustic_piano', 'strings', 'pad_synth'],
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
                'cinematic_orchestral': {
                    'name': 'Cinematic Orchestral',
                    'description': 'Epic orchestral music for film scoring',
                    'instruments': ['violin', 'viola', 'cello', 'trumpet', 'french_horn', 'acoustic_drums'],
                    'tempo_range': [60, 140],
                    'mood': 'dramatic'
                },
                'video_game_music': {
                    'name': 'Video Game Music',
                    'description': 'Dynamic music for gaming',
                    'instruments': ['synthesizer', 'electronic_drums', 'lead_synth', 'arp_synth'],
                    'tempo_range': [100, 160],
                    'mood': 'adventurous'
                },
                'commercial_jingle': {
                    'name': 'Commercial Jingle',
                    'description': 'Catchy short music for advertising',
                    'instruments': ['acoustic_piano', 'acoustic_guitar', 'female_vocals', 'acoustic_drums'],
                    'tempo_range': [110, 130],
                    'mood': 'uplifting'
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

@app.route('/api/generate-enhanced-music', methods=['POST'])
def generate_enhanced_music():
    """Generate music using the enhanced multi-instrumental generator"""
    try:
        print("Enhanced music generation request received", file=sys.stderr)
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        print(f"Enhanced generation params: {data}", file=sys.stderr)
        
        # Extract parameters
        params = {
            'lyrics': data.get('lyrics', ''),
            'mood': data.get('mood', 'happy'),
            'genre': data.get('genre', 'pop'),
            'instruments': data.get('instruments', ['acoustic_piano', 'acoustic_guitar']),
            'tempo_bpm': data.get('tempo_bpm'),
            'duration': float(data.get('duration', 30)),
            'key': data.get('key', 'C'),
            'structure': data.get('structure', []),
            'template': data.get('template'),
            'export_stems': data.get('export_stems', False),
            'style_complexity': data.get('style_complexity', 'moderate'),
            'output_format': data.get('output_format', 'wav')
        }
        
        # Generate unique track ID
        track_id = f"enhanced_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # FORCE USE COMPREHENSIVE LIST - if ENHANCED_GENERATOR_AVAILABLE and enhanced_generator:
            print("Using enhanced generator", file=sys.stderr)
            
            # Generate the composition
            audio_data, metadata = enhanced_generator.generate_composition(params)
            
            # Save audio file
            filename = f"{track_id}.wav"
            filepath = os.path.join('generated_audio', filename)
            
            # Ensure directory exists
            os.makedirs('generated_audio', exist_ok=True)
            
            # Normalize and save audio
            if np.max(np.abs(audio_data)) > 0:
                normalized_audio = audio_data / np.max(np.abs(audio_data)) * 0.8
            # else:
                normalized_audio = audio_data
            
            sf.write(filepath, normalized_audio, enhanced_generator.sample_rate)
            
            print(f"Enhanced audio saved: {filepath}", file=sys.stderr)
            
            # Create response
            response = {
                "success": True,
                "status": "completed",
                "track_id": track_id,
                "filename": filename,
                "audio_url": f"/api/audio/{filename}",
                "download_url": f"/api/download/{filename}",
                "metadata": metadata,
                "duration": params['duration'],
                "sample_rate": enhanced_generator.sample_rate
            }
            
            # Add stem files if exported
            if params['export_stems'] and 'stem_files' in metadata:
                stem_urls = {}
                for instrument, stem_path in metadata['stem_files'].items():
                    stem_filename = os.path.basename(stem_path)
                    stem_urls[instrument] = f"/api/audio/stems/{stem_filename}"
                response['stem_urls'] = stem_urls
            
        # else:
            print("Enhanced generator not available, using fallback", file=sys.stderr)
            # Fallback to basic generation
            response = {
                "success": False,
                "error": "Enhanced generator not available. Please check server configuration."
            }
        
        print(f"Enhanced generation response: {response.get('success', False)}", file=sys.stderr)
        return jsonify(response)
        
    except Exception as e:
        print(f"Enhanced generation error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-ai-music', methods=['POST'])
def generate_ai_music():
    """
    Generate multi-instrumental AI music composition using advanced neural networks.
    Expects JSON payload with:
      - lyrics (str)
      - genre (str)
      - mood (str)
      - tempo_bpm (int)
      - duration (float)
      - instruments (list of str, min 3)
      - key (optional)
      - time_signature (optional)
      - style_complexity (optional)
      - enable_stems (optional)
      - export_formats (optional)
    Returns: stems, metadata, and download links.
    """
    try:
        data = request.get_json(force=True)
        # Validate required fields
        required = ['lyrics', 'genre', 'mood', 'tempo_bpm', 'duration', 'instruments']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        if not isinstance(data['instruments'], list) or len(data['instruments']) < 3:
            return jsonify({"success": False, "error": "At least 3 instruments must be selected."}), 400

        # Build request object
        req = MusicGenerationRequest(
            lyrics=data['lyrics'],
            genre=data['genre'],
            mood=data['mood'],
            tempo_bpm=int(data['tempo_bpm']),
            duration=float(data['duration']),
            instruments=data['instruments'],
            key=data.get('key', 'C'),
            time_signature=data.get('time_signature', '4/4'),
            style_complexity=data.get('style_complexity', 'moderate'),
            enable_stems=bool(data.get('enable_stems', True)),
            export_formats=data.get('export_formats', ['wav', 'midi'])
        )
        composer = get_composer()
        tracks, metadata = composer.generate_composition(req)

        # Save stems and build response
        stem_files = {}
        for track in tracks:
            filename = f"{track.instrument_name}_{uuid.uuid4().hex[:8]}.wav"
            filepath = os.path.join('generated_audio', filename)
            sf.write(filepath, track.audio_data, 44100)
            stem_files[track.instrument_name] = f"/api/audio/{filename}"

        response = {
            "success": True,
            "metadata": metadata,
            "stems": stem_files,
            "message": "AI music generated successfully."
        }
        return jsonify(response)
    except Exception as e:
        print(f"AI music generation error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

def generate_waveform_data(audio_data, num_points=50):
    """Generate waveform visualization data from audio"""
    try:
        # Downsample for visualization
        step = len(audio_data) // num_points
        if step < 1:
            step = 1
        
        downsampled = audio_data[::step]
        
        # Convert to amplitude values (0-100)
        normalized = np.abs(downsampled)
        max_val = np.max(normalized) if np.max(normalized) > 0 else 1
        waveform = (normalized / max_val * 100).astype(int).tolist()
        
        # Ensure we have exactly num_points
        if len(waveform) > num_points:
            waveform = waveform[:num_points]
        elif len(waveform) < num_points:
            waveform.extend([0] * (num_points - len(waveform)))
            
        return waveform
        
    except Exception as e:
        print(f"Error generating waveform data: {e}", file=sys.stderr)
        return [random.randint(10, 50) for _ in range(num_points)]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"🚀 Starting Flask server on port {port}...", file=sys.stderr)
    print(f"📍 Health check available at: http://localhost:{port}/health", file=sys.stderr)
    print(f"📡 API endpoints available at: http://localhost:{port}/api/", file=sys.stderr)
    print("🔧 CORS enabled for: http://localhost:3000, http://127.0.0.1:3000", file=sys.stderr)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True
    )