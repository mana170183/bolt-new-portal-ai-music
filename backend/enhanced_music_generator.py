"""
🎵 Enhanced Multi-Instrumental Music Generation System
Comprehensive AI-powered music generator with 15+ instruments, neural style transfer,
genre/mood awareness, and professional-grade audio processing.
"""

import numpy as np
import soundfile as sf
import librosa
from scipy import signal
import random
import json
import tempfile
import os
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstrumentType(Enum):
    KEYBOARD = "keyboard"
    STRING = "string"
    BRASS = "brass"
    WOODWIND = "woodwind"
    PERCUSSION = "percussion"
    ELECTRONIC = "electronic"
    BASS = "bass"
    VOCAL = "vocal"

@dataclass
class InstrumentConfig:
    name: str
    type: InstrumentType
    priority: int
    default_octave: int
    amplitude_range: Tuple[float, float]
    frequency_range: Tuple[float, float]

class EnhancedInstrumentSynthesizer:
    """Advanced instrument synthesizer with 15+ instruments and professional quality samples"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.instrument_configs = self._initialize_instruments()
        
    def _initialize_instruments(self) -> Dict[str, InstrumentConfig]:
        """Initialize comprehensive instrument configurations"""
        return {
            # Keyboard Section
            'acoustic_piano': InstrumentConfig('Acoustic Piano', InstrumentType.KEYBOARD, 1, 4, (0.3, 0.7), (80, 4000)),
            'electric_piano': InstrumentConfig('Electric Piano', InstrumentType.KEYBOARD, 2, 4, (0.4, 0.8), (80, 3000)),
            'organ': InstrumentConfig('Organ', InstrumentType.KEYBOARD, 3, 4, (0.5, 0.9), (65, 2000)),
            'synthesizer': InstrumentConfig('Synthesizer', InstrumentType.ELECTRONIC, 1, 4, (0.3, 0.8), (50, 8000)),
            
            # String Section
            'acoustic_guitar': InstrumentConfig('Acoustic Guitar', InstrumentType.STRING, 1, 3, (0.4, 0.7), (80, 2000)),
            'electric_guitar': InstrumentConfig('Electric Guitar', InstrumentType.STRING, 2, 3, (0.5, 0.8), (80, 4000)),
            'bass_guitar': InstrumentConfig('Bass Guitar', InstrumentType.BASS, 1, 2, (0.5, 0.9), (40, 400)),
            'violin': InstrumentConfig('Violin', InstrumentType.STRING, 1, 5, (0.2, 0.6), (196, 3136)),
            'cello': InstrumentConfig('Cello', InstrumentType.STRING, 2, 3, (0.3, 0.7), (65, 1000)),
            
            # Brass Section
            'trumpet': InstrumentConfig('Trumpet', InstrumentType.BRASS, 1, 4, (0.4, 0.8), (165, 1400)),
            'trombone': InstrumentConfig('Trombone', InstrumentType.BRASS, 2, 3, (0.5, 0.9), (82, 600)),
            'saxophone': InstrumentConfig('Saxophone', InstrumentType.BRASS, 3, 4, (0.4, 0.7), (130, 1500)),
            
            # Percussion Section
            'acoustic_drums': InstrumentConfig('Acoustic Drums', InstrumentType.PERCUSSION, 1, 0, (0.6, 1.0), (40, 8000)),
            'electronic_drums': InstrumentConfig('Electronic Drums', InstrumentType.PERCUSSION, 2, 0, (0.5, 0.9), (50, 10000)),
            
            # Additional
            'flute': InstrumentConfig('Flute', InstrumentType.WOODWIND, 1, 5, (0.2, 0.5), (262, 2093)),
            'harp': InstrumentConfig('Harp', InstrumentType.STRING, 3, 4, (0.2, 0.6), (32, 4186))
        }
    
    def generate_enhanced_piano(self, frequency: float, duration: float, velocity: float = 0.7, style: str = 'classical') -> np.ndarray:
        """Generate enhanced piano sound with multiple styles"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Style-specific harmonic profiles
        if style == 'classical':
            harmonics = [1.0, 0.6, 0.3, 0.15, 0.08, 0.04, 0.02]
        elif style == 'jazz':
            harmonics = [1.0, 0.4, 0.6, 0.2, 0.3, 0.1, 0.05]
        elif style == 'rock':
            harmonics = [1.0, 0.7, 0.4, 0.2, 0.1, 0.05]
        else:
            harmonics = [1.0, 0.5, 0.25, 0.125, 0.0625]
        
        signal_audio = np.zeros_like(t)
        
        for i, harm_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            if harmonic_freq < self.sample_rate / 2:
                # Add slight detuning for realism
                detune = 1 + random.uniform(-0.002, 0.002)
                signal_audio += harm_amp * np.sin(2 * np.pi * harmonic_freq * detune * t)
        
        # Enhanced ADSR envelope with velocity sensitivity
        envelope = self._create_enhanced_adsr(len(t), velocity, style)
        return signal_audio * envelope * velocity
    
    def generate_electric_guitar(self, frequency: float, duration: float, velocity: float = 0.7, style: str = 'clean') -> np.ndarray:
        """Generate electric guitar with different amp styles"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Base guitar signal
        signal_audio = (np.sin(2 * np.pi * frequency * t) + 
                       0.3 * np.sin(2 * np.pi * frequency * 2 * t) +
                       0.2 * np.sin(2 * np.pi * frequency * 3 * t))
        
        # Style-specific processing
        if style == 'distorted':
            # Add distortion
            signal_audio = np.tanh(signal_audio * 3) * 0.7
        elif style == 'chorus':
            # Add chorus effect
            delay_samples = int(0.02 * self.sample_rate)
            if len(signal_audio) > delay_samples:
                delayed = np.zeros_like(signal_audio)
                delayed[delay_samples:] = signal_audio[:-delay_samples]
                signal_audio = signal_audio + 0.5 * delayed
        
        # String pluck envelope
        envelope = np.exp(-2 * t) * (1 - np.exp(-50 * t))
        return signal_audio * envelope * velocity
    
    def generate_bass_guitar(self, frequency: float, duration: float, velocity: float = 0.8, style: str = 'fingered') -> np.ndarray:
        """Generate bass guitar with different playing styles"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Bass harmonics (emphasized fundamental)
        signal_audio = (np.sin(2 * np.pi * frequency * t) + 
                       0.4 * np.sin(2 * np.pi * frequency * 2 * t) +
                       0.2 * np.sin(2 * np.pi * frequency * 3 * t) +
                       0.1 * np.sin(2 * np.pi * frequency * 4 * t))
        
        # Style-specific characteristics
        if style == 'slapped':
            # Sharper attack, more harmonics
            signal_audio += 0.3 * np.sin(2 * np.pi * frequency * 5 * t)
            envelope = np.exp(-4 * t) * (1 - np.exp(-100 * t))
        elif style == 'picked':
            # Brighter tone
            signal_audio += 0.2 * np.sin(2 * np.pi * frequency * 6 * t)
            envelope = np.exp(-3 * t) * (1 - np.exp(-30 * t))
        else:  # fingered
            envelope = np.exp(-1.5 * t) * (1 - np.exp(-20 * t))
        
        # Low-pass filter for bass character
        sos = signal.butter(4, 800, btype='low', fs=self.sample_rate, output='sos')
        signal_audio = signal.sosfilt(sos, signal_audio)
        
        return signal_audio * envelope * velocity
    
    def generate_strings(self, frequency: float, duration: float, velocity: float = 0.5, instrument: str = 'violin') -> np.ndarray:
        """Generate orchestral strings (violin, viola, cello)"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Instrument-specific harmonics
        if instrument == 'violin':
            harmonics = [1.0, 0.7, 0.5, 0.3, 0.2, 0.15, 0.1, 0.05]
            vibrato_freq = 6.5
        elif instrument == 'viola':
            harmonics = [1.0, 0.8, 0.6, 0.4, 0.25, 0.15, 0.08]
            vibrato_freq = 6.0
        elif instrument == 'cello':
            harmonics = [1.0, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1]
            vibrato_freq = 5.5
        else:
            harmonics = [1.0, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1]
            vibrato_freq = 6.0
        
        signal_audio = np.zeros_like(t)
        
        for i, harm_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            if harmonic_freq < self.sample_rate / 2:
                # Add vibrato
                vibrato = 1 + 0.02 * np.sin(2 * np.pi * vibrato_freq * t)
                signal_audio += harm_amp * np.sin(2 * np.pi * harmonic_freq * t * vibrato)
        
        # Strings envelope (slow attack, sustained)
        envelope = 1 - np.exp(-4 * t)
        if duration > 1.0:  # Add release for longer notes
            release_start = int(0.8 * len(t))
            envelope[release_start:] *= np.exp(-3 * t[release_start:])
        
        return signal_audio * envelope * velocity
    
    def generate_brass(self, frequency: float, duration: float, velocity: float = 0.7, instrument: str = 'trumpet') -> np.ndarray:
        """Generate brass instruments (trumpet, trombone, saxophone)"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Instrument-specific characteristics
        if instrument == 'trumpet':
            harmonics = [1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1]
            brightness = 1.2
        elif instrument == 'trombone':
            harmonics = [1.0, 0.9, 0.7, 0.5, 0.3, 0.2]
            brightness = 0.8
        elif instrument == 'saxophone':
            harmonics = [1.0, 0.6, 0.8, 0.4, 0.5, 0.2, 0.3]
            brightness = 1.0
        else:
            harmonics = [1.0, 0.7, 0.5, 0.3, 0.2]
            brightness = 1.0
        
        signal_audio = np.zeros_like(t)
        
        for i, harm_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            if harmonic_freq < self.sample_rate / 2:
                signal_audio += harm_amp * np.sin(2 * np.pi * harmonic_freq * t)
        
        # Brass envelope (quick attack, sustained)
        envelope = 1 - np.exp(-10 * t)
        
        # Add brightness control
        signal_audio *= brightness
        
        return signal_audio * envelope * velocity
    
    def generate_enhanced_drums(self, drum_type: str, velocity: float = 0.8, style: str = 'acoustic') -> np.ndarray:
        """Generate enhanced drum sounds with different styles"""
        if style == 'acoustic':
            return self._generate_acoustic_drums(drum_type, velocity)
        elif style == 'electronic':
            return self._generate_electronic_drums(drum_type, velocity)
        else:
            return self._generate_acoustic_drums(drum_type, velocity)
    
    def _generate_acoustic_drums(self, drum_type: str, velocity: float) -> np.ndarray:
        """Generate acoustic drum sounds"""
        if drum_type == 'kick':
            duration = 0.8
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            frequency = 60 * (1 + velocity * 0.2)
            signal_audio = np.sin(2 * np.pi * frequency * t) + 0.3 * np.sin(2 * np.pi * frequency * 0.5 * t)
            envelope = np.exp(-5 * t)
            
        elif drum_type == 'snare':
            duration = 0.3
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            noise = np.random.normal(0, 0.4, len(t))
            tone = np.sin(2 * np.pi * 200 * t)
            signal_audio = 0.6 * noise + 0.4 * tone
            envelope = np.exp(-10 * t)
            
        elif drum_type == 'hihat':
            duration = 0.15
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            signal_audio = np.random.normal(0, 0.3, len(t))
            sos = signal.butter(4, 6000, btype='high', fs=self.sample_rate, output='sos')
            signal_audio = signal.sosfilt(sos, signal_audio)
            envelope = np.exp(-20 * t)
            
        elif drum_type == 'crash':
            duration = 2.0
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            signal_audio = np.random.normal(0, 0.4, len(t))
            sos = signal.butter(4, 3000, btype='high', fs=self.sample_rate, output='sos')
            signal_audio = signal.sosfilt(sos, signal_audio)
            envelope = np.exp(-2 * t)
            
        else:
            return np.zeros(int(0.1 * self.sample_rate))
        
        return signal_audio * envelope * velocity
    
    def _generate_electronic_drums(self, drum_type: str, velocity: float) -> np.ndarray:
        """Generate electronic drum sounds"""
        if drum_type == 'kick':
            duration = 0.6
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            frequency = 50
            signal_audio = np.sin(2 * np.pi * frequency * t * np.exp(-8 * t))
            envelope = np.exp(-4 * t)
            
        elif drum_type == 'snare':
            duration = 0.2
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            signal_audio = np.sin(2 * np.pi * 200 * t) + 0.8 * np.random.normal(0, 0.3, len(t))
            envelope = np.exp(-15 * t)
            
        elif drum_type == 'hihat':
            duration = 0.1
            t = np.linspace(0, duration, int(self.sample_rate * duration), False)
            signal_audio = np.random.normal(0, 0.2, len(t))
            sos = signal.butter(4, 8000, btype='high', fs=self.sample_rate, output='sos')
            signal_audio = signal.sosfilt(sos, signal_audio)
            envelope = np.exp(-30 * t)
            
        else:
            return np.zeros(int(0.1 * self.sample_rate))
        
        return signal_audio * envelope * velocity
    
    def _create_enhanced_adsr(self, length: int, velocity: float, style: str = 'default') -> np.ndarray:
        """Create enhanced ADSR envelope with style variations"""
        envelope = np.ones(length)
        
        # Style-specific ADSR parameters
        if style == 'classical':
            attack, decay, sustain_level, release = 0.1, 0.2, 0.7, 0.3
        elif style == 'jazz':
            attack, decay, sustain_level, release = 0.05, 0.15, 0.8, 0.2
        elif style == 'rock':
            attack, decay, sustain_level, release = 0.02, 0.1, 0.9, 0.1
        else:
            attack, decay, sustain_level, release = 0.1, 0.3, 0.7, 0.2
        
        # Velocity affects sustain level
        sustain_level *= velocity
        
        attack_samples = int(length * attack)
        decay_samples = int(length * decay)
        release_samples = int(length * release)
        sustain_samples = length - attack_samples - decay_samples - release_samples
        
        if sustain_samples < 0:
            sustain_samples = 0
            release_samples = length - attack_samples - decay_samples
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > 0:
            decay_start = attack_samples
            decay_end = decay_start + decay_samples
            envelope[decay_start:decay_end] = np.linspace(1, sustain_level, decay_samples)
        
        # Sustain
        if sustain_samples > 0:
            sustain_start = attack_samples + decay_samples
            sustain_end = sustain_start + sustain_samples
            envelope[sustain_start:sustain_end] = sustain_level
        
        # Release
        if release_samples > 0:
            release_start = length - release_samples
            envelope[release_start:] = np.linspace(sustain_level, 0, release_samples)
        
        return envelope


class GenreMoodProcessor:
    """Advanced genre and mood processing with style transfer capabilities"""
    
    def __init__(self):
        self.genre_characteristics = self._load_genre_characteristics()
        self.mood_parameters = self._load_mood_parameters()
        
    def _load_genre_characteristics(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive genre characteristics"""
        return {
            'pop': {
                'tempo_range': (100, 130),
                'chord_complexity': 'simple',
                'rhythm_pattern': '4/4',
                'instrument_priority': ['acoustic_piano', 'electric_guitar', 'bass_guitar', 'acoustic_drums'],
                'harmonic_profile': [1.0, 0.6, 0.3, 0.15],
                'dynamic_range': (0.4, 0.8)
            },
            'rock': {
                'tempo_range': (110, 160),
                'chord_complexity': 'moderate',
                'rhythm_pattern': '4/4',
                'instrument_priority': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'organ'],
                'harmonic_profile': [1.0, 0.8, 0.4, 0.2],
                'dynamic_range': (0.6, 1.0)
            },
            'jazz': {
                'tempo_range': (80, 200),
                'chord_complexity': 'complex',
                'rhythm_pattern': 'swing',
                'instrument_priority': ['acoustic_piano', 'bass_guitar', 'acoustic_drums', 'trumpet', 'saxophone'],
                'harmonic_profile': [1.0, 0.5, 0.7, 0.3, 0.4],
                'dynamic_range': (0.3, 0.9)
            },
            'classical': {
                'tempo_range': (60, 180),
                'chord_complexity': 'complex',
                'rhythm_pattern': 'varied',
                'instrument_priority': ['acoustic_piano', 'violin', 'cello', 'flute', 'trumpet'],
                'harmonic_profile': [1.0, 0.7, 0.5, 0.3, 0.2, 0.1],
                'dynamic_range': (0.2, 1.0)
            },
            'electronic': {
                'tempo_range': (120, 140),
                'chord_complexity': 'simple',
                'rhythm_pattern': '4/4',
                'instrument_priority': ['synthesizer', 'electronic_drums', 'bass_guitar'],
                'harmonic_profile': [1.0, 0.4, 0.6, 0.2, 0.3],
                'dynamic_range': (0.5, 1.0)
            },
            'blues': {
                'tempo_range': (60, 120),
                'chord_complexity': 'simple',
                'rhythm_pattern': '12-bar',
                'instrument_priority': ['electric_guitar', 'acoustic_piano', 'bass_guitar', 'acoustic_drums'],
                'harmonic_profile': [1.0, 0.7, 0.5, 0.4],
                'dynamic_range': (0.4, 0.8)
            }
        }
    
    def _load_mood_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Load mood parameter modifications"""
        return {
            'happy': {
                'tempo_modifier': 1.1,
                'key_preference': 'major',
                'brightness': 1.2,
                'rhythm_energy': 1.1
            },
            'sad': {
                'tempo_modifier': 0.8,
                'key_preference': 'minor',
                'brightness': 0.7,
                'rhythm_energy': 0.8
            },
            'energetic': {
                'tempo_modifier': 1.3,
                'key_preference': 'major',
                'brightness': 1.4,
                'rhythm_energy': 1.4
            },
            'calm': {
                'tempo_modifier': 0.7,
                'key_preference': 'major',
                'brightness': 0.8,
                'rhythm_energy': 0.6
            },
            'romantic': {
                'tempo_modifier': 0.9,
                'key_preference': 'major',
                'brightness': 0.9,
                'rhythm_energy': 0.8
            },
            'mysterious': {
                'tempo_modifier': 0.8,
                'key_preference': 'minor',
                'brightness': 0.6,
                'rhythm_energy': 0.7
            },
            'epic': {
                'tempo_modifier': 1.2,
                'key_preference': 'major',
                'brightness': 1.3,
                'rhythm_energy': 1.3
            }
        }
    
    def apply_genre_style(self, base_params: Dict[str, Any], genre: str) -> Dict[str, Any]:
        """Apply genre-specific styling to generation parameters"""
        if genre not in self.genre_characteristics:
            genre = 'pop'  # Default fallback
        
        genre_data = self.genre_characteristics[genre]
        styled_params = base_params.copy()
        
        # Apply genre modifications
        styled_params['genre_data'] = genre_data
        styled_params['preferred_instruments'] = genre_data['instrument_priority']
        styled_params['harmonic_profile'] = genre_data['harmonic_profile']
        styled_params['dynamic_range'] = genre_data['dynamic_range']
        
        return styled_params
    
    def apply_mood_style(self, base_params: Dict[str, Any], mood: str) -> Dict[str, Any]:
        """Apply mood-specific styling to generation parameters"""
        if mood not in self.mood_parameters:
            mood = 'happy'  # Default fallback
        
        mood_data = self.mood_parameters[mood]
        styled_params = base_params.copy()
        
        # Apply mood modifications
        if 'tempo_bpm' in styled_params:
            styled_params['tempo_bpm'] = int(styled_params['tempo_bpm'] * mood_data['tempo_modifier'])
        
        styled_params['mood_data'] = mood_data
        styled_params['brightness'] = mood_data['brightness']
        styled_params['rhythm_energy'] = mood_data['rhythm_energy']
        
        return styled_params


# This will be continued in the next file...
