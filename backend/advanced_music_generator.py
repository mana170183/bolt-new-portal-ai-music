"""
🎵 Advanced Multi-Instrumental Music Generator
Supports multiple instruments, lyrics integration, and diverse musical arrangements
"""

import numpy as np
import soundfile as sf
import librosa
from scipy import signal
import random
import json
from typing import Dict, List, Optional, Tuple
import tempfile
import os

class InstrumentSynthesizer:
    """Synthesizes different instrument sounds using advanced DSP techniques"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
    def generate_piano(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """Generate piano-like sound with harmonics and ADSR envelope"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Piano harmonics (fundamental + overtones)
        harmonics = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
        signal = np.zeros_like(t)
        
        for i, harm_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            if harmonic_freq < self.sample_rate / 2:  # Nyquist limit
                signal += harm_amp * np.sin(2 * np.pi * harmonic_freq * t)
        
        # ADSR envelope (Attack, Decay, Sustain, Release)
        envelope = self._create_adsr_envelope(len(t), 0.1, 0.3, 0.4, 0.2)
        return signal * envelope * amplitude
    
    def generate_guitar(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """Generate guitar-like sound with string characteristics"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Guitar-like harmonics
        signal = (np.sin(2 * np.pi * frequency * t) + 
                 0.3 * np.sin(2 * np.pi * frequency * 2 * t) +
                 0.2 * np.sin(2 * np.pi * frequency * 3 * t) +
                 0.1 * np.sin(2 * np.pi * frequency * 4 * t))
        
        # Add slight detuning for realism
        detuned = np.sin(2 * np.pi * frequency * 1.002 * t) * 0.1
        signal += detuned
        
        # String pluck envelope
        envelope = np.exp(-3 * t) * (1 - np.exp(-20 * t))
        return signal * envelope * amplitude
    
    def generate_drums(self, drum_type: str, duration: float = 0.5, amplitude: float = 0.7) -> np.ndarray:
        """Generate drum sounds (kick, snare, hihat)"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        if drum_type == 'kick':
            # Low frequency thump with quick decay
            frequency = 60
            signal = np.sin(2 * np.pi * frequency * t) + 0.5 * np.sin(2 * np.pi * frequency * 0.5 * t)
            envelope = np.exp(-8 * t)
            
        elif drum_type == 'snare':
            # High frequency noise with mid tone
            noise = np.random.normal(0, 0.3, len(t))
            tone = np.sin(2 * np.pi * 200 * t)
            signal = 0.7 * noise + 0.3 * tone
            envelope = np.exp(-15 * t)
            
        elif drum_type == 'hihat':
            # High frequency noise
            signal = np.random.normal(0, 0.2, len(t))
            # High-pass filter
            sos = signal.butter(4, 8000, btype='high', fs=self.sample_rate, output='sos')
            signal = signal.sosfilt(sos, signal)
            envelope = np.exp(-25 * t)
            
        else:
            return np.zeros(len(t))
            
        return signal * envelope * amplitude
    
    def generate_bass(self, frequency: float, duration: float, amplitude: float = 0.6) -> np.ndarray:
        """Generate bass guitar sound"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Bass harmonics (emphasized fundamental)
        signal = (np.sin(2 * np.pi * frequency * t) + 
                 0.3 * np.sin(2 * np.pi * frequency * 2 * t) +
                 0.1 * np.sin(2 * np.pi * frequency * 3 * t))
        
        # Low-pass filter for bass character
        sos = signal.butter(4, 800, btype='low', fs=self.sample_rate, output='sos')
        signal = signal.sosfilt(sos, signal)
        
        # Bass envelope
        envelope = np.exp(-2 * t) * (1 - np.exp(-10 * t))
        return signal * envelope * amplitude
    
    def generate_strings(self, frequency: float, duration: float, amplitude: float = 0.4) -> np.ndarray:
        """Generate string section sound"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Rich harmonic content for strings
        harmonics = [1.0, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1]
        signal = np.zeros_like(t)
        
        for i, harm_amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            if harmonic_freq < self.sample_rate / 2:
                # Add slight vibrato
                vibrato = 1 + 0.02 * np.sin(2 * np.pi * 5 * t)
                signal += harm_amp * np.sin(2 * np.pi * harmonic_freq * t * vibrato)
        
        # Slow attack for strings
        envelope = 1 - np.exp(-3 * t)
        return signal * envelope * amplitude
    
    def _create_adsr_envelope(self, length: int, attack: float, decay: float, 
                            sustain: float, release: float) -> np.ndarray:
        """Create ADSR envelope"""
        envelope = np.ones(length)
        
        attack_samples = int(length * attack)
        decay_samples = int(length * decay)
        release_samples = int(length * release)
        sustain_samples = length - attack_samples - decay_samples - release_samples
        
        # Attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        decay_start = attack_samples
        decay_end = decay_start + decay_samples
        envelope[decay_start:decay_end] = np.linspace(1, 0.7, decay_samples)
        
        # Sustain
        sustain_start = decay_end
        sustain_end = sustain_start + sustain_samples
        envelope[sustain_start:sustain_end] = 0.7
        
        # Release
        release_start = sustain_end
        envelope[release_start:] = np.linspace(0.7, 0, release_samples)
        
        return envelope


class ChordProgressionGenerator:
    """Generates chord progressions based on genre and mood"""
    
    def __init__(self):
        # Common chord progressions by genre
        self.progressions = {
            'pop': [
                ['C', 'Am', 'F', 'G'],      # vi-IV-I-V
                ['Am', 'F', 'C', 'G'],      # vi-IV-I-V
                ['C', 'G', 'Am', 'F'],      # I-V-vi-IV
                ['F', 'G', 'C', 'Am'],      # IV-V-I-vi
            ],
            'rock': [
                ['C', 'F', 'G', 'C'],       # I-IV-V-I
                ['Am', 'F', 'C', 'G'],      # vi-IV-I-V
                ['C', 'Bb', 'F', 'C'],      # I-bVII-IV-I
                ['E', 'A', 'B', 'E'],       # I-IV-V-I in E
            ],
            'jazz': [
                ['Cmaj7', 'A7', 'Dm7', 'G7'],     # ii-V-I variations
                ['Am7', 'D7', 'Gmaj7', 'C7'],
                ['Fmaj7', 'Bm7b5', 'Em7', 'Am7'],
                ['Dm7', 'G7', 'Cmaj7', 'Fmaj7'],
            ],
            'blues': [
                ['C7', 'C7', 'C7', 'C7'],       # 12-bar blues
                ['F7', 'F7', 'C7', 'C7'],
                ['G7', 'F7', 'C7', 'G7'],
            ],
            'folk': [
                ['C', 'F', 'G', 'C'],       # Simple progressions
                ['Am', 'F', 'C', 'G'],
                ['C', 'Am', 'Dm', 'G'],
                ['F', 'C', 'G', 'Am'],
            ]
        }
        
        # Note frequencies (C4 = middle C)
        self.note_frequencies = {
            'C': 261.63, 'C#': 277.18, 'Db': 277.18,
            'D': 293.66, 'D#': 311.13, 'Eb': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'Gb': 369.99,
            'G': 392.00, 'G#': 415.30, 'Ab': 415.30,
            'A': 440.00, 'A#': 466.16, 'Bb': 466.16,
            'B': 493.88
        }
        
        # Chord definitions (intervals from root)
        self.chord_intervals = {
            'major': [0, 4, 7],
            'minor': [0, 3, 7],
            '7': [0, 4, 7, 10],
            'maj7': [0, 4, 7, 11],
            'm7': [0, 3, 7, 10],
            'm7b5': [0, 3, 6, 10],
        }
    
    def get_progression(self, genre: str, mood: str) -> List[str]:
        """Get chord progression based on genre and mood"""
        if genre.lower() not in self.progressions:
            genre = 'pop'  # Default
            
        progressions = self.progressions[genre.lower()]
        
        # Modify based on mood
        if mood.lower() in ['sad', 'melancholic', 'depressive']:
            # Prefer minor progressions
            progressions = [p for p in progressions if any('m' in chord.lower() for chord in p)]
            if not progressions:
                progressions = [['Am', 'F', 'C', 'G']]
                
        elif mood.lower() in ['happy', 'upbeat', 'energetic']:
            # Prefer major progressions
            progressions = [p for p in progressions if not any('m' in chord.lower() for chord in p)]
            if not progressions:
                progressions = [['C', 'F', 'G', 'C']]
        
        return random.choice(progressions)
    
    def chord_to_frequencies(self, chord_name: str) -> List[float]:
        """Convert chord name to list of frequencies"""
        # Parse chord name
        root = chord_name[0]
        if len(chord_name) > 1 and chord_name[1] in ['#', 'b']:
            root += chord_name[1]
            suffix = chord_name[2:]
        else:
            suffix = chord_name[1:]
        
        # Determine chord type
        if suffix == '':
            chord_type = 'major'
        elif suffix.lower() == 'm':
            chord_type = 'minor'
        elif suffix == '7':
            chord_type = '7'
        elif suffix.lower() == 'maj7':
            chord_type = 'maj7'
        elif suffix.lower() == 'm7':
            chord_type = 'm7'
        elif suffix.lower() == 'm7b5':
            chord_type = 'm7b5'
        else:
            chord_type = 'major'  # Default
        
        # Get root frequency
        root_freq = self.note_frequencies.get(root, 261.63)  # Default to C
        
        # Calculate chord frequencies
        intervals = self.chord_intervals[chord_type]
        frequencies = []
        for interval in intervals:
            # Calculate frequency using equal temperament
            freq = root_freq * (2 ** (interval / 12))
            frequencies.append(freq)
        
        return frequencies


class AdvancedMultiInstrumentalGenerator:
    """Advanced music generator supporting multiple instruments and complex arrangements"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.synthesizer = InstrumentSynthesizer(sample_rate)
        self.chord_generator = ChordProgressionGenerator()
        
        # Available instruments
        self.instruments = [
            'piano', 'guitar', 'bass', 'drums', 'strings', 'synthesizer'
        ]
        
        # Tempo mappings
        self.tempo_ranges = {
            'ballad': (60, 80),
            'moderate': (80, 120),
            'upbeat': (120, 140),
            'fast': (140, 180),
            'energetic': (160, 200)
        }
    
    def generate_composition(self, params: Dict) -> Tuple[np.ndarray, Dict]:
        """
        Generate a complete multi-instrumental composition
        
        Args:
            params: Dictionary containing:
                - lyrics: str (optional)
                - mood: str 
                - genre: str
                - instruments: List[str]
                - tempo_bpm: int (optional)
                - duration: float
                - key: str (optional)
        
        Returns:
            Tuple of (audio_array, metadata)
        """
        # Extract parameters
        lyrics = params.get('lyrics', '')
        mood = params.get('mood', 'moderate')
        genre = params.get('genre', 'pop')
        instruments = params.get('instruments', ['piano', 'guitar', 'bass', 'drums'])
        duration = params.get('duration', 30.0)
        tempo_bpm = params.get('tempo_bpm', self._get_tempo_for_mood(mood))
        key = params.get('key', 'C')
        
        # Generate chord progression
        chord_progression = self.chord_generator.get_progression(genre, mood)
        
        # Calculate timing
        beats_per_second = tempo_bpm / 60
        chord_duration = 2.0 / beats_per_second  # Each chord lasts 2 beats
        total_samples = int(duration * self.sample_rate)
        
        # Initialize mix
        final_mix = np.zeros(total_samples)
        
        # Generate each instrument track
        tracks = {}
        for instrument in instruments:
            if instrument in self.instruments:
                track = self._generate_instrument_track(
                    instrument, chord_progression, chord_duration, 
                    total_samples, tempo_bpm, mood, genre
                )
                tracks[instrument] = track
                final_mix += track
        
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(final_mix))
        if max_amplitude > 0:
            final_mix = final_mix / max_amplitude * 0.8
        
        # Generate metadata
        metadata = {
            'genre': genre,
            'mood': mood,
            'tempo_bpm': tempo_bpm,
            'key': key,
            'chord_progression': chord_progression,
            'instruments': instruments,
            'duration': duration,
            'sample_rate': self.sample_rate,
            'tracks': list(tracks.keys())
        }
        
        return final_mix, metadata
    
    def _generate_instrument_track(self, instrument: str, chord_progression: List[str], 
                                 chord_duration: float, total_samples: int, 
                                 tempo_bpm: int, mood: str, genre: str) -> np.ndarray:
        """Generate a single instrument track"""
        track = np.zeros(total_samples)
        current_sample = 0
        
        # Repeat progression to fill duration
        progression_cycles = int(total_samples / (len(chord_progression) * chord_duration * self.sample_rate)) + 1
        
        for cycle in range(progression_cycles):
            for chord_name in chord_progression:
                if current_sample >= total_samples:
                    break
                    
                chord_samples = int(chord_duration * self.sample_rate)
                end_sample = min(current_sample + chord_samples, total_samples)
                
                if instrument == 'drums':
                    chord_audio = self._generate_drum_pattern(chord_duration, tempo_bpm, mood)
                else:
                    chord_frequencies = self.chord_generator.chord_to_frequencies(chord_name)
                    chord_audio = self._generate_chord_audio(
                        instrument, chord_frequencies, chord_duration, mood, genre
                    )
                
                # Add to track
                actual_length = min(len(chord_audio), end_sample - current_sample)
                track[current_sample:current_sample + actual_length] += chord_audio[:actual_length]
                current_sample += chord_samples
        
        return track
    
    def _generate_chord_audio(self, instrument: str, frequencies: List[float], 
                            duration: float, mood: str, genre: str) -> np.ndarray:
        """Generate audio for a chord on a specific instrument"""
        if instrument == 'piano':
            # Piano plays all notes of the chord
            chord_audio = np.zeros(int(duration * self.sample_rate))
            for freq in frequencies:
                note_audio = self.synthesizer.generate_piano(freq, duration, 0.3)
                chord_audio += note_audio
            return chord_audio
            
        elif instrument == 'guitar':
            # Guitar strums the chord
            chord_audio = np.zeros(int(duration * self.sample_rate))
            for i, freq in enumerate(frequencies):
                strum_delay = i * 0.02  # Small delay between strings
                if strum_delay < duration:
                    note_duration = duration - strum_delay
                    note_audio = self.synthesizer.generate_guitar(freq, note_duration, 0.4)
                    start_sample = int(strum_delay * self.sample_rate)
                    end_sample = start_sample + len(note_audio)
                    if end_sample <= len(chord_audio):
                        chord_audio[start_sample:end_sample] += note_audio
            return chord_audio
            
        elif instrument == 'bass':
            # Bass plays root note
            root_freq = frequencies[0] / 2  # One octave lower
            return self.synthesizer.generate_bass(root_freq, duration, 0.5)
            
        elif instrument == 'strings':
            # Strings play sustained chord
            chord_audio = np.zeros(int(duration * self.sample_rate))
            for freq in frequencies:
                note_audio = self.synthesizer.generate_strings(freq, duration, 0.2)
                chord_audio += note_audio
            return chord_audio
            
        else:
            # Default to piano
            return self._generate_chord_audio('piano', frequencies, duration, mood, genre)
    
    def _generate_drum_pattern(self, duration: float, tempo_bpm: int, mood: str) -> np.ndarray:
        """Generate drum pattern for the given duration"""
        beats_per_second = tempo_bpm / 60
        beat_duration = 1.0 / beats_per_second
        num_beats = int(duration / beat_duration)
        
        pattern_audio = np.zeros(int(duration * self.sample_rate))
        
        for beat in range(num_beats):
            beat_start = beat * beat_duration
            
            # Kick drum on beats 1 and 3 (in 4/4 time)
            if beat % 4 in [0, 2]:
                kick = self.synthesizer.generate_drums('kick', 0.3, 0.6)
                start_sample = int(beat_start * self.sample_rate)
                end_sample = start_sample + len(kick)
                if end_sample <= len(pattern_audio):
                    pattern_audio[start_sample:end_sample] += kick
            
            # Snare on beats 2 and 4
            if beat % 4 in [1, 3]:
                snare = self.synthesizer.generate_drums('snare', 0.2, 0.5)
                start_sample = int(beat_start * self.sample_rate)
                end_sample = start_sample + len(snare)
                if end_sample <= len(pattern_audio):
                    pattern_audio[start_sample:end_sample] += snare
            
            # Hi-hat on every beat (if upbeat mood)
            if mood.lower() in ['upbeat', 'energetic']:
                hihat = self.synthesizer.generate_drums('hihat', 0.1, 0.3)
                start_sample = int(beat_start * self.sample_rate)
                end_sample = start_sample + len(hihat)
                if end_sample <= len(pattern_audio):
                    pattern_audio[start_sample:end_sample] += hihat
        
        return pattern_audio
    
    def _get_tempo_for_mood(self, mood: str) -> int:
        """Get appropriate tempo for mood"""
        mood_lower = mood.lower()
        if mood_lower in ['ballad', 'sad', 'melancholic']:
            return random.randint(*self.tempo_ranges['ballad'])
        elif mood_lower in ['moderate', 'neutral']:
            return random.randint(*self.tempo_ranges['moderate'])
        elif mood_lower in ['happy', 'upbeat']:
            return random.randint(*self.tempo_ranges['upbeat'])
        elif mood_lower in ['energetic', 'excited']:
            return random.randint(*self.tempo_ranges['energetic'])
        elif mood_lower in ['fast', 'intense']:
            return random.randint(*self.tempo_ranges['fast'])
        else:
            return random.randint(*self.tempo_ranges['moderate'])
    
    def export_stems(self, tracks: Dict[str, np.ndarray], output_dir: str) -> Dict[str, str]:
        """Export individual instrument tracks as separate files"""
        stem_files = {}
        
        for instrument, track in tracks.items():
            filename = f"{instrument}_stem.wav"
            filepath = os.path.join(output_dir, filename)
            sf.write(filepath, track, self.sample_rate)
            stem_files[instrument] = filepath
        
        return stem_files


# Example usage and testing
if __name__ == "__main__":
    generator = AdvancedMultiInstrumentalGenerator()
    
    # Test parameters
    test_params = {
        'lyrics': 'Walking down the street, feeling the beat',
        'mood': 'upbeat',
        'genre': 'pop',
        'instruments': ['piano', 'guitar', 'bass', 'drums'],
        'duration': 15.0,
        'tempo_bpm': 120
    }
    
    audio, metadata = generator.generate_composition(test_params)
    print("Generated composition metadata:", json.dumps(metadata, indent=2))
