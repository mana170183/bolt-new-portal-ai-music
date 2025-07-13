"""
Advanced AI Music Generation Core System
Multi-instrumental composition with neural network architecture
Enhanced with vocal synthesis and expanded instrument support
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import librosa
import pretty_midi
import mido
from scipy import signal
import json
import os
import threading
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MusicGenerationRequest:
    """Data structure for music generation requests"""
    lyrics: str
    genre: str
    mood: str
    tempo_bpm: int
    duration: float
    instruments: List[str]
    key: str = "C"
    time_signature: str = "4/4"
    style_complexity: str = "moderate"
    enable_stems: bool = True
    export_formats: List[str] = None
    vocal_style: str = "auto"  # NEW: vocal style selection
    vocal_gender: str = "auto"  # NEW: vocal gender preference

    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["wav", "midi"]

@dataclass
class InstrumentTrack:
    """Individual instrument track data"""
    instrument_name: str
    midi_data: np.ndarray
    audio_data: np.ndarray
    volume: float
    pan: float
    effects: Dict[str, Any]

class MelodyGeneratorNN(nn.Module):
    """Neural network for melody generation using LSTM and attention"""
    
    def __init__(self, vocab_size=128, embedding_dim=256, hidden_dim=512, num_layers=3):
        super(MelodyGeneratorNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True, dropout=0.3)
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=8)
        self.output_layer = nn.Linear(hidden_dim, vocab_size)
        self.dropout = nn.Dropout(0.3)
        
    def forward(self, x, hidden=None):
        embedded = self.embedding(x)
        lstm_out, hidden = self.lstm(embedded, hidden)
        
        # Apply attention mechanism
        attended, _ = self.attention(lstm_out, lstm_out, lstm_out)
        attended = self.dropout(attended)
        
        output = self.output_layer(attended)
        return output, hidden

class HarmonyGeneratorNN(nn.Module):
    """Neural network for harmony and chord progression generation"""
    
    def __init__(self, melody_dim=128, chord_vocab=200, hidden_dim=384):
        super(HarmonyGeneratorNN, self).__init__()
        self.melody_encoder = nn.Linear(melody_dim, hidden_dim)
        self.chord_lstm = nn.LSTM(hidden_dim, hidden_dim, num_layers=2, batch_first=True)
        self.chord_output = nn.Linear(hidden_dim, chord_vocab)
        self.voicing_network = nn.Sequential(
            nn.Linear(hidden_dim + chord_vocab, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 128 * 4)  # 4-voice harmony
        )
        
    def forward(self, melody_features, chord_context=None):
        encoded_melody = self.melody_encoder(melody_features)
        chord_progression, _ = self.chord_lstm(encoded_melody)
        chord_probs = self.chord_output(chord_progression)
        
        # Generate voicings
        voicing_input = torch.cat([chord_progression, chord_probs], dim=-1)
        voicings = self.voicing_network(voicing_input)
        
        return chord_probs, voicings.reshape(-1, 4, 128)

class RhythmGeneratorNN(nn.Module):
    """Neural network for rhythm and percussion generation"""
    
    def __init__(self, genre_dim=50, tempo_dim=10, drum_channels=16):
        super(RhythmGeneratorNN, self).__init__()
        self.genre_embedding = nn.Embedding(genre_dim, 64)
        self.tempo_embedding = nn.Embedding(tempo_dim, 32)
        
        self.rhythm_generator = nn.Sequential(
            nn.Linear(64 + 32, 256),
            nn.ReLU(),
            nn.LSTM(256, 256, num_layers=2, batch_first=True),
        )
        
        self.drum_head = nn.Linear(256, drum_channels)
        self.velocity_head = nn.Linear(256, drum_channels)
        
    def forward(self, genre_id, tempo_category, sequence_length):
        genre_emb = self.genre_embedding(genre_id)
        tempo_emb = self.tempo_embedding(tempo_category)
        
        combined = torch.cat([genre_emb, tempo_emb], dim=-1)
        combined = combined.unsqueeze(1).repeat(1, sequence_length, 1)
        
        rhythm_features, _ = self.rhythm_generator(combined)
        
        drum_pattern = torch.sigmoid(self.drum_head(rhythm_features))
        velocities = torch.sigmoid(self.velocity_head(rhythm_features))
        
        return drum_pattern, velocities

class InstrumentArrangementNN(nn.Module):
    """Neural network for intelligent instrument arrangement"""
    
    def __init__(self, instrument_vocab=100, arrangement_dim=512):
        super(InstrumentArrangementNN, self).__init__()
        self.instrument_embedding = nn.Embedding(instrument_vocab, 128)
        self.arrangement_transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=512, nhead=8, batch_first=True),
            num_layers=6
        )
        self.layering_head = nn.Linear(512, instrument_vocab)
        self.dynamics_head = nn.Linear(512, instrument_vocab)
        
    def forward(self, selected_instruments, music_context):
        # Arrange instruments based on genre, complexity, and musical context
        inst_emb = self.instrument_embedding(selected_instruments)
        
        # Combine with musical context (melody, harmony features)
        arrangement_input = torch.cat([inst_emb, music_context], dim=-1)
        arranged = self.arrangement_transformer(arrangement_input)
        
        layering = torch.softmax(self.layering_head(arranged), dim=-1)
        dynamics = torch.sigmoid(self.dynamics_head(arranged))
        
        return layering, dynamics

class VocalSynthesisNN(nn.Module):
    """Advanced Neural Network for Vocal Synthesis and Harmony Generation"""
    
    def __init__(self, vocab_size=10000, vocal_dim=512, harmony_voices=4):
        super(VocalSynthesisNN, self).__init__()
        
        # Lyric processing
        self.lyric_embedding = nn.Embedding(vocab_size, 256)
        self.phoneme_encoder = nn.LSTM(256, 256, num_layers=2, batch_first=True)
        
        # Vocal style and gender control
        self.vocal_style_embedding = nn.Embedding(20, 64)  # different vocal styles
        self.gender_embedding = nn.Embedding(3, 32)  # male, female, neutral
        
        # Melody generation for vocals
        self.vocal_melody_generator = nn.Sequential(
            nn.Linear(256 + 64 + 32, 512),
            nn.ReLU(),
            nn.LSTM(512, 512, num_layers=3, batch_first=True)
        )
        
        # Harmony generation for backing vocals/choir
        self.harmony_generator = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, harmony_voices * 128)  # 4-part harmony
        )
        
        # Vocal expression and dynamics
        self.expression_head = nn.Linear(512, 128)  # vibrato, breath, etc.
        self.dynamics_head = nn.Linear(512, 128)   # volume, intensity
        
    def forward(self, lyrics_tokens, vocal_style, gender, sequence_length):
        # Process lyrics
        lyric_emb = self.lyric_embedding(lyrics_tokens)
        phoneme_features, _ = self.phoneme_encoder(lyric_emb)
        
        # Style and gender conditioning
        style_emb = self.vocal_style_embedding(vocal_style)
        gender_emb = self.gender_embedding(gender)
        
        # Combine features
        combined_features = torch.cat([
            phoneme_features.mean(dim=1, keepdim=True).expand(-1, sequence_length, -1),
            style_emb.unsqueeze(1).expand(-1, sequence_length, -1),
            gender_emb.unsqueeze(1).expand(-1, sequence_length, -1)
        ], dim=-1)
        
        # Generate vocal melody
        vocal_output, _ = self.vocal_melody_generator(combined_features)
        
        # Generate harmony
        harmony = self.harmony_generator(vocal_output)
        harmony = harmony.reshape(-1, sequence_length, 4, 128)
        
        # Expression and dynamics
        expression = torch.sigmoid(self.expression_head(vocal_output))
        dynamics = torch.sigmoid(self.dynamics_head(vocal_output))
        
        return vocal_output, harmony, expression, dynamics

class ModernGenreNN(nn.Module):
    """Neural Network for Modern Genre-Specific Elements (Hip-Hop, EDM, etc.)"""
    
    def __init__(self, genre_vocab=50):
        super(ModernGenreNN, self).__init__()
        
        # Hip-Hop specific elements
        self.trap_808_generator = nn.Sequential(
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 128)  # 808 bass patterns
        )
        
        # EDM specific elements
        self.edm_synth_generator = nn.Sequential(
            nn.Linear(128, 512),
            nn.ReLU(),
            nn.LSTM(512, 512, batch_first=True),
        )
        
        # Drop and buildup generation for EDM
        self.buildup_generator = nn.Linear(512, 256)
        self.drop_generator = nn.Linear(512, 512)
        
        # Genre-specific percussion
        self.genre_percussion = nn.ModuleDict({
            'trap': nn.Linear(128, 64),
            'house': nn.Linear(128, 64),
            'techno': nn.Linear(128, 64),
            'dubstep': nn.Linear(128, 64)
        })
        
    def forward(self, genre_context, sequence_length):
        # Generate modern elements based on genre
        outputs = {}
        
        if 'trap' in genre_context or 'hip-hop' in genre_context:
            trap_808 = self.trap_808_generator(genre_context)
            outputs['808_bass'] = trap_808
            
        if any(edm_genre in genre_context for edm_genre in ['house', 'techno', 'dubstep']):
            edm_features, _ = self.edm_synth_generator(genre_context.unsqueeze(1).repeat(1, sequence_length, 1))
            outputs['edm_synth'] = edm_features
            outputs['buildup'] = self.buildup_generator(edm_features)
            outputs['drop'] = self.drop_generator(edm_features)
            
        return outputs

# ...existing code...

class AIComposer:
    """Main AI composer class integrating all neural networks"""
    
    def __init__(self, device='cpu'):
        self.device = device
        self.melody_generator = MelodyGeneratorNN().to(device)
        self.harmony_generator = HarmonyGeneratorNN().to(device)
        self.rhythm_generator = RhythmGeneratorNN().to(device)
        self.arrangement_generator = InstrumentArrangementNN().to(device)
        self.vocal_generator = VocalSynthesisNN().to(device)  # NEW: Vocal synthesis
        self.modern_genre_generator = ModernGenreNN().to(device)  # NEW: Modern genres
        
        # Music theory knowledge base
        self.chord_progressions = self._load_chord_progressions()
        self.scale_patterns = self._load_scale_patterns()
        self.genre_templates = self._load_genre_templates()
        
        # Enhanced instrument mappings
        self.instrument_mappings = self._load_instrument_mappings()
        
        # Load pre-trained models if available
        self._load_pretrained_models()
        
    def _load_instrument_mappings(self):
        """Load comprehensive instrument mappings for 40+ instruments"""
        return {
            # Vocal instruments
            'male_vocals': {'type': 'vocal', 'range': (60, 84), 'program': 0},
            'female_vocals': {'type': 'vocal', 'range': (64, 88), 'program': 0},
            'choir': {'type': 'vocal', 'range': (48, 84), 'program': 91},
            'backing_vocals': {'type': 'vocal', 'range': (60, 84), 'program': 0},
            
            # Hip-hop specific
            '808_drums': {'type': 'percussion', 'range': (24, 60), 'program': 118},
            'trap_drums': {'type': 'percussion', 'range': (35, 81), 'program': 128},
            
            # Electronic expanded
            'lead_synth': {'type': 'electronic', 'range': (60, 96), 'program': 81},
            'pad_synth': {'type': 'electronic', 'range': (36, 84), 'program': 89},
            'bass_synth': {'type': 'electronic', 'range': (24, 60), 'program': 39},
            'arp_synth': {'type': 'electronic', 'range': (48, 84), 'program': 103},
            
            # Traditional instruments (existing + new)
            'acoustic_piano': {'type': 'keyboard', 'range': (21, 108), 'program': 1},
            'electric_piano': {'type': 'keyboard', 'range': (28, 103), 'program': 5},
            'organ': {'type': 'keyboard', 'range': (36, 96), 'program': 17},
            'acoustic_guitar': {'type': 'string', 'range': (40, 84), 'program': 25},
            'electric_guitar': {'type': 'string', 'range': (40, 84), 'program': 30},
            'bass_guitar': {'type': 'bass', 'range': (28, 67), 'program': 34},
            'electric_bass': {'type': 'bass', 'range': (28, 67), 'program': 34},
            'upright_bass': {'type': 'bass', 'range': (28, 67), 'program': 43},
            'violin': {'type': 'string', 'range': (55, 103), 'program': 41},
            'viola': {'type': 'string', 'range': (48, 91), 'program': 42},
            'cello': {'type': 'string', 'range': (36, 76), 'program': 43},
            'harp': {'type': 'string', 'range': (23, 103), 'program': 47},
            'mandolin': {'type': 'string', 'range': (55, 84), 'program': 25},
            'banjo': {'type': 'string', 'range': (50, 84), 'program': 106},
            'ukulele': {'type': 'string', 'range': (60, 84), 'program': 25},
            'acoustic_drums': {'type': 'percussion', 'range': (35, 81), 'program': 128},
            'electronic_drums': {'type': 'percussion', 'range': (35, 81), 'program': 128},
            'congas': {'type': 'percussion', 'range': (62, 67), 'program': 128},
            'bongos': {'type': 'percussion', 'range': (60, 67), 'program': 128},
            'tabla': {'type': 'percussion', 'range': (50, 67), 'program': 128},
            'xylophone': {'type': 'percussion', 'range': (65, 108), 'program': 14},
            'marimba': {'type': 'percussion', 'range': (48, 103), 'program': 13},
            'trumpet': {'type': 'brass', 'range': (58, 94), 'program': 57},
            'trombone': {'type': 'brass', 'range': (40, 72), 'program': 58},
            'french_horn': {'type': 'brass', 'range': (41, 77), 'program': 61},
            'tuba': {'type': 'brass', 'range': (28, 58), 'program': 59},
            'saxophone': {'type': 'brass', 'range': (49, 80), 'program': 67},
            'flute': {'type': 'woodwind', 'range': (60, 96), 'program': 74},
            'clarinet': {'type': 'woodwind', 'range': (50, 91), 'program': 72},
            'oboe': {'type': 'woodwind', 'range': (58, 91), 'program': 69},
            'bassoon': {'type': 'woodwind', 'range': (34, 67), 'program': 71},
            'harmonica': {'type': 'woodwind', 'range': (60, 84), 'program': 23},
            'synthesizer': {'type': 'electronic', 'range': (21, 108), 'program': 81},
            'sitar': {'type': 'world', 'range': (48, 84), 'program': 105},
            'didgeridoo': {'type': 'world', 'range': (28, 48), 'program': 123},
            'accordion': {'type': 'world', 'range': (41, 96), 'program': 22}
        }
        
    def _load_chord_progressions(self):
        """Load common chord progressions for different genres"""
        return {
            'pop': [
                [1, 5, 6, 4],  # I-V-vi-IV
                [1, 6, 4, 5],  # I-vi-IV-V
                [6, 4, 1, 5],  # vi-IV-I-V
            ],
            'rock': [
                [1, 7, 4, 1],  # I-♭VII-IV-I
                [1, 5, 6, 4],  # I-V-vi-IV
                [1, 4, 5, 4],  # I-IV-V-IV
            ],
            'jazz': [
                [1, 6, 2, 5],  # I-vi-ii-V
                [1, 3, 6, 2, 5, 1],  # I-iii-vi-ii-V-I
                [2, 5, 1, 6],  # ii-V-I-vi
            ],
            'classical': [
                [1, 4, 5, 1],  # I-IV-V-I
                [1, 2, 5, 1],  # I-ii-V-I
                [1, 6, 4, 5],  # I-vi-IV-V
            ]
        }
    
    def _load_scale_patterns(self):
        """Load musical scales and modes"""
        return {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'minor': [0, 2, 3, 5, 7, 8, 10],
            'dorian': [0, 2, 3, 5, 7, 9, 10],
            'mixolydian': [0, 2, 4, 5, 7, 9, 10],
            'blues': [0, 3, 5, 6, 7, 10],
            'pentatonic': [0, 2, 4, 7, 9],
        }
    
    def _load_genre_templates(self):
        """Load genre-specific templates and characteristics"""
        return {
            'pop': {
                'tempo_range': (80, 140),
                'common_instruments': ['piano', 'guitar', 'bass', 'drums', 'strings'],
                'structure': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
                'scale_preference': 'major',
            },
            'rock': {
                'tempo_range': (100, 180),
                'common_instruments': ['electric_guitar', 'bass', 'drums', 'vocals'],
                'structure': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'solo', 'chorus', 'outro'],
                'scale_preference': 'minor',
            },
            'jazz': {
                'tempo_range': (60, 200),
                'common_instruments': ['piano', 'bass', 'drums', 'saxophone', 'trumpet'],
                'structure': ['head', 'solos', 'head'],
                'scale_preference': 'dorian',
            },
            'classical': {
                'tempo_range': (60, 160),
                'common_instruments': ['violin', 'viola', 'cello', 'piano', 'flute', 'oboe'],
                'structure': ['exposition', 'development', 'recapitulation'],
                'scale_preference': 'major',
            }
        }
    
    def _load_pretrained_models(self):
        """Load pre-trained model weights if available"""
        model_dir = 'models/pretrained'
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            if os.path.exists(f'{model_dir}/melody_generator.pth'):
                self.melody_generator.load_state_dict(torch.load(f'{model_dir}/melody_generator.pth'))
                logger.info("Loaded pre-trained melody generator")
            if os.path.exists(f'{model_dir}/vocal_generator.pth'):
                self.vocal_generator.load_state_dict(torch.load(f'{model_dir}/vocal_generator.pth'))
                logger.info("Loaded pre-trained vocal generator")
        except Exception as e:
            logger.warning(f"Could not load pre-trained models: {e}")
    
    def generate_composition(self, request: MusicGenerationRequest) -> Tuple[List[InstrumentTrack], Dict]:
        """Generate a complete multi-instrumental composition"""
        logger.info(f"Generating composition: {request.genre} {request.mood} - {request.duration}s")
        
        # 1. Analyze lyrics and extract emotional features
        lyric_features = self._analyze_lyrics(request.lyrics)
        
        # 2. Generate musical structure
        structure = self._generate_structure(request.genre, request.duration)
        
        # 3. Generate melody
        melody_data = self._generate_melody(request, lyric_features, structure)
        
        # 4. Generate harmony
        harmony_data = self._generate_harmony(melody_data, request)
        
        # 5. Generate rhythm section
        rhythm_data = self._generate_rhythm(request, structure)
        
        # 6. Arrange instruments
        instrument_tracks = self._arrange_instruments(
            request.instruments, melody_data, harmony_data, rhythm_data, request
        )
        
        # 7. Apply mixing and mastering
        mixed_tracks = self._apply_mixing(instrument_tracks, request)
        
        # 8. Generate metadata
        metadata = self._generate_metadata(request, structure, mixed_tracks)
        
        return mixed_tracks, metadata
    
    def _analyze_lyrics(self, lyrics: str) -> Dict:
        """Analyze lyrics for emotional content and structure"""
        if not lyrics.strip():
            return {'emotion_vector': np.zeros(10), 'word_count': 0, 'syllable_pattern': []}
        
        # Simple sentiment analysis (can be enhanced with proper NLP)
        emotion_keywords = {
            'happy': ['love', 'joy', 'bright', 'smile', 'laugh', 'dance'],
            'sad': ['cry', 'tear', 'pain', 'lost', 'lonely', 'dark'],
            'angry': ['fight', 'rage', 'mad', 'hate', 'break'],
            'peaceful': ['calm', 'peace', 'quiet', 'gentle', 'soft'],
            'energetic': ['run', 'jump', 'fast', 'energy', 'power']
        }
        
        words = lyrics.lower().split()
        emotion_scores = {emotion: 0 for emotion in emotion_keywords}
        
        for word in words:
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in word for keyword in keywords):
                    emotion_scores[emotion] += 1
        
        return {
            'emotion_vector': np.array(list(emotion_scores.values())),
            'word_count': len(words),
            'syllable_pattern': self._extract_syllable_pattern(lyrics)
        }
    
    def _extract_syllable_pattern(self, lyrics: str) -> List[int]:
        """Extract syllable pattern from lyrics for rhythm generation"""
        # Simplified syllable counting
        words = lyrics.split()
        syllables = []
        for word in words:
            # Simple vowel counting heuristic
            vowels = 'aeiouAEIOU'
            count = sum(1 for char in word if char in vowels)
            syllables.append(max(1, count))
        return syllables
    
    def _generate_structure(self, genre: str, duration: float) -> List[Dict]:
        """Generate musical structure based on genre and duration"""
        template = self.genre_templates.get(genre, self.genre_templates['pop'])
        base_structure = template['structure']
        
        # Calculate section durations
        total_sections = len(base_structure)
        avg_section_duration = duration / total_sections
        
        structure = []
        current_time = 0
        
        for i, section_name in enumerate(base_structure):
            section_duration = avg_section_duration
            
            # Adjust durations for specific sections
            if section_name in ['intro', 'outro']:
                section_duration *= 0.7
            elif section_name in ['chorus']:
                section_duration *= 1.2
            elif section_name in ['bridge', 'solo']:
                section_duration *= 1.1
            
            structure.append({
                'name': section_name,
                'start_time': current_time,
                'duration': section_duration,
                'tempo_multiplier': 1.0,
                'intensity': self._calculate_section_intensity(section_name)
            })
            
            current_time += section_duration
        
        return structure
    
    def _calculate_section_intensity(self, section_name: str) -> float:
        """Calculate intensity level for different song sections"""
        intensity_map = {
            'intro': 0.3,
            'verse': 0.6,
            'chorus': 1.0,
            'bridge': 0.8,
            'solo': 0.9,
            'outro': 0.4,
            'head': 0.7,
            'exposition': 0.5,
            'development': 0.8,
            'recapitulation': 0.6
        }
        return intensity_map.get(section_name, 0.7)
    
    def _generate_melody(self, request: MusicGenerationRequest, lyric_features: Dict, structure: List[Dict]) -> np.ndarray:
        """Generate main melody using neural network"""
        # Prepare input features
        genre_features = self._encode_genre(request.genre)
        mood_features = self._encode_mood(request.mood)
        
        # Generate melody sequence
        with torch.no_grad():
            sequence_length = int(request.duration * 4)  # 4 beats per second
            
            # Start with a seed note based on key
            seed = self._key_to_midi(request.key)
            melody_sequence = [seed]
            
            hidden = None
            
            for i in range(sequence_length - 1):
                current_input = torch.tensor([melody_sequence[-1:]], dtype=torch.long).to(self.device)
                output, hidden = self.melody_generator(current_input, hidden)
                
                # Apply music theory constraints
                next_note = self._apply_melodic_constraints(
                    output, melody_sequence[-1], request.key, i / sequence_length
                )
                melody_sequence.append(next_note)
        
        return np.array(melody_sequence)
    
    def _generate_harmony(self, melody: np.ndarray, request: MusicGenerationRequest) -> np.ndarray:
        """Generate harmony and chord progressions"""
        # Convert melody to features
        melody_tensor = torch.tensor(melody, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            chord_probs, voicings = self.harmony_generator(melody_tensor)
            
            # Apply chord progression rules
            chord_progression = self._apply_harmonic_rules(
                chord_probs, request.genre, request.key
            )
        
        return voicings.cpu().numpy()
    
    def _generate_rhythm(self, request: MusicGenerationRequest, structure: List[Dict]) -> Dict:
        """Generate rhythm and percussion patterns"""
        genre_id = self._encode_genre_id(request.genre)
        tempo_category = self._encode_tempo_category(request.tempo_bpm)
        
        rhythm_patterns = {}
        
        for section in structure:
            sequence_length = int(section['duration'] * 4)
            intensity = section['intensity']
            
            with torch.no_grad():
                genre_tensor = torch.tensor([genre_id], dtype=torch.long).to(self.device)
                tempo_tensor = torch.tensor([tempo_category], dtype=torch.long).to(self.device)
                
                drum_pattern, velocities = self.rhythm_generator(
                    genre_tensor, tempo_tensor, sequence_length
                )
                
                # Apply intensity scaling
                scaled_pattern = drum_pattern * intensity
                scaled_velocities = velocities * intensity
                
                rhythm_patterns[section['name']] = {
                    'pattern': scaled_pattern.cpu().numpy(),
                    'velocities': scaled_velocities.cpu().numpy()
                }
        
        return rhythm_patterns
    
    def _arrange_instruments(self, instruments: List[str], melody: np.ndarray, 
                           harmony: np.ndarray, rhythm: Dict, 
                           request: MusicGenerationRequest) -> List[InstrumentTrack]:
        """Arrange and orchestrate selected instruments"""
        tracks = []
        
        # Primary melody instrument
        if 'piano' in instruments or 'lead_guitar' in instruments:
            melody_instrument = 'piano' if 'piano' in instruments else 'lead_guitar'
            melody_track = self._create_instrument_track(
                melody_instrument, melody, request, role='melody'
            )
            tracks.append(melody_track)
        
        # Harmony instruments
        harmony_instruments = [inst for inst in instruments if inst in 
                             ['strings', 'pad', 'choir', 'acoustic_guitar']]
        
        for i, instrument in enumerate(harmony_instruments[:3]):  # Max 3 harmony instruments
            if i < harmony.shape[1]:  # Ensure we have harmony data
                harmony_track = self._create_instrument_track(
                    instrument, harmony[0, i, :], request, role='harmony'
                )
                tracks.append(harmony_track)
        
        # Bass line
        if 'bass' in instruments or 'bass_guitar' in instruments:
            bass_line = self._generate_bass_line(melody, harmony, request)
            bass_track = self._create_instrument_track(
                'bass', bass_line, request, role='bass'
            )
            tracks.append(bass_track)
        
        # Percussion
        if 'drums' in instruments:
            drum_track = self._create_drum_track(rhythm, request)
            tracks.append(drum_track)
        
        # Vocals
        if 'vocals' in instruments:
            lyrics = request.lyrics if request.lyrics else "La la la"
            vocal_track = self._create_vocal_track(lyrics, melody, request)
            tracks.append(vocal_track)
        
        return tracks
    
    def _create_instrument_track(self, instrument_name: str, midi_data: np.ndarray, 
                               request: MusicGenerationRequest, role: str) -> InstrumentTrack:
        """Create an individual instrument track"""
        # Convert MIDI to audio
        audio_data = self._midi_to_audio(midi_data, instrument_name, request)
        
        # Apply instrument-specific effects
        effects = self._get_instrument_effects(instrument_name, request.genre)
        
        # Set mixing parameters
        volume = self._calculate_instrument_volume(role, request.mood)
        pan = self._calculate_instrument_pan(instrument_name, role)
        
        return InstrumentTrack(
            instrument_name=instrument_name,
            midi_data=midi_data,
            audio_data=audio_data,
            volume=volume,
            pan=pan,
            effects=effects
        )
    
    def _create_drum_track(self, rhythm_patterns: Dict, request: MusicGenerationRequest) -> InstrumentTrack:
        """Create drum track from rhythm patterns"""
        # Combine all rhythm patterns
        full_pattern = []
        for section_name, pattern_data in rhythm_patterns.items():
            full_pattern.append(pattern_data['pattern'])
        
        combined_pattern = np.concatenate(full_pattern, axis=1)
        
        # Convert to audio
        drum_audio = self._drums_to_audio(combined_pattern, request)
        
        return InstrumentTrack(
            instrument_name='drums',
            midi_data=combined_pattern,
            audio_data=drum_audio,
            volume=0.8,
            pan=0.0,  # Center
            effects={'compression': True, 'eq': 'drums'}
        )
    
    def _create_vocal_track(self, lyrics: str, melody: np.ndarray, request: MusicGenerationRequest) -> InstrumentTrack:
        """Create vocal track with lyrics and melody"""
        # Convert melody to MIDI
        midi_data = melody.astype(int)
        
        # Generate vocal audio from MIDI and lyrics
        audio_data = self._vocal_to_audio(midi_data, lyrics, request)
        
        return InstrumentTrack(
            instrument_name='vocals',
            midi_data=midi_data,
            audio_data=audio_data,
            volume=1.0,
            pan=0.0,
            effects={'reverb': True, 'eq': 'vocals'}
        )
    
    def _apply_mixing(self, tracks: List[InstrumentTrack], request: MusicGenerationRequest) -> List[InstrumentTrack]:
        """Apply professional mixing to all tracks"""
        mixed_tracks = []
        
        for track in tracks:
            # Apply EQ
            eq_audio = self._apply_eq(track.audio_data, track.effects.get('eq', 'default'))
            
            # Apply compression
            if track.effects.get('compression', False):
                eq_audio = self._apply_compression(eq_audio)
            
            # Apply reverb based on genre
            reverb_audio = self._apply_reverb(eq_audio, request.genre, track.instrument_name)
            
            # Apply volume and pan
            final_audio = reverb_audio * track.volume
            if track.pan != 0:
                final_audio = self._apply_pan(final_audio, track.pan)
            
            mixed_track = InstrumentTrack(
                instrument_name=track.instrument_name,
                midi_data=track.midi_data,
                audio_data=final_audio,
                volume=track.volume,
                pan=track.pan,
                effects=track.effects
            )
            mixed_tracks.append(mixed_track)
        
        return mixed_tracks
    
    def _generate_metadata(self, request: MusicGenerationRequest, structure: List[Dict], 
                         tracks: List[InstrumentTrack]) -> Dict:
        """Generate comprehensive metadata for the composition"""
        return {
            'composition_info': {
                'genre': request.genre,
                'mood': request.mood,
                'tempo_bpm': request.tempo_bpm,
                'key': request.key,
                'duration': request.duration,
                'time_signature': request.time_signature
            },
            'structure': structure,
            'instruments': [track.instrument_name for track in tracks],
            'track_count': len(tracks),
            'generation_timestamp': time.time(),
            'ai_model_version': '2.0',
            'stems_available': request.enable_stems,
            'export_formats': request.export_formats
        }
    
    # Helper methods for audio processing
    def _midi_to_audio(self, midi_data: np.ndarray, instrument: str, request: MusicGenerationRequest) -> np.ndarray:
        """Convert MIDI data to audio using synthesized instruments"""
        # This is a simplified implementation
        # In practice, you would use high-quality sample libraries or neural audio synthesis
        
        sample_rate = 44100
        duration = request.duration
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        audio = np.zeros_like(t)
        
        # Simple synthesis based on MIDI notes
        for i, note in enumerate(midi_data):
            if note > 0:  # Valid MIDI note
                freq = 440 * (2 ** ((note - 69) / 12))  # Convert MIDI to frequency
                note_start = i * len(t) / len(midi_data)
                note_end = min((i + 1) * len(t) / len(midi_data), len(t))
                
                if note_end > note_start:
                    note_t = t[int(note_start):int(note_end)]
                    
                    # Generate waveform based on instrument
                    if instrument == 'piano':
                        waveform = self._generate_piano_sound(note_t, freq)
                    elif instrument == 'guitar':
                        waveform = self._generate_guitar_sound(note_t, freq)
                    elif instrument == 'strings':
                        waveform = self._generate_strings_sound(note_t, freq)
                    else:
                        waveform = self._generate_generic_sound(note_t, freq)
                    
                    audio[int(note_start):int(note_end)] += waveform
        
        return audio
    
    def _generate_piano_sound(self, t: np.ndarray, freq: float) -> np.ndarray:
        """Generate piano-like sound"""
        # Attack-decay envelope
        envelope = np.exp(-3 * t) * (1 - np.exp(-30 * t))
        
        # Harmonic content for piano
        fundamental = np.sin(2 * np.pi * freq * t)
        second_harmonic = 0.3 * np.sin(2 * np.pi * freq * 2 * t)
        third_harmonic = 0.15 * np.sin(2 * np.pi * freq * 3 * t)
        
        return envelope * (fundamental + second_harmonic + third_harmonic)
    
    def _generate_guitar_sound(self, t: np.ndarray, freq: float) -> np.ndarray:
        """Generate guitar-like sound"""
        # Plucked string envelope
        envelope = np.exp(-2 * t)
        
        # Add slight detuning and harmonics
        fundamental = np.sin(2 * np.pi * freq * t)
        detune = 0.1 * np.sin(2 * np.pi * freq * 1.001 * t)
        harmonics = 0.2 * np.sin(2 * np.pi * freq * 2 * t) + 0.1 * np.sin(2 * np.pi * freq * 3 * t)
        
        return envelope * (fundamental + detune + harmonics)
    
    def _generate_strings_sound(self, t: np.ndarray, freq: float) -> np.ndarray:
        """Generate string section sound"""
        # Slow attack for strings
        envelope = 1 - np.exp(-8 * t)
        
        # Rich harmonic content
        fundamental = np.sin(2 * np.pi * freq * t)
        harmonics = sum(0.3/i * np.sin(2 * np.pi * freq * i * t) for i in range(2, 6))
        
        return envelope * (fundamental + harmonics)
    
    def _generate_generic_sound(self, t: np.ndarray, freq: float) -> np.ndarray:
        """Generate generic synthesized sound"""
        envelope = np.exp(-t) * (1 - np.exp(-10 * t))
        return envelope * np.sin(2 * np.pi * freq * t)
    
    def _drums_to_audio(self, pattern: np.ndarray, request: MusicGenerationRequest) -> np.ndarray:
        """Convert drum pattern to audio"""
        sample_rate = 44100
        audio = np.zeros(int(sample_rate * request.duration))
        
        # Simple drum sounds (in practice, use high-quality samples)
        for channel in range(pattern.shape[0]):
            for beat in range(pattern.shape[1]):
                if pattern[channel, beat] > 0.5:
                    beat_time = beat * len(audio) / pattern.shape[1]
                    drum_sound = self._generate_drum_sound(channel, request.genre)
                    
                    start_idx = int(beat_time)
                    end_idx = min(start_idx + len(drum_sound), len(audio))
                    
                    audio[start_idx:end_idx] += drum_sound[:end_idx-start_idx] * pattern[channel, beat]
        
        return audio
    
    def _generate_drum_sound(self, channel: int, genre: str) -> np.ndarray:
        """Generate drum sounds for different channels"""
        sample_rate = 44100
        duration = 0.2  # 200ms drum hit
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        if channel == 0:  # Kick drum
            freq = 60
            envelope = np.exp(-20 * t)
            return envelope * np.sin(2 * np.pi * freq * t)
        elif channel == 1:  # Snare
            envelope = np.exp(-10 * t)
            noise = np.random.normal(0, 0.1, len(t))
            tone = np.sin(2 * np.pi * 200 * t)
            return envelope * (0.7 * noise + 0.3 * tone)
        elif channel == 2:  # Hi-hat
            envelope = np.exp(-15 * t)
            noise = np.random.normal(0, 0.05, len(t))
            return envelope * noise
        else:
            # Other percussion
            envelope = np.exp(-8 * t)
            freq = 100 + channel * 50
            return envelope * np.sin(2 * np.pi * freq * t)
    
    def _vocal_to_audio(self, midi_data: np.ndarray, lyrics: str, request: MusicGenerationRequest) -> np.ndarray:
        """Convert vocal MIDI data and lyrics to audio"""
        # This is a simplified implementation
        # In practice, use a high-quality neural vocoder or sample library
        
        sample_rate = 44100
        duration = request.duration
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        audio = np.zeros_like(t)
        
        # Simple synthesis based on MIDI notes (vocal formants)
        for i, note in enumerate(midi_data):
            if note > 0:  # Valid MIDI note
                freq = 440 * (2 ** ((note - 69) / 12))  # Convert MIDI to frequency
                note_start = i * len(t) / len(midi_data)
                note_end = min((i + 1) * len(t) / len(midi_data), len(t))
                
                if note_end > note_start:
                    note_t = t[int(note_start):int(note_end)]
                    
                    # Generate vocal-like waveform
                    formant_freqs = [freq, freq * 1.5, freq * 2.0]  # Harmonics
                    waveform = sum(np.sin(2 * np.pi * f * note_t) for f in formant_freqs)
                    
                    # Apply simple envelope
                    envelope = np.exp(-3 * note_t)
                    audio[int(note_start):int(note_end)] += waveform * envelope
        
        return audio
    
    # Audio effects methods
    def _apply_eq(self, audio: np.ndarray, eq_type: str) -> np.ndarray:
        """Apply EQ based on instrument type"""
        # Simplified EQ using basic filtering
        if eq_type == 'drums':
            # Boost low end, cut some mids
            return audio * 1.2  # Simplified
        elif eq_type == 'bass':
            # Boost low frequencies
            return audio * 1.1
        elif eq_type == 'vocals':
            # Enhance presence and clarity
            return audio * 1.3
        else:
            return audio
    
    def _apply_compression(self, audio: np.ndarray, ratio: float = 4.0, threshold: float = 0.7) -> np.ndarray:
        """Apply dynamic compression"""
        compressed = np.copy(audio)
        mask = np.abs(compressed) > threshold
        compressed[mask] = threshold + (compressed[mask] - threshold) / ratio
        return compressed
    
    def _apply_reverb(self, audio: np.ndarray, genre: str, instrument: str) -> np.ndarray:
        """Apply reverb appropriate for genre and instrument"""
        # Simple convolution reverb simulation
        reverb_amount = 0.1
        if genre in ['classical', 'ambient']:
            reverb_amount = 0.3
        elif genre in ['pop', 'rock']:
            reverb_amount = 0.15
        
        # Create simple impulse response
        impulse_length = 4410  # 0.1 second at 44.1kHz
        impulse = np.exp(-np.linspace(0, 3, impulse_length)) * np.random.normal(0, 0.01, impulse_length)
        
        # Convolve with audio
        reverb_audio = np.convolve(audio, impulse, mode='same')
        return audio + reverb_amount * reverb_audio
    
    def _apply_pan(self, audio: np.ndarray, pan: float) -> np.ndarray:
        """Apply stereo panning (-1 = left, 0 = center, 1 = right)"""
        # For mono to stereo conversion
        left_gain = np.sqrt((1 - pan) / 2)
        right_gain = np.sqrt((1 + pan) / 2)
        
        stereo_audio = np.column_stack([audio * left_gain, audio * right_gain])
        return stereo_audio
    
    # Utility methods
    def _encode_genre(self, genre: str) -> np.ndarray:
        """Encode genre as feature vector"""
        genres = ['pop', 'rock', 'jazz', 'classical', 'electronic', 'folk', 'blues', 'country']
        vector = np.zeros(len(genres))
        if genre.lower() in genres:
            vector[genres.index(genre.lower())] = 1.0
        return vector
    
    def _encode_mood(self, mood: str) -> np.ndarray:
        """Encode mood as feature vector"""
        moods = ['happy', 'sad', 'energetic', 'calm', 'mysterious', 'romantic', 'aggressive']
        vector = np.zeros(len(moods))
        if mood.lower() in moods:
            vector[moods.index(mood.lower())] = 1.0
        return vector
    
    def _encode_genre_id(self, genre: str) -> int:
        """Encode genre as ID for neural networks"""
        genres = ['pop', 'rock', 'jazz', 'classical', 'electronic', 'folk', 'blues', 'country']
        return genres.index(genre.lower()) if genre.lower() in genres else 0
    
    def _encode_tempo_category(self, tempo_bpm: int) -> int:
        """Categorize tempo for neural networks"""
        if tempo_bpm < 60:
            return 0  # Very slow
        elif tempo_bpm < 90:
            return 1  # Slow
        elif tempo_bpm < 120:
            return 2  # Moderate
        elif tempo_bpm < 150:
            return 3  # Fast
        else:
            return 4  # Very fast
    
    def _key_to_midi(self, key: str) -> int:
        """Convert key signature to MIDI note number"""
        key_map = {'C': 60, 'C#': 61, 'D': 62, 'D#': 63, 'E': 64, 'F': 65, 
                   'F#': 66, 'G': 67, 'G#': 68, 'A': 69, 'A#': 70, 'B': 71}
        return key_map.get(key.upper(), 60)
    
    def _apply_melodic_constraints(self, output: torch.Tensor, prev_note: int, 
                                 key: str, position: float) -> int:
        """Apply music theory constraints to melody generation"""
        probabilities = torch.softmax(output[0, -1], dim=0)
        
        # Prefer notes in key
        key_notes = self._get_key_notes(key)
        for note in key_notes:
            if 0 <= note < len(probabilities):
                probabilities[note] *= 1.5
        
        # Prefer smaller intervals
        for i in range(len(probabilities)):
            interval = abs(i - prev_note)
            if interval <= 2:  # Step-wise motion
                probabilities[i] *= 1.3
            elif interval <= 4:  # Small leaps
                probabilities[i] *= 1.1
        
        # Sample from modified probabilities
        note = torch.multinomial(probabilities, 1).item()
        return max(0, min(127, note))  # Ensure valid MIDI range
    
    def _get_key_notes(self, key: str) -> List[int]:
        """Get MIDI notes in the given key"""
        root = self._key_to_midi(key)
        scale = self.scale_patterns['major']  # Default to major scale
        return [(root + interval) % 128 for interval in scale]
    
    def _apply_harmonic_rules(self, chord_probs: torch.Tensor, genre: str, key: str) -> np.ndarray:
        """Apply harmonic rules to chord progressions"""
        # Get genre-appropriate progressions
        progressions = self.chord_progressions.get(genre, self.chord_progressions['pop'])
        
        # Select a progression (simplified)
        selected_progression = progressions[0]  # Use first progression for now
        
        # Convert to actual chords in the key
        root = self._key_to_midi(key)
        scale = self.scale_patterns['major']
        
        chord_sequence = []
        for degree in selected_progression:
            chord_root = (root + scale[degree - 1]) % 128
            chord_sequence.append(chord_root)
        
        return np.array(chord_sequence)
    
    def _generate_bass_line(self, melody: np.ndarray, harmony: np.ndarray, 
                          request: MusicGenerationRequest) -> np.ndarray:
        """Generate bass line that follows the harmony"""
        bass_line = np.zeros_like(melody)
        
        # Simple bass line generation
        for i in range(len(bass_line)):
            if i < harmony.shape[-1]:
                # Use root of current chord, transposed down
                chord_root = harmony[0, 0, i] if harmony.ndim > 2 else harmony[0, i]
                bass_note = chord_root - 24  # Two octaves down
                bass_line[i] = max(24, bass_note)  # Don't go below low C
        
        return bass_line
    
    def _get_instrument_effects(self, instrument: str, genre: str) -> Dict[str, Any]:
        """Get appropriate effects for instrument and genre"""
        base_effects = {
            'piano': {'reverb': 0.2, 'eq': 'piano'},
            'guitar': {'reverb': 0.3, 'eq': 'guitar', 'compression': True},
            'bass': {'compression': True, 'eq': 'bass'},
            'drums': {'compression': True, 'eq': 'drums'},
            'strings': {'reverb': 0.4, 'eq': 'strings'},
            'vocals': {'reverb': 0.5, 'eq': 'vocals'}
        }
        
        effects = base_effects.get(instrument, {'eq': 'default'})
        
        # Modify based on genre
        if genre == 'rock':
            if instrument == 'guitar':
                effects['distortion'] = True
        elif genre == 'jazz':
            effects['reverb'] = effects.get('reverb', 0.1) * 1.5
        
        return effects
    
    def _calculate_instrument_volume(self, role: str, mood: str) -> float:
        """Calculate appropriate volume for instrument role and mood"""
        base_volumes = {
            'melody': 0.8,
            'harmony': 0.6,
            'bass': 0.7,
            'drums': 0.8
        }
        
        volume = base_volumes.get(role, 0.6)
        
        # Adjust for mood
        if mood in ['energetic', 'aggressive']:
            volume *= 1.2
        elif mood in ['calm', 'peaceful']:
            volume *= 0.8
        
        return min(1.0, volume)
    
    def _calculate_instrument_pan(self, instrument: str, role: str) -> float:
        """Calculate stereo pan position for instrument"""
        pan_map = {
            'piano': 0.0,      # Center
            'guitar': 0.3,     # Slightly right
            'bass': 0.0,       # Center
            'drums': 0.0,      # Center
            'strings': -0.2,   # Slightly left
            'brass': 0.4,      # Right
            'woodwinds': -0.3,  # Left
            'vocals': 0.0      # Center
        }
        
        return pan_map.get(instrument, 0.0)

# Global composer instance
composer_instance = None

def get_composer() -> AIComposer:
    """Get singleton composer instance"""
    global composer_instance
    if composer_instance is None:
        composer_instance = AIComposer()
    return composer_instance

def initialize_ai_composer():
    """Initialize the AI composer system"""
    try:
        composer = get_composer()
        logger.info("AI Composer initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize AI Composer: {e}")
        return False
