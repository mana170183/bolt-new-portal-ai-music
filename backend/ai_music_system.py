"""
Advanced AI Music Generation System
Real-time music generation with AI models and synthesis
"""

import os
import sys
import logging
import json
import numpy as np
import torch
from datetime import datetime
from pathlib import Path
import threading
import time

# Flask imports
from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Audio processing
try:
    import librosa
    import soundfile as sf
    from pydub import AudioSegment
    AUDIO_LIBS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Audio libraries not available: {e}")
    AUDIO_LIBS_AVAILABLE = False

# AI/ML imports
try:
    from transformers import AutoModel
    AI_LIBS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AI libraries not available: {e}")
    AI_LIBS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_music_generator.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# Configuration
class Config:
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'generated_audio'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SAMPLE_RATE = 44100
    DEFAULT_DURATION = 30
    MAX_DURATION = 300

config = Config()

# Create directories
for folder in [config.UPLOAD_FOLDER, config.OUTPUT_FOLDER, 'models']:
    Path(folder).mkdir(exist_ok=True)

class AIMusicGenerator:
    """AI Music Generation Engine"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        self.models_loaded = False
        
    def generate_melody(self, style="classical", duration=30, tempo=120):
        """Generate a melodic sequence"""
        if not AUDIO_LIBS_AVAILABLE:
            return self.generate_simple_tone(duration)
            
        try:
            sample_rate = config.SAMPLE_RATE
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Generate chord progression
            chord_progression = self.get_chord_progression(style)
            melody = np.zeros_like(t)
            
            # Generate melody based on style
            for i, chord in enumerate(chord_progression):
                start_time = i * (duration / len(chord_progression))
                end_time = (i + 1) * (duration / len(chord_progression))
                
                segment_mask = (t >= start_time) & (t < end_time)
                segment_t = t[segment_mask]
                
                if len(segment_t) > 0:
                    chord_melody = self.generate_chord_melody(chord, segment_t, tempo, style)
                    melody[segment_mask] = chord_melody
            
            return self.apply_envelope(melody)
            
        except Exception as e:
            logger.error(f"Error generating melody: {e}")
            return self.generate_simple_tone(duration)
    
    def get_chord_progression(self, style):
        """Get chord progression for style"""
        progressions = {
            "classical": ["C", "Am", "F", "G"],
            "jazz": ["Cmaj7", "Am7", "Dm7", "G7"],
            "rock": ["C", "F", "G", "C"],
            "blues": ["C7", "F7", "C7", "G7"],
            "electronic": ["Cm", "Bb", "Ab", "Gm"],
            "ambient": ["C", "Em", "Am", "F"]
        }
        return progressions.get(style, progressions["classical"])
    
    def generate_chord_melody(self, chord, t, tempo, style):
        """Generate melody for a chord"""
        # Basic chord frequencies
        chord_freqs = {
            "C": [261.63, 329.63, 392.00],
            "Am": [220.00, 261.63, 329.63],
            "F": [174.61, 220.00, 261.63],
            "G": [196.00, 246.94, 293.66],
            "Em": [164.81, 196.00, 246.94],
            "Dm": [146.83, 174.61, 220.00]
        }
        
        base_chord = chord.replace("maj7", "").replace("m7", "m").replace("7", "")
        freqs = chord_freqs.get(base_chord, chord_freqs["C"])
        
        melody = np.zeros_like(t)
        for i, freq in enumerate(freqs):
            wave = 0.3 * np.sin(2 * np.pi * freq * t + i * np.pi/3)
            melody += wave
        
        return melody
    
    def apply_envelope(self, audio):
        """Apply ADSR envelope"""
        length = len(audio)
        envelope = np.ones(length)
        
        # Attack (5%)
        attack_len = int(0.05 * length)
        envelope[:attack_len] = np.linspace(0, 1, attack_len)
        
        # Release (15%)
        release_len = int(0.15 * length)
        envelope[-release_len:] = np.linspace(1, 0, release_len)
        
        return audio * envelope
    
    def generate_simple_tone(self, duration):
        """Fallback simple tone generation"""
        sample_rate = config.SAMPLE_RATE
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Simple major scale melody
        frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        melody = np.zeros_like(t)
        
        note_duration = duration / len(frequencies)
        for i, freq in enumerate(frequencies):
            start_idx = int(i * note_duration * sample_rate)
            end_idx = int((i + 1) * note_duration * sample_rate)
            
            if end_idx <= len(t):
                note_t = t[start_idx:end_idx] - t[start_idx]
                note = 0.3 * np.sin(2 * np.pi * freq * note_t) * np.exp(-2 * note_t / note_duration)
                melody[start_idx:end_idx] = note
        
        return melody

# Initialize generator
ai_generator = AIMusicGenerator()

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "Advanced AI Music Generation System",
        "version": "2.0.0",
        "features": [
            "AI Melody Generation",
            "Multiple Music Styles",
            "Real-time Synthesis",
            "Audio Export"
        ],
        "libraries": {
            "audio": AUDIO_LIBS_AVAILABLE,
            "ai": AI_LIBS_AVAILABLE
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "device": str(ai_generator.device),
        "audio_libs": AUDIO_LIBS_AVAILABLE,
        "ai_libs": AI_LIBS_AVAILABLE
    })

@app.route('/api/generate', methods=['POST'])
def generate_music():
    """Generate AI music"""
    try:
        data = request.get_json() or {}
        
        style = data.get('style', 'classical')
        duration = min(data.get('duration', 30), config.MAX_DURATION)
        tempo = data.get('tempo', 120)
        
        logger.info(f"Generating music: {style}, {duration}s, {tempo}BPM")
        
        # Generate melody
        melody = ai_generator.generate_melody(style, duration, tempo)
        
        # Save audio file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{style}_{timestamp}.wav"
        filepath = os.path.join(config.OUTPUT_FOLDER, filename)
        
        # Save audio
        melody = np.clip(melody, -1, 1)
        
        if AUDIO_LIBS_AVAILABLE:
            sf.write(filepath, melody, config.SAMPLE_RATE)
        else:
            # Fallback: save as numpy array
            np.save(filepath.replace('.wav', '.npy'), melody)
            filename = filename.replace('.wav', '.npy')
        
        return jsonify({
            "success": True,
            "message": "Music generated successfully",
            "filename": filename,
            "duration": duration,
            "style": style,
            "download_url": f"/api/download/{filename}"
        })
        
    except Exception as e:
        logger.error(f"Error generating music: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated file"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/styles')
def get_styles():
    """Get available music styles"""
    return jsonify({
        "styles": [
            {"name": "classical", "description": "Classical music"},
            {"name": "jazz", "description": "Jazz with complex chords"},
            {"name": "rock", "description": "Rock music"},
            {"name": "blues", "description": "Blues progression"},
            {"name": "electronic", "description": "Electronic music"},
            {"name": "ambient", "description": "Ambient soundscapes"}
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Advanced AI Music Generation System...")
    logger.info(f"Device: {ai_generator.device}")
    logger.info(f"Audio libraries: {AUDIO_LIBS_AVAILABLE}")
    logger.info(f"AI libraries: {AI_LIBS_AVAILABLE}")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False
    )
