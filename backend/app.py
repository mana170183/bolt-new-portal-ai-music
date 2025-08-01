# DEPRECATED: This Flask app has been replaced by test-server.cjs (Node.js/Express)
# The current backend runs on port 7071 instead of port 5000
# This file is kept for reference but should not be used

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

def generate_enhanced_audio(duration=30, genre='pop', mood='upbeat'):
    """
    Generate enhanced, pleasant audio based on parameters
    Improved algorithm to avoid buzzing sounds
    """
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
try:
    from enhanced_main_generator import EnhancedMultiInstrumentalGenerator
    ENHANCED_GENERATOR_AVAILABLE = True
    enhanced_generator = EnhancedMultiInstrumentalGenerator()
    print("🎼 Enhanced Multi-Instrumental Generator imported successfully")
except ImportError as e:
    ENHANCED_GENERATOR_AVAILABLE = False
    enhanced_generator = None
    print(f"⚠️  Enhanced generator not available: {e}")

try:
    from advanced_music_generator import AdvancedMultiInstrumentalGenerator
    if not ENHANCED_GENERATOR_AVAILABLE:
        enhanced_generator = AdvancedMultiInstrumentalGenerator()
        ENHANCED_GENERATOR_AVAILABLE = True
        print("🎼 Advanced Multi-Instrumental Generator loaded")
except ImportError:
    print("🔄 Using basic procedural music generation")

app = Flask(__name__)

frontend_urls = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

CORS(app, origins=frontend_urls, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "AI Music Portal Backend is running",
        "enhanced_generator": ENHANCED_GENERATOR_AVAILABLE
    })

@app.route('/api/health', methods=['GET'])
def api_health_check():
    return jsonify({
        "status": "healthy",
        "message": "AI Music Portal Backend is running",
        "enhanced_generator": ENHANCED_GENERATOR_AVAILABLE,
        "database_available": False,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/genres', methods=['GET'])
def get_genres():
    try:
        print("Genres request received", file=sys.stderr)
        # Placeholder music genres
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
        # Placeholder music moods
        moods = [
            {"id": "uplifting", "name": "Uplifting", "description": "Positive and inspiring energy"},
            {"id": "calm", "name": "Calm", "description": "Peaceful and relaxing"},
            {"id": "energetic", "name": "Energetic", "description": "High energy and motivating"},
            {"id": "dramatic", "name": "Dramatic", "description": "Intense and emotional"},
            {"id": "upbeat", "name": "Upbeat", "description": "Fun and lighthearted"},
            {"id": "mysterious", "name": "Mysterious", "description": "Dark and intriguing"},
            {"id": "romantic", "name": "Romantic", "description": "Love and tender emotions"},
            {"id": "melancholic", "name": "Melancholic", "description": "Sad and reflective"},
            {"id": "triumphant", "name": "Triumphant", "description": "Victory and achievement"},
            {"id": "playful", "name": "Playful", "description": "Fun and lighthearted"},
            {"id": "suspenseful", "name": "Suspenseful", "description": "Tension and anticipation"},
            {"id": "nostalgic", "name": "Nostalgic", "description": "Reminiscent and wistful"},
            {"id": "meditative", "name": "Meditative", "description": "Contemplative and zen"},
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
        
        response = {
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

@app.route('/api/advanced-generate', methods=['POST'])
def advanced_generate():
    try:
        print("Advanced generate request received", file=sys.stderr)
        data = request.get_json() or {}
        print(f"Advanced generate data: {data}", file=sys.stderr)
        
        # Extract advanced parameters
        prompt = data.get('prompt', '')
        duration = data.get('duration', 60)
        tempo = data.get('tempo', 120)
        key = data.get('key', 'C')
        genre = data.get('genre', 'electronic')
        mood = data.get('mood', 'energetic')
        instruments = data.get('instruments', [])
        effects = data.get('effects', [])
        structure = data.get('structure', 'verse-chorus-verse-chorus')
        
        if not prompt.strip():
            return jsonify({
                "success": False,
                "error": "Prompt is required"
            }), 400
        
        # Simulate advanced music generation
        response = {
            "success": True,
            "track": {
                "id": "adv_track_12345",
                "title": f"Advanced Track - {prompt[:30]}...",
                "prompt": prompt,
                "duration": duration,
                "tempo": tempo,
                "key": key,
                "genre": genre,
                "mood": mood,
                "instruments": instruments,
                "effects": effects,
                "structure": structure,
                "url": "https://example.com/advanced-generated-music.mp3",
                "download_url": "https://example.com/advanced-generated-music.wav",
                "waveform_data": [0.2, 0.8, 0.4, 0.9, 0.3, 0.7, 0.6, 0.5],
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
        print(f"Advanced generate response: {response}", file=sys.stderr)
        return jsonify(response)
    
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
    port = int(os.environ.get('PORT', 5002))
    print(f"🚀 Starting Flask server on port {port}...")
    print(f"📍 Health check available at: http://localhost:{port}/health")
    print(f"📡 API endpoints available at: http://localhost:{port}/api/")
    print(f"🔧 CORS enabled for: {', '.join(frontend_urls)}")
    
    app.run(host='0.0.0.0', port=port, debug=True)
