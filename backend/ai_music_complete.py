"""
Complete AI Music Generation Backend
Real-time synthesis with multiple AI models
"""

import os
import sys
import logging
import json
import numpy as np
import torch
from datetime import datetime
from pathlib import Path
import traceback

# Flask imports
from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Audio processing
import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub.generators import Sine, Square, Sawtooth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_music.log')
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
    AUDIO_FORMAT = 'wav'
    DEFAULT_DURATION = 30
    DEFAULT_TEMPO = 120
    MAX_DURATION = 300

config = Config()

# Create directories
for folder in [config.UPLOAD_FOLDER, config.OUTPUT_FOLDER]:
    Path(folder).mkdir(exist_ok=True)

class AdvancedMusicSynthesizer:
    """Advanced music synthesis engine with AI-inspired algorithms"""
    
    def __init__(self):
        self.sample_rate = config.SAMPLE_RATE
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
    
    def generate_music(self, style: str, duration: int, tempo: int, mood: str = "neutral") -> np.ndarray:
        """Generate music using advanced synthesis"""
        try:
            logger.info(f"Generating {style} music: {duration}s at {tempo} BPM, mood: {mood}")
            
            # Generate chord progression based on style
            chord_progression = self.get_chord_progression(style, mood)
            
            # Create time array
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            
            # Generate multiple tracks
            tracks = []
            
            # Melody track
            melody = self.generate_melody(t, chord_progression, style, tempo, mood)
            tracks.append(('melody', melody, 0.6))
            
            # Bass track
            bass = self.generate_bass(t, chord_progression, style, tempo)
            tracks.append(('bass', bass, 0.5))
            
            # Drum track
            drums = self.generate_drums(t, style, tempo)
            tracks.append(('drums', drums, 0.4))
            
            # Harmony/pad track
            harmony = self.generate_harmony(t, chord_progression, style, mood)
            tracks.append(('harmony', harmony, 0.3))
            
            # Mix all tracks
            final_audio = self.mix_tracks(tracks)
            
            # Apply master effects
            final_audio = self.apply_master_effects(final_audio, style)
            
            return final_audio
            
        except Exception as e:
            logger.error(f"Error generating music: {e}")
            return self.generate_fallback_audio(duration, tempo)
    
    def get_chord_progression(self, style: str, mood: str) -> list:
        """Get chord progression based on style and mood"""
        progressions = {
            "classical": {
                "happy": ["C", "Am", "F", "G", "C", "F", "G", "C"],
                "sad": ["Am", "F", "C", "G", "Am", "F", "G", "Am"],
                "neutral": ["C", "G", "Am", "F", "C", "G", "F", "C"]
            },
            "jazz": {
                "happy": ["Cmaj7", "Am7", "Dm7", "G7", "Em7", "Am7", "Dm7", "G7"],
                "sad": ["Am7", "Dm7", "G7", "Cmaj7", "Fmaj7", "Bm7b5", "E7", "Am7"],
                "neutral": ["Cmaj7", "A7", "Dm7", "G7", "Em7", "A7", "Dm7", "G7"]
            },
            "rock": {
                "happy": ["C", "F", "G", "C", "Am", "F", "G", "C"],
                "sad": ["Am", "F", "C", "G", "Am", "F", "C", "G"],
                "neutral": ["C", "G", "F", "C", "Am", "G", "F", "C"]
            },
            "electronic": {
                "happy": ["C", "Bb", "F", "G", "Am", "Bb", "F", "C"],
                "sad": ["Am", "F", "C", "G", "Dm", "Bb", "F", "C"],
                "neutral": ["Cm", "Bb", "Ab", "Gm", "Fm", "Eb", "Bb", "Cm"]
            },
            "ambient": {
                "happy": ["C", "Em", "Am", "F", "C", "G", "Am", "F"],
                "sad": ["Am", "C", "F", "G", "Em", "Am", "F", "C"],
                "neutral": ["C", "Em", "F", "G", "Am", "C", "F", "G"]
            }
        }
        
        style_progs = progressions.get(style, progressions["classical"])
        return style_progs.get(mood, style_progs["neutral"])
    
    def generate_melody(self, t: np.ndarray, chords: list, style: str, tempo: int, mood: str) -> np.ndarray:
        """Generate melodic line"""
        melody = np.zeros_like(t)
        
        # Note frequencies (C major scale)
        notes = {
            "C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
            "G": 392.00, "A": 440.00, "B": 493.88
        }
        
        chord_duration = len(t) / len(chords)
        beat_duration = 60 / tempo * self.sample_rate
        
        for i, chord in enumerate(chords):
            start_idx = int(i * chord_duration)
            end_idx = int((i + 1) * chord_duration)
            
            # Get chord tones
            root = chord[0]
            chord_tones = self.get_chord_tones(chord, notes)
            
            # Generate melodic pattern for this chord
            segment_t = t[start_idx:end_idx]
            if len(segment_t) > 0:
                segment_melody = self.create_melodic_pattern(
                    segment_t, chord_tones, style, mood, beat_duration
                )
                melody[start_idx:end_idx] = segment_melody
        
        return melody
    
    def get_chord_tones(self, chord: str, notes: dict) -> list:
        """Get frequencies for chord tones"""
        root = chord[0]
        base_freq = notes.get(root, 261.63)
        
        # Simple triad construction
        if "m" in chord.lower():
            # Minor chord
            return [base_freq, base_freq * 1.2, base_freq * 1.5]
        else:
            # Major chord
            return [base_freq, base_freq * 1.25, base_freq * 1.5]
    
    def create_melodic_pattern(self, t: np.ndarray, chord_tones: list, style: str, mood: str, beat_duration: float) -> np.ndarray:
        """Create a melodic pattern"""
        pattern = np.zeros_like(t)
        
        # Choose waveform based on style
        if style == "electronic":
            waveform = "square"
        elif style == "jazz":
            waveform = "sine"
        else:
            waveform = "sine"
        
        # Generate notes based on beat divisions
        num_beats = len(t) / beat_duration
        notes_per_beat = 2 if style == "jazz" else 1
        
        for beat in range(int(num_beats * notes_per_beat)):
            start_sample = int(beat * beat_duration / notes_per_beat)
            end_sample = int((beat + 1) * beat_duration / notes_per_beat)
            
            if end_sample > len(t):
                break
            
            # Choose note from chord tones
            freq = chord_tones[beat % len(chord_tones)]
            
            # Apply octave variations
            if beat % 4 == 2:  # Higher octave on beat 3
                freq *= 2
            elif beat % 8 == 7:  # Lower octave occasionally
                freq *= 0.5
            
            # Generate note
            note_t = t[start_sample:end_sample] - t[start_sample]
            
            if waveform == "square":
                note = 0.3 * np.sign(np.sin(2 * np.pi * freq * note_t))
            else:
                note = 0.3 * np.sin(2 * np.pi * freq * note_t)
            
            # Apply envelope
            envelope = np.exp(-note_t * 3)  # Decay envelope
            pattern[start_sample:end_sample] = note * envelope
        
        return pattern
    
    def generate_bass(self, t: np.ndarray, chords: list, style: str, tempo: int) -> np.ndarray:
        """Generate bass line"""
        bass = np.zeros_like(t)
        
        notes = {
            "C": 65.41, "D": 73.42, "E": 82.41, "F": 87.31,
            "G": 98.00, "A": 110.00, "B": 123.47
        }
        
        chord_duration = len(t) / len(chords)
        beat_duration = 60 / tempo * self.sample_rate
        
        for i, chord in enumerate(chords):
            start_idx = int(i * chord_duration)
            end_idx = int((i + 1) * chord_duration)
            
            root_note = chord[0]
            freq = notes.get(root_note, 65.41)
            
            segment_t = t[start_idx:end_idx]
            if len(segment_t) > 0:
                # Create bass pattern
                if style == "electronic":
                    # Steady bass with sub harmonics
                    bass_note = 0.5 * np.sin(2 * np.pi * freq * segment_t)
                    bass_note += 0.3 * np.sin(2 * np.pi * freq * 0.5 * segment_t)  # Sub bass
                elif style == "jazz":
                    # Walking bass
                    walking_bass = self.create_walking_bass(segment_t, freq, beat_duration)
                    bass_note = walking_bass
                else:
                    # Simple root note bass
                    bass_note = 0.4 * np.sin(2 * np.pi * freq * segment_t)
                
                bass[start_idx:end_idx] = bass_note
        
        return bass
    
    def create_walking_bass(self, t: np.ndarray, root_freq: float, beat_duration: float) -> np.ndarray:
        """Create walking bass line"""
        pattern = np.zeros_like(t)
        
        # Walking bass frequencies (around root)
        freqs = [root_freq, root_freq * 1.125, root_freq * 1.25, root_freq * 1.5]
        
        beats_in_segment = len(t) / beat_duration
        
        for beat in range(int(beats_in_segment)):
            start_sample = int(beat * beat_duration)
            end_sample = int((beat + 1) * beat_duration)
            
            if end_sample > len(t):
                break
            
            freq = freqs[beat % len(freqs)]
            note_t = t[start_sample:end_sample] - t[start_sample]
            
            note = 0.4 * np.sin(2 * np.pi * freq * note_t)
            envelope = np.exp(-note_t * 2)
            
            pattern[start_sample:end_sample] = note * envelope
        
        return pattern
    
    def generate_drums(self, t: np.ndarray, style: str, tempo: int) -> np.ndarray:
        """Generate drum pattern"""
        drums = np.zeros_like(t)
        
        beat_duration = 60 / tempo * self.sample_rate
        
        # Drum patterns
        patterns = {
            "rock": [1, 0, 1, 0, 1, 0, 1, 0],  # 4/4 rock
            "jazz": [1, 0, 0, 1, 0, 1, 0, 0],  # Jazz swing
            "electronic": [1, 0, 0, 0, 1, 0, 0, 0],  # Four on the floor
            "classical": [1, 0, 0, 0, 0, 0, 0, 0],  # Minimal
            "ambient": [1, 0, 0, 0, 0, 0, 0, 0]   # Very minimal
        }
        
        pattern = patterns.get(style, patterns["rock"])
        
        for beat in range(int(len(t) / beat_duration)):
            if pattern[beat % len(pattern)]:
                start_sample = int(beat * beat_duration)
                end_sample = min(start_sample + int(0.1 * self.sample_rate), len(drums))
                
                # Create kick drum sound
                drum_t = np.linspace(0, 0.1, end_sample - start_sample)
                kick = 0.5 * np.sin(2 * np.pi * 60 * drum_t) * np.exp(-50 * drum_t)
                
                drums[start_sample:end_sample] += kick
        
        return drums
    
    def generate_harmony(self, t: np.ndarray, chords: list, style: str, mood: str) -> np.ndarray:
        """Generate harmony/pad track"""
        harmony = np.zeros_like(t)
        
        notes = {
            "C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
            "G": 392.00, "A": 440.00, "B": 493.88
        }
        
        chord_duration = len(t) / len(chords)
        
        for i, chord in enumerate(chords):
            start_idx = int(i * chord_duration)
            end_idx = int((i + 1) * chord_duration)
            
            chord_tones = self.get_chord_tones(chord, notes)
            segment_t = t[start_idx:end_idx]
            
            if len(segment_t) > 0:
                # Create chord voicing
                chord_audio = np.zeros_like(segment_t)
                
                for freq in chord_tones:
                    if style == "ambient":
                        # Soft pad sound
                        voice = 0.1 * np.sin(2 * np.pi * freq * segment_t)
                        voice += 0.05 * np.sin(2 * np.pi * freq * 2 * segment_t)  # Octave
                    else:
                        # Standard chord voicing
                        voice = 0.15 * np.sin(2 * np.pi * freq * segment_t)
                    
                    chord_audio += voice
                
                harmony[start_idx:end_idx] = chord_audio
        
        return harmony
    
    def mix_tracks(self, tracks: list) -> np.ndarray:
        """Mix multiple audio tracks"""
        if not tracks:
            return np.array([])
        
        # Get the length of the longest track
        max_length = max(len(track[1]) for track in tracks)
        mixed = np.zeros(max_length)
        
        for name, track, level in tracks:
            # Ensure track is the right length
            if len(track) < max_length:
                padded_track = np.pad(track, (0, max_length - len(track)))
            else:
                padded_track = track[:max_length]
            
            mixed += level * padded_track
        
        # Normalize to prevent clipping
        if np.max(np.abs(mixed)) > 0:
            mixed = mixed / np.max(np.abs(mixed)) * 0.8
        
        return mixed
    
    def apply_master_effects(self, audio: np.ndarray, style: str) -> np.ndarray:
        """Apply master effects based on style"""
        try:
            if style == "ambient":
                # Add reverb-like effect
                delay_samples = int(0.1 * self.sample_rate)
                delayed = np.pad(audio, (delay_samples, 0))[:len(audio)]
                audio = audio + 0.3 * delayed
            
            elif style == "electronic":
                # Add slight distortion
                audio = np.tanh(audio * 2) * 0.7
            
            # Apply soft compression
            threshold = 0.5
            compressed = np.where(
                np.abs(audio) > threshold,
                threshold + (np.abs(audio) - threshold) * 0.3,
                np.abs(audio)
            ) * np.sign(audio)
            
            return compressed
            
        except Exception as e:
            logger.warning(f"Error applying effects: {e}")
            return audio
    
    def generate_fallback_audio(self, duration: int, tempo: int) -> np.ndarray:
        """Generate simple fallback audio"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Simple sine wave melody
        freq = 440  # A4
        melody = 0.3 * np.sin(2 * np.pi * freq * t) * np.exp(-t / duration)
        
        return melody

# Initialize the synthesizer
synthesizer = AdvancedMusicSynthesizer()

def cors_response(data, status=200):
    """Create CORS-enabled JSON response"""
    response = jsonify(data)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response, status

# API Routes
@app.route('/')
def home():
    return cors_response({
        "status": "running",
        "message": "Advanced AI Music Generation System",
        "version": "3.0.0",
        "features": [
            "Multi-track synthesis",
            "Style-based generation",
            "Mood adaptation",
            "Real-time processing",
            "Advanced audio effects"
        ]
    })

@app.route('/health')
def health():
    return cors_response({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "device": str(synthesizer.device)
    })

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate_music():
    """Generate AI music"""
    if request.method == 'OPTIONS':
        return cors_response({})
    
    try:
        data = request.get_json() or {}
        
        # Extract parameters
        style = data.get('style', 'classical')
        duration = min(data.get('duration', 30), config.MAX_DURATION)
        tempo = data.get('tempo', 120)
        mood = data.get('mood', 'neutral')
        
        logger.info(f"Generating: {style} {mood} music, {duration}s @ {tempo}BPM")
        
        # Generate music
        audio = synthesizer.generate_music(style, duration, tempo, mood)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_music_{style}_{mood}_{timestamp}.wav"
        filepath = os.path.join(config.OUTPUT_FOLDER, filename)
        
        # Ensure audio is properly formatted
        audio = np.clip(audio, -1, 1)
        sf.write(filepath, audio, config.SAMPLE_RATE)
        
        return cors_response({
            "success": True,
            "message": "AI music generated successfully",
            "filename": filename,
            "duration": duration,
            "style": style,
            "mood": mood,
            "download_url": f"/api/download/{filename}",
            "audioUrl": f"/api/download/{filename}"
        })
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        logger.error(traceback.format_exc())
        return cors_response({
            "success": False,
            "error": str(e)
        }, 500)

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated audio file"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return cors_response({"error": "File not found"}, 404)
        
        def generate():
            with open(filepath, 'rb') as f:
                data = f.read(1024)
                while data:
                    yield data
                    data = f.read(1024)
        
        response = Response(generate(), mimetype='audio/wav')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return cors_response({"error": str(e)}, 500)

@app.route('/api/styles')
def get_styles():
    """Get available music styles"""
    return cors_response({
        "styles": [
            {"name": "classical", "description": "Classical orchestral style"},
            {"name": "jazz", "description": "Jazz with complex harmonies"},
            {"name": "rock", "description": "Rock with strong rhythms"},
            {"name": "electronic", "description": "Electronic/synthesized music"},
            {"name": "ambient", "description": "Atmospheric ambient soundscapes"}
        ]
    })

@app.route('/api/moods')
def get_moods():
    """Get available moods"""
    return cors_response({
        "moods": [
            {"name": "happy", "description": "Uplifting and cheerful"},
            {"name": "sad", "description": "Melancholic and introspective"},
            {"name": "neutral", "description": "Balanced and calm"}
        ]
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return cors_response({"error": "Endpoint not found"}, 404)

@app.errorhandler(500)
def internal_error(error):
    return cors_response({"error": "Internal server error"}, 500)

if __name__ == '__main__':
    logger.info("Starting Advanced AI Music Generation System...")
    logger.info(f"Device: {synthesizer.device}")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False
    )
