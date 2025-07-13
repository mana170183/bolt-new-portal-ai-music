from http.server import BaseHTTPRequestHandler
import json
import uuid
import math
import struct
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            'cinematic': 246
        }
        
        base_freq = genre_freqs.get(genre, 440)
        
        # Generate audio samples
        audio_data = []
        for i in range(num_samples):
            t = i / sample_rate
            
            # Simple envelope (fade out)
            envelope = max(0, 1 - t / duration) * 0.5
            
            # Create harmonics for richer sound
            freq1 = base_freq * (1 + 0.05 * math.sin(t * 2))
            freq2 = base_freq * 1.5
            freq3 = base_freq * 2
            
            sample = envelope * (
                0.6 * math.sin(2 * math.pi * freq1 * t) +
                0.3 * math.sin(2 * math.pi * freq2 * t) +
                0.1 * math.sin(2 * math.pi * freq3 * t)
            )
            
            # Mood adjustments
            if mood == 'upbeat':
                sample *= (1 + 0.1 * math.sin(t * 8))
            elif mood == 'calm':
                sample *= 0.7
            elif mood == 'energetic':
                sample *= (1 + 0.2 * math.sin(t * 12))
            
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
    header.extend(struct.pack('<I', 16))
    header.extend(struct.pack('<H', 1))
    header.extend(struct.pack('<H', num_channels))
    header.extend(struct.pack('<I', sample_rate))
    header.extend(struct.pack('<I', byte_rate))
    header.extend(struct.pack('<H', block_align))
    header.extend(struct.pack('<H', 16))
    header.extend(b'data')
    header.extend(struct.pack('<I', data_size))
    
    # Add audio data
    for sample in audio_16bit:
        header.extend(struct.pack('<h', sample))
    
    return bytes(header)

import base64

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)
            else:
                data = {}
            
            # Extract parameters
            duration = min(max(int(data.get('duration', 10)), 5), 30)
            genre = data.get('genre', 'pop')
            mood = data.get('mood', 'upbeat')
            prompt = data.get('prompt', f'{mood} {genre} music')
            
            # Generate audio
            audio_data = generate_simple_audio(duration, genre, mood)
            
            # Convert to base64 for JSON response
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Create filename
            filename = f"music_{uuid.uuid4().hex[:8]}.wav"
            
            # Response
            response_data = {
                "success": True,
                "message": "Music generated successfully",
                "audio_file": filename,
                "audio_data": audio_base64,
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
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
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
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
            self.end_headers()
            
            response = json.dumps(error_response)
            self.wfile.write(response.encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.end_headers()
