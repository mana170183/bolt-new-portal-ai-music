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
warnings.filterwarnings("ignore")

# Advanced Music Generation imports
try:
    import torch
    import torchaudio
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write
    import librosa
    import soundfile as sf
    MUSICGEN_AVAILABLE = True
    print("🎵 MusicGen successfully imported", file=sys.stderr)
except ImportError as e:
    MUSICGEN_AVAILABLE = False
    print(f"⚠️  MusicGen not available: {e}", file=sys.stderr)
    print("🔄 Using advanced procedural music generation", file=sys.stderr)

# Import advanced multi-instrumental generator
try:
    from advanced_music_generator import AdvancedMultiInstrumentalGenerator
    ADVANCED_GENERATOR_AVAILABLE = True
    print("🎼 Advanced Multi-Instrumental Generator loaded", file=sys.stderr)
except ImportError as e:
    ADVANCED_GENERATOR_AVAILABLE = False
    print(f"⚠️  Advanced generator not available: {e}", file=sys.stderr)

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
    else:
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
        else:
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
        
        else:
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
def get_available_instruments():
    """Get list of available instruments for multi-instrumental generation"""
    try:
        instruments = [
            {
                "id": "piano",
                "name": "Piano",
                "category": "keyboard",
                "description": "Acoustic piano with rich harmonics"
            },
            {
                "id": "guitar", 
                "name": "Guitar",
                "category": "string",
                "description": "Acoustic/electric guitar with strumming patterns"
            },
            {
                "id": "bass",
                "name": "Bass Guitar", 
                "category": "string",
                "description": "Electric bass guitar for rhythm section"
            },
            {
                "id": "drums",
                "name": "Drum Kit",
                "category": "percussion", 
                "description": "Complete drum kit (kick, snare, hi-hat)"
            },
            {
                "id": "strings",
                "name": "String Section",
                "category": "orchestral",
                "description": "Orchestral string ensemble with vibrato"
            },
            {
                "id": "synthesizer",
                "name": "Synthesizer",
                "category": "electronic",
                "description": "Electronic synthesizer with various waveforms"
            }
        ]
        
        return jsonify({
            "success": True,
            "instruments": instruments
        })
        
    except Exception as e:
        print(f"Error getting instruments: {e}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/composition-templates', methods=['GET'])
def get_composition_templates():
    """Get pre-defined composition templates for different genres"""
    try:
        templates = {
            "pop": {
                "name": "Pop Song",
                "instruments": ["piano", "guitar", "bass", "drums"],
                "tempo_range": [120, 140],
                "structure": "Verse-Chorus-Verse-Chorus-Bridge-Chorus",
                "chord_progressions": ["vi-IV-I-V", "I-V-vi-IV"]
            },
            "rock": {
                "name": "Rock Song", 
                "instruments": ["guitar", "bass", "drums"],
                "tempo_range": [140, 180],
                "structure": "Intro-Verse-Chorus-Verse-Chorus-Solo-Chorus",
                "chord_progressions": ["I-IV-V-I", "vi-IV-I-V"]
            },
            "jazz": {
                "name": "Jazz Standard",
                "instruments": ["piano", "bass", "drums"],
                "tempo_range": [80, 120],
                "structure": "Head-Solos-Head",
                "chord_progressions": ["ii-V-I", "I-vi-ii-V"]
            },
            "orchestral": {
                "name": "Orchestral Piece",
                "instruments": ["strings", "piano"],
                "tempo_range": [60, 100],
                "structure": "Exposition-Development-Recapitulation",
                "chord_progressions": ["I-V-vi-iii-IV-I-IV-V"]
            },
            "folk": {
                "name": "Folk Song",
                "instruments": ["guitar", "bass"],
                "tempo_range": [80, 110], 
                "structure": "Verse-Chorus-Verse-Chorus-Bridge-Chorus",
                "chord_progressions": ["I-IV-V-I", "vi-IV-I-V"]
            }
        }
        
        return jsonify({
            "success": True,
            "templates": templates
        })
        
    except Exception as e:
        print(f"Error getting templates: {e}", file=sys.stderr)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


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