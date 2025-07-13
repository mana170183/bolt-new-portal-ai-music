from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import traceback
from datetime import datetime
import uuid
import tempfile
import mimetypes
import math
import struct
import random
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create output directory for generated audio
AUDIO_OUTPUT_DIR = '/tmp/generated_audio'
if not os.path.exists(AUDIO_OUTPUT_DIR):
    os.makedirs(AUDIO_OUTPUT_DIR)

def generate_simple_audio(duration=30, genre='pop', mood='upbeat'):
    """Generate simple audio based on parameters and return as WAV bytes"""
    try:
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        # Base frequency based on genre
        genre_freqs = {
            'pop': 440,
            'rock': 329,
            'jazz': 369,
            'classical': 523,
            'electronic': 262,
            'hip-hop': 196,
            'ambient': 220,
            'cinematic': 246,
            'corporate': 392,
            'folk': 293
        }
        
        base_freq = genre_freqs.get(genre, 440)
        
        # Generate audio samples
        audio_data = []
        for i in range(num_samples):
            t = i / sample_rate
            
            # Simple envelope (fade out)
            envelope = max(0, 1 - t / duration) * 0.5
            
            # Create harmonics for richer sound
            freq1 = base_freq * (1 + 0.05 * math.sin(t * 2))  # Slight modulation
            freq2 = base_freq * 1.5  # Perfect fifth
            freq3 = base_freq * 2    # Octave
            
            sample = envelope * (
                0.6 * math.sin(2 * math.pi * freq1 * t) +
                0.3 * math.sin(2 * math.pi * freq2 * t) +
                0.1 * math.sin(2 * math.pi * freq3 * t)
            )
            
            # Mood adjustments
            if mood == 'upbeat':
                sample *= (1 + 0.1 * math.sin(t * 8))
            elif mood == 'melancholic':
                sample *= (1 - 0.1 * math.sin(t * 2))
            elif mood == 'energetic':
                sample *= (1 + 0.2 * math.sin(t * 12))
            elif mood == 'calm':
                sample *= 0.7
            
            audio_data.append(sample)
        
        # Convert to WAV file
        wav_bytes = create_wav_file(audio_data, sample_rate)
        return wav_bytes
        
    except Exception as e:
        logger.error(f"Error generating simple audio: {str(e)}")
        raise

def create_wav_file(audio_data, sample_rate):
    """Create a WAV file from audio data"""
    # Convert to 16-bit PCM
    audio_16bit = []
    for sample in audio_data:
        # Clamp and convert to 16-bit signed integer
        sample_clamped = max(-1, min(1, sample))
        sample_16bit = int(sample_clamped * 32767)
        audio_16bit.append(sample_16bit)
    
    # Create WAV header
    num_samples = len(audio_16bit)
    bytes_per_sample = 2
    num_channels = 1
    byte_rate = sample_rate * num_channels * bytes_per_sample
    block_align = num_channels * bytes_per_sample
    data_size = num_samples * bytes_per_sample
    
    # WAV file header
    header = bytearray()
    header.extend(b'RIFF')
    header.extend(struct.pack('<I', 36 + data_size))
    header.extend(b'WAVE')
    header.extend(b'fmt ')
    header.extend(struct.pack('<I', 16))  # PCM format chunk size
    header.extend(struct.pack('<H', 1))   # PCM format
    header.extend(struct.pack('<H', num_channels))
    header.extend(struct.pack('<I', sample_rate))
    header.extend(struct.pack('<I', byte_rate))
    header.extend(struct.pack('<H', block_align))
    header.extend(struct.pack('<H', 16))  # Bits per sample
    header.extend(b'data')
    header.extend(struct.pack('<I', data_size))
    
    # Add audio data
    for sample in audio_16bit:
        header.extend(struct.pack('<h', sample))
    
    return bytes(header)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = self.path
            
            if path == '/api/health':
                self.handle_health()
            elif path == '/api/genres':
                self.handle_genres()
            elif path == '/api/moods':
                self.handle_moods()
            elif path.startswith('/api/stream/'):
                filename = path.split('/')[-1]
                self.handle_stream(filename)
            elif path.startswith('/api/download/'):
                filename = path.split('/')[-1]
                self.handle_download(filename)
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"GET error: {str(e)}")
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            path = self.path
            
            if path == '/api/generate-music':
                self.handle_generate_music()
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"POST error: {str(e)}")
            self.send_error(500, str(e))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Expose-Headers', 'Accept-Ranges, Content-Range, Content-Length')
    
    def handle_health(self):
        """Handle health check"""
        health_status = {
            "status": "healthy",
            "message": "AI Music Portal Backend is running",
            "enhanced_generator": False,
            "database_available": False,
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = json.dumps(health_status)
        self.wfile.write(response.encode())
    
    def handle_genres(self):
        """Handle genres endpoint"""
        genres = [
            {"id": "pop", "name": "Pop", "description": "Popular mainstream music"},
            {"id": "rock", "name": "Rock", "description": "Rock and alternative music"},
            {"id": "jazz", "name": "Jazz", "description": "Jazz and swing music"},
            {"id": "classical", "name": "Classical", "description": "Classical orchestral music"},
            {"id": "electronic", "name": "Electronic", "description": "Electronic and synth music"},
            {"id": "hip-hop", "name": "Hip-Hop", "description": "Hip-hop and rap music"},
            {"id": "ambient", "name": "Ambient", "description": "Atmospheric and ambient music"},
            {"id": "cinematic", "name": "Cinematic", "description": "Epic orchestral and dramatic music"},
            {"id": "corporate", "name": "Corporate", "description": "Professional business-friendly music"},
            {"id": "folk", "name": "Folk", "description": "Traditional and acoustic folk music"}
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = json.dumps({"success": True, "genres": genres})
        self.wfile.write(response.encode())
    
    def handle_moods(self):
        """Handle moods endpoint"""
        moods = [
            {"id": "upbeat", "name": "Upbeat", "description": "Energetic and positive"},
            {"id": "calm", "name": "Calm", "description": "Peaceful and relaxing"},
            {"id": "melancholic", "name": "Melancholic", "description": "Sad and contemplative"},
            {"id": "energetic", "name": "Energetic", "description": "High-energy and exciting"},
            {"id": "mysterious", "name": "Mysterious", "description": "Dark and intriguing"},
            {"id": "romantic", "name": "Romantic", "description": "Love and affection"},
            {"id": "triumphant", "name": "Triumphant", "description": "Victorious and celebratory"},
            {"id": "nostalgic", "name": "Nostalgic", "description": "Memories and longing"}
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = json.dumps({"success": True, "moods": moods})
        self.wfile.write(response.encode())
    
    def handle_generate_music(self):
        """Handle music generation"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)
            else:
                data = {}
            
            # Extract parameters
            duration = min(max(int(data.get('duration', 10)), 5), 30)  # Limit to 5-30 seconds
            genre = data.get('genre', 'pop')
            mood = data.get('mood', 'upbeat')
            prompt = data.get('prompt', f'{mood} {genre} music')
            
            logger.info(f"Generating music: duration={duration}, genre={genre}, mood={mood}")
            
            # Generate audio
            audio_data = generate_simple_audio(duration, genre, mood)
            
            # Create a unique filename
            filename = f"music_{uuid.uuid4().hex[:8]}.wav"
            filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
            
            # Save the audio file
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Generated audio saved to: {filepath}")
            
            # Response in the expected format
            response_data = {
                "success": True,
                "message": "Music generated successfully",
                "audio_file": filename,
                "download_url": f"/api/download/{filename}",
                "stream_url": f"/api/stream/{filename}",
                "metadata": {
                    "prompt": prompt,
                    "duration": duration,
                    "genre": genre,
                    "mood": mood,
                    "filename": filename,
                    "sample_rate": 44100,
                    "format": "wav"
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = json.dumps(response_data)
            self.wfile.write(response.encode())
            
        except Exception as e:
            logger.error(f"Error generating music: {str(e)}")
            
            # Send error response
            error_response = {
                "success": False,
                "error": str(e),
                "message": "Music generation failed"
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = json.dumps(error_response)
            self.wfile.write(response.encode())
    
    def handle_stream(self, filename):
        """Handle audio streaming"""
        try:
            filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
            if not os.path.exists(filepath):
                self.send_error(404, "File not found")
                return
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Determine MIME type
            mime_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Content-Length', str(file_size))
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Cache-Control', 'public, max-age=31536000')
            self.send_cors_headers()
            self.end_headers()
            
            # Stream the file
            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
                
        except Exception as e:
            logger.error(f"Error streaming audio: {str(e)}")
            self.send_error(500, str(e))
    
    def handle_download(self, filename):
        """Handle audio download"""
        try:
            filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
            if not os.path.exists(filepath):
                self.send_error(404, "File not found")
                return
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Determine MIME type
            mime_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.send_header('Content-Length', str(file_size))
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Cache-Control', 'public, max-age=31536000')
            self.send_cors_headers()
            self.end_headers()
            
            # Stream the file
            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
                
        except Exception as e:
            logger.error(f"Error downloading audio: {str(e)}")
            self.send_error(500, str(e))