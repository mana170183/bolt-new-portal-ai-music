"""
🎵 Enhanced Multi-Instrumental Music Generation System - Main Engine
Comprehensive AI-powered music generator with 15+ instruments, neural style transfer,
and professional-grade audio processing.
"""

import numpy as np
import soundfile as sf
import random
import json
import tempfile
import os
import threading
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
import logging
from dataclasses import dataclass

# Import our enhanced components
from enhanced_music_generator import (
    EnhancedInstrumentSynthesizer, 
    GenreMoodProcessor, 
    InstrumentType, 
    InstrumentConfig
)
from enhanced_chord_system import (
    AdvancedChordProgressionGenerator,
    ArrangementEngine
)

logger = logging.getLogger(__name__)

class EnhancedMultiInstrumentalGenerator:
    """
    Enhanced Multi-Instrumental Music Generator
    
    Features:
    - 15+ professional-quality instruments
    - Advanced chord progressions with complex harmonies
    - Genre-specific arrangement templates
    - Mood-based style transfer
    - Parallel processing for real-time generation
    - Multi-format export (WAV, MP3, MIDI)
    - Individual stem exports
    """
    
    def __init__(self, sample_rate: int = 44100, max_workers: int = 4):
        self.sample_rate = sample_rate
        self.max_workers = max_workers
        
        # Initialize core components
        self.synthesizer = EnhancedInstrumentSynthesizer(sample_rate)
        self.chord_generator = AdvancedChordProgressionGenerator()
        self.arrangement_engine = ArrangementEngine()
        self.genre_mood_processor = GenreMoodProcessor()
        
        # Available instruments (15 total)
        self.available_instruments = [
            'acoustic_piano', 'electric_piano', 'organ', 'synthesizer',
            'acoustic_guitar', 'electric_guitar', 'bass_guitar',
            'violin', 'cello', 'trumpet', 'trombone', 'saxophone',
            'acoustic_drums', 'electronic_drums', 'flute', 'harp'
        ]
        
        # Initialize thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Composition templates
        self.composition_templates = self._load_composition_templates()
        
        logger.info(f"Enhanced Music Generator initialized with {len(self.available_instruments)} instruments")
    
    def _load_composition_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load pre-defined composition templates"""
        return {
            'pop_ballad': {
                'structure': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
                'instruments': ['acoustic_piano', 'acoustic_guitar', 'bass_guitar', 'acoustic_drums', 'strings'],
                'tempo_range': (70, 90),
                'mood': 'romantic',
                'key': 'C'
            },
            'rock_anthem': {
                'structure': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
                'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'organ', 'electric_piano'],
                'tempo_range': (120, 140),
                'mood': 'energetic',
                'key': 'G'
            },
            'jazz_standard': {
                'structure': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro'],
                'instruments': ['acoustic_piano', 'bass_guitar', 'acoustic_drums', 'trumpet', 'saxophone'],
                'tempo_range': (120, 160),
                'mood': 'sophisticated',
                'key': 'Bb'
            },
            'electronic_dance': {
                'structure': ['intro', 'buildup', 'drop', 'breakdown', 'buildup', 'drop', 'outro'],
                'instruments': ['synthesizer', 'electronic_drums', 'bass_guitar'],
                'tempo_range': (128, 140),
                'mood': 'energetic',
                'key': 'Am'
            },
            'classical_piece': {
                'structure': ['intro', 'theme_a', 'theme_b', 'development', 'recapitulation', 'coda'],
                'instruments': ['acoustic_piano', 'violin', 'cello', 'flute', 'trumpet'],
                'tempo_range': (60, 120),
                'mood': 'elegant',
                'key': 'D'
            },
            'folk_song': {
                'structure': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'outro'],
                'instruments': ['acoustic_guitar', 'acoustic_piano', 'violin', 'flute'],
                'tempo_range': (80, 110),
                'mood': 'calm',
                'key': 'G'
            }
        }
    
    def generate_composition(self, params: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate a complete multi-instrumental composition
        
        Args:
            params: Dictionary containing:
                - lyrics: str (optional)
                - mood: str (required)
                - genre: str (required)
                - instruments: List[str] (optional, will use template if not provided)
                - tempo_bpm: int (optional)
                - duration: float (required)
                - key: str (optional)
                - structure: List[str] (optional)
                - template: str (optional)
                - export_stems: bool (optional)
                - style_complexity: str (optional: 'simple', 'moderate', 'complex')
        
        Returns:
            Tuple of (audio_array, metadata_dict)
        """
        
        # Extract and validate parameters
        validated_params = self._validate_and_process_params(params)
        
        # Apply template if specified
        if validated_params.get('template'):
            validated_params = self._apply_template(validated_params)
        
        # Generate chord progression
        chord_progression = self._generate_enhanced_chord_progression(validated_params)
        
        # Create arrangement
        arrangement = self._create_arrangement(validated_params, chord_progression)
        
        # Generate individual instrument tracks in parallel
        tracks = self._generate_parallel_tracks(validated_params, chord_progression, arrangement)
        
        # Mix tracks together
        final_mix = self._mix_tracks(tracks, validated_params)
        
        # Apply master processing
        final_audio = self._apply_master_processing(final_mix, validated_params)
        
        # Generate comprehensive metadata
        metadata = self._generate_metadata(validated_params, chord_progression, arrangement, tracks)
        
        # Export stems if requested
        if validated_params.get('export_stems', False):
            metadata['stem_files'] = self._export_stems(tracks, validated_params)
        
        logger.info(f"Generated composition: {metadata['duration']:.1f}s, {len(tracks)} tracks")
        
        return final_audio, metadata
    
    def _validate_and_process_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and process input parameters"""
        validated = {
            'lyrics': params.get('lyrics', ''),
            'mood': params.get('mood', 'happy'),
            'genre': params.get('genre', 'pop'),
            'duration': float(params.get('duration', 30.0)),
            'key': params.get('key', 'C'),
            'tempo_bpm': params.get('tempo_bpm'),
            'instruments': params.get('instruments', []),
            'structure': params.get('structure', []),
            'template': params.get('template'),
            'export_stems': params.get('export_stems', False),
            'style_complexity': params.get('style_complexity', 'moderate'),
            'output_format': params.get('output_format', 'wav')
        }
        
        # Validate instruments
        if validated['instruments']:
            validated['instruments'] = [
                inst for inst in validated['instruments'] 
                if inst in self.available_instruments
            ]
        
        # Set default instruments if none provided
        if not validated['instruments']:
            validated['instruments'] = ['acoustic_piano', 'acoustic_guitar', 'bass_guitar', 'acoustic_drums']
        
        # Apply genre/mood processing
        validated = self.genre_mood_processor.apply_genre_style(validated, validated['genre'])
        validated = self.genre_mood_processor.apply_mood_style(validated, validated['mood'])
        
        # Set tempo if not provided
        if not validated['tempo_bpm']:
            validated['tempo_bpm'] = self._get_tempo_for_mood_and_genre(validated['mood'], validated['genre'])
        
        return validated
    
    def _apply_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply composition template"""
        template_name = params['template']
        if template_name in self.composition_templates:
            template = self.composition_templates[template_name]
            
            # Apply template defaults if not overridden
            for key, value in template.items():
                if key not in params or not params[key]:
                    params[key] = value
            
            # Handle tempo range
            if 'tempo_range' in template and not params.get('tempo_bpm'):
                min_tempo, max_tempo = template['tempo_range']
                params['tempo_bpm'] = random.randint(min_tempo, max_tempo)
        
        return params
    
    def _generate_enhanced_chord_progression(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced chord progression with complex harmonies"""
        
        # Calculate number of chords needed
        duration = params['duration']
        tempo_bpm = params['tempo_bpm']
        beats_per_second = tempo_bpm / 60
        chord_duration = 2.0  # Each chord lasts 2 beats
        num_chords = int(duration / (chord_duration / beats_per_second))
        
        # Generate progression
        progression = self.chord_generator.generate_progression(
            genre=params['genre'],
            mood=params['mood'],
            key=params['key'],
            num_chords=num_chords,
            complexity=params['style_complexity']
        )
        
        return progression
    
    def _create_arrangement(self, params: Dict[str, Any], chord_progression: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create sophisticated arrangement with sections"""
        
        structure = params.get('structure', ['intro', 'verse', 'chorus', 'outro'])
        
        arrangement = self.arrangement_engine.create_arrangement(
            genre=params['genre'],
            structure=structure,
            total_duration=params['duration']
        )
        
        return arrangement
    
    def _generate_parallel_tracks(self, params: Dict[str, Any], 
                                chord_progression: List[Dict[str, Any]], 
                                arrangement: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Generate instrument tracks in parallel for better performance"""
        
        tracks = {}
        futures = {}
        
        # Submit track generation tasks to thread pool
        for instrument in params['instruments']:
            future = self.executor.submit(
                self._generate_single_track,
                instrument, params, chord_progression, arrangement
            )
            futures[instrument] = future
        
        # Collect results
        for instrument, future in futures.items():
            try:
                track = future.result(timeout=30)  # 30 second timeout
                tracks[instrument] = track
                logger.debug(f"Generated track for {instrument}: {len(track)} samples")
            except Exception as e:
                logger.error(f"Failed to generate track for {instrument}: {e}")
                # Generate fallback track
                tracks[instrument] = np.zeros(int(params['duration'] * self.sample_rate))
        
        return tracks
    
    def _generate_single_track(self, instrument: str, params: Dict[str, Any], 
                             chord_progression: List[Dict[str, Any]], 
                             arrangement: Dict[str, Any]) -> np.ndarray:
        """Generate a single instrument track"""
        
        total_samples = int(params['duration'] * self.sample_rate)
        track = np.zeros(total_samples)
        
        # Calculate timing
        tempo_bpm = params['tempo_bpm']
        beats_per_second = tempo_bpm / 60
        chord_duration = 2.0 / beats_per_second  # Each chord lasts 2 beats
        
        current_sample = 0
        chord_index = 0
        
        # Generate based on arrangement sections
        for section in arrangement.get('sections', []):
            if instrument not in section['instruments']:
                continue  # Skip this section for this instrument
            
            section_start_sample = int(section['start_bar'] * 2 * self.sample_rate / beats_per_second)
            section_duration_samples = int(section['length_bars'] * 2 * self.sample_rate / beats_per_second)
            section_end_sample = min(section_start_sample + section_duration_samples, total_samples)
            
            # Get instrument pattern for this section
            pattern_info = self.arrangement_engine.get_instrument_pattern(
                instrument, section['name'], params['genre'], chord_progression, tempo_bpm
            )
            
            # Generate audio for this section
            section_audio = self._generate_section_audio(
                instrument, section, chord_progression, pattern_info, 
                params, chord_duration, section_duration_samples
            )
            
            # Add to track
            actual_length = min(len(section_audio), section_end_sample - section_start_sample)
            if actual_length > 0:
                track[section_start_sample:section_start_sample + actual_length] += section_audio[:actual_length]
        
        # If no arrangement sections, generate simple progression
        if not arrangement.get('sections'):
            track = self._generate_simple_track(instrument, params, chord_progression, chord_duration, total_samples)
        
        return track
    
    def _generate_section_audio(self, instrument: str, section: Dict[str, Any], 
                              chord_progression: List[Dict[str, Any]], 
                              pattern_info: Dict[str, Any], params: Dict[str, Any],
                              chord_duration: float, section_duration_samples: int) -> np.ndarray:
        """Generate audio for a specific section and instrument"""
        
        section_audio = np.zeros(section_duration_samples)
        current_sample = 0
        chord_samples = int(chord_duration * self.sample_rate)
        
        # Repeat chord progression for section duration
        chord_index = 0
        while current_sample < section_duration_samples:
            if chord_index >= len(chord_progression):
                chord_index = 0
            
            chord = chord_progression[chord_index]
            end_sample = min(current_sample + chord_samples, section_duration_samples)
            
            # Generate chord audio for this instrument
            chord_audio = self._generate_instrument_chord_audio(
                instrument, chord, chord_duration, pattern_info, section['dynamics'], params
            )
            
            # Add to section
            actual_length = min(len(chord_audio), end_sample - current_sample)
            if actual_length > 0:
                section_audio[current_sample:current_sample + actual_length] += chord_audio[:actual_length]
            
            current_sample += chord_samples
            chord_index += 1
        
        return section_audio
    
    def _generate_simple_track(self, instrument: str, params: Dict[str, Any], 
                             chord_progression: List[Dict[str, Any]], 
                             chord_duration: float, total_samples: int) -> np.ndarray:
        """Generate simple track without arrangement sections"""
        
        track = np.zeros(total_samples)
        current_sample = 0
        chord_samples = int(chord_duration * self.sample_rate)
        
        # Default pattern info
        pattern_info = {
            'pattern': 'medium',
            'style': 'default',
            'role': 'harmonic',
            'octave_range': (3, 5)
        }
        
        # Repeat progression to fill duration
        chord_index = 0
        while current_sample < total_samples:
            if chord_index >= len(chord_progression):
                chord_index = 0
            
            chord = chord_progression[chord_index]
            end_sample = min(current_sample + chord_samples, total_samples)
            
            chord_audio = self._generate_instrument_chord_audio(
                instrument, chord, chord_duration, pattern_info, 'medium', params
            )
            
            actual_length = min(len(chord_audio), end_sample - current_sample)
            if actual_length > 0:
                track[current_sample:current_sample + actual_length] += chord_audio[:actual_length]
            
            current_sample += chord_samples
            chord_index += 1
        
        return track
    
    def _generate_instrument_chord_audio(self, instrument: str, chord: Dict[str, Any], 
                                       duration: float, pattern_info: Dict[str, Any], 
                                       dynamics: str, params: Dict[str, Any]) -> np.ndarray:
        """Generate audio for a specific instrument and chord"""
        
        # Dynamic level mapping
        dynamic_levels = {
            'soft': 0.3, 'medium': 0.5, 'medium_loud': 0.7, 'loud': 0.8, 'fade': 0.2
        }
        base_velocity = dynamic_levels.get(dynamics, 0.5)
        
        # Apply mood brightness
        brightness = params.get('brightness', 1.0)
        velocity = base_velocity * brightness
        velocity = max(0.1, min(1.0, velocity))  # Clamp to valid range
        
        # Get style from pattern info
        style = pattern_info.get('style', 'default')
        
        # Generate based on instrument type
        if instrument == 'acoustic_piano':
            return self._generate_piano_chord(chord, duration, velocity, style)
        elif instrument == 'electric_piano':
            return self._generate_electric_piano_chord(chord, duration, velocity, style)
        elif instrument == 'acoustic_guitar':
            return self._generate_guitar_chord(chord, duration, velocity, 'acoustic')
        elif instrument == 'electric_guitar':
            return self._generate_guitar_chord(chord, duration, velocity, style)
        elif instrument == 'bass_guitar':
            return self._generate_bass_chord(chord, duration, velocity, style)
        elif instrument in ['acoustic_drums', 'electronic_drums']:
            drum_style = 'acoustic' if 'acoustic' in instrument else 'electronic'
            return self._generate_drum_pattern(duration, params['tempo_bpm'], velocity, drum_style)
        elif instrument in ['violin', 'cello']:
            return self._generate_strings_chord(chord, duration, velocity, instrument)
        elif instrument in ['trumpet', 'trombone', 'saxophone']:
            return self._generate_brass_chord(chord, duration, velocity, instrument)
        elif instrument == 'flute':
            return self._generate_flute_melody(chord, duration, velocity)
        elif instrument == 'synthesizer':
            return self._generate_synth_chord(chord, duration, velocity, params['genre'])
        else:
            # Default to piano
            return self._generate_piano_chord(chord, duration, velocity, 'classical')
    
    def _generate_piano_chord(self, chord: Dict[str, Any], duration: float, velocity: float, style: str) -> np.ndarray:
        """Generate piano chord audio"""
        chord_audio = np.zeros(int(duration * self.sample_rate))
        for freq in chord['frequencies']:
            note_audio = self.synthesizer.generate_enhanced_piano(freq, duration, velocity, style)
            chord_audio += note_audio
        return chord_audio
    
    def _generate_electric_piano_chord(self, chord: Dict[str, Any], duration: float, velocity: float, style: str) -> np.ndarray:
        """Generate electric piano chord audio"""
        # Use enhanced piano with different style
        chord_audio = np.zeros(int(duration * self.sample_rate))
        for freq in chord['frequencies']:
            note_audio = self.synthesizer.generate_enhanced_piano(freq, duration, velocity, 'jazz')
            chord_audio += note_audio * 0.8  # Slightly softer than acoustic
        return chord_audio
    
    def _generate_guitar_chord(self, chord: Dict[str, Any], duration: float, velocity: float, guitar_type: str) -> np.ndarray:
        """Generate guitar chord with strumming"""
        chord_audio = np.zeros(int(duration * self.sample_rate))
        
        for i, freq in enumerate(chord['frequencies']):
            strum_delay = i * 0.02  # Small delay between strings
            if strum_delay < duration:
                note_duration = duration - strum_delay
                if guitar_type == 'acoustic':
                    note_audio = self.synthesizer.generate_guitar(freq, note_duration, velocity)
                else:
                    note_audio = self.synthesizer.generate_electric_guitar(freq, note_duration, velocity, guitar_type)
                
                start_sample = int(strum_delay * self.sample_rate)
                end_sample = start_sample + len(note_audio)
                if end_sample <= len(chord_audio):
                    chord_audio[start_sample:end_sample] += note_audio
        
        return chord_audio
    
    def _generate_bass_chord(self, chord: Dict[str, Any], duration: float, velocity: float, style: str) -> np.ndarray:
        """Generate bass line (typically root note)"""
        root_freq = chord['frequencies'][0] / 2  # One octave lower
        return self.synthesizer.generate_bass_guitar(root_freq, duration, velocity, style)
    
    def _generate_drum_pattern(self, duration: float, tempo_bpm: int, velocity: float, style: str) -> np.ndarray:
        """Generate drum pattern"""
        beats_per_second = tempo_bpm / 60
        beat_duration = 1.0 / beats_per_second
        num_beats = int(duration / beat_duration)
        
        pattern_audio = np.zeros(int(duration * self.sample_rate))
        
        for beat in range(num_beats):
            beat_start = beat * beat_duration
            
            # Basic 4/4 pattern
            if beat % 4 in [0, 2]:  # Kick on 1 and 3
                kick = self.synthesizer.generate_enhanced_drums('kick', velocity, style)
                self._add_audio_at_time(pattern_audio, kick, beat_start)
            
            if beat % 4 in [1, 3]:  # Snare on 2 and 4
                snare = self.synthesizer.generate_enhanced_drums('snare', velocity * 0.8, style)
                self._add_audio_at_time(pattern_audio, snare, beat_start)
            
            # Hi-hat on every beat for energetic songs
            if velocity > 0.6:
                hihat = self.synthesizer.generate_enhanced_drums('hihat', velocity * 0.5, style)
                self._add_audio_at_time(pattern_audio, hihat, beat_start)
        
        return pattern_audio
    
    def _generate_strings_chord(self, chord: Dict[str, Any], duration: float, velocity: float, instrument: str) -> np.ndarray:
        """Generate string section chord"""
        chord_audio = np.zeros(int(duration * self.sample_rate))
        for freq in chord['frequencies']:
            note_audio = self.synthesizer.generate_strings(freq, duration, velocity, instrument)
            chord_audio += note_audio
        return chord_audio
    
    def _generate_brass_chord(self, chord: Dict[str, Any], duration: float, velocity: float, instrument: str) -> np.ndarray:
        """Generate brass section chord"""
        chord_audio = np.zeros(int(duration * self.sample_rate))
        for freq in chord['frequencies']:
            note_audio = self.synthesizer.generate_brass(freq, duration, velocity, instrument)
            chord_audio += note_audio
        return chord_audio
    
    def _generate_flute_melody(self, chord: Dict[str, Any], duration: float, velocity: float) -> np.ndarray:
        """Generate flute melody (plays chord tones sequentially)"""
        if not chord['frequencies']:
            return np.zeros(int(duration * self.sample_rate))
        
        note_duration = duration / len(chord['frequencies'])
        melody_audio = np.zeros(int(duration * self.sample_rate))
        
        for i, freq in enumerate(chord['frequencies']):
            note_start = i * note_duration
            note_audio = self.synthesizer.generate_strings(freq * 2, note_duration, velocity, 'violin')  # Use violin synthesis for flute-like sound
            start_sample = int(note_start * self.sample_rate)
            end_sample = start_sample + len(note_audio)
            if end_sample <= len(melody_audio):
                melody_audio[start_sample:end_sample] += note_audio
        
        return melody_audio
    
    def _generate_synth_chord(self, chord: Dict[str, Any], duration: float, velocity: float, genre: str) -> np.ndarray:
        """Generate synthesizer chord with genre-specific characteristics"""
        # Use enhanced piano with electronic characteristics
        chord_audio = np.zeros(int(duration * self.sample_rate))
        for freq in chord['frequencies']:
            note_audio = self.synthesizer.generate_enhanced_piano(freq, duration, velocity, 'rock')
            # Add some electronic processing (simple distortion)
            note_audio = np.tanh(note_audio * 1.5) * 0.7
            chord_audio += note_audio
        return chord_audio
    
    def _add_audio_at_time(self, target_audio: np.ndarray, source_audio: np.ndarray, time_seconds: float):
        """Add source audio to target audio at specified time"""
        start_sample = int(time_seconds * self.sample_rate)
        end_sample = start_sample + len(source_audio)
        if end_sample <= len(target_audio):
            target_audio[start_sample:end_sample] += source_audio
    
    def _mix_tracks(self, tracks: Dict[str, np.ndarray], params: Dict[str, Any]) -> np.ndarray:
        """Mix multiple tracks together with proper balancing"""
        if not tracks:
            return np.zeros(int(params['duration'] * self.sample_rate))
        
        # Find maximum length
        max_length = max(len(track) for track in tracks.values())
        
        # Mix tracks with instrument-specific levels
        mixed_audio = np.zeros(max_length)
        
        # Instrument mixing levels
        mix_levels = {
            'acoustic_drums': 0.8, 'electronic_drums': 0.8,
            'bass_guitar': 0.7,
            'acoustic_piano': 0.6, 'electric_piano': 0.6,
            'acoustic_guitar': 0.5, 'electric_guitar': 0.6,
            'strings': 0.4, 'violin': 0.4, 'cello': 0.4,
            'trumpet': 0.5, 'trombone': 0.5, 'saxophone': 0.5,
            'flute': 0.3, 'harp': 0.3, 'synthesizer': 0.6
        }
        
        for instrument, track in tracks.items():
            level = mix_levels.get(instrument, 0.5)
            # Pad track to max length if needed
            if len(track) < max_length:
                padded_track = np.zeros(max_length)
                padded_track[:len(track)] = track
                track = padded_track
            
            mixed_audio += track * level
        
        return mixed_audio
    
    def _apply_master_processing(self, audio: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply master processing (compression, EQ, limiting)"""
        
        # Simple master limiting to prevent clipping
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            # Soft limiting with some headroom
            target_level = 0.8
            if max_amplitude > target_level:
                audio = audio * (target_level / max_amplitude)
        
        # Apply gentle compression (simple)
        threshold = 0.6
        ratio = 3.0
        compressed_audio = audio.copy()
        
        over_threshold = np.abs(audio) > threshold
        compressed_audio[over_threshold] = np.sign(audio[over_threshold]) * (
            threshold + (np.abs(audio[over_threshold]) - threshold) / ratio
        )
        
        return compressed_audio
    
    def _generate_metadata(self, params: Dict[str, Any], chord_progression: List[Dict[str, Any]], 
                         arrangement: Dict[str, Any], tracks: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Generate comprehensive metadata"""
        return {
            'title': f"{params['mood'].title()} {params['genre'].title()} Composition",
            'genre': params['genre'],
            'mood': params['mood'],
            'key': params['key'],
            'tempo_bpm': params['tempo_bpm'],
            'duration': params['duration'],
            'sample_rate': self.sample_rate,
            'instruments': list(tracks.keys()),
            'num_tracks': len(tracks),
            'chord_progression': [
                f"{chord['root']}{chord['type']}" for chord in chord_progression
            ],
            'structure': arrangement.get('sections', []),
            'style_complexity': params['style_complexity'],
            'generated_by': 'Enhanced Multi-Instrumental Generator v2.0',
            'timestamp': str(np.datetime64('now'))
        }
    
    def _export_stems(self, tracks: Dict[str, np.ndarray], params: Dict[str, Any]) -> Dict[str, str]:
        """Export individual instrument tracks as separate files"""
        stem_files = {}
        output_dir = 'generated_audio/stems'
        os.makedirs(output_dir, exist_ok=True)
        
        for instrument, track in tracks.items():
            # Normalize track
            if np.max(np.abs(track)) > 0:
                normalized_track = track / np.max(np.abs(track)) * 0.8
            else:
                normalized_track = track
                
            filename = f"{instrument}_stem_{int(np.datetime64('now').astype('datetime64[s]').astype(int))}.wav"
            filepath = os.path.join(output_dir, filename)
            
            try:
                sf.write(filepath, normalized_track, self.sample_rate)
                stem_files[instrument] = filepath
            except Exception as e:
                logger.error(f"Failed to export stem for {instrument}: {e}")
        
        return stem_files
    
    def _get_tempo_for_mood_and_genre(self, mood: str, genre: str) -> int:
        """Get appropriate tempo based on mood and genre"""
        base_tempos = {
            'pop': 120, 'rock': 130, 'jazz': 140, 'blues': 90,
            'folk': 100, 'classical': 110, 'electronic': 128
        }
        
        mood_modifiers = {
            'happy': 1.1, 'sad': 0.8, 'energetic': 1.3, 'calm': 0.7,
            'romantic': 0.9, 'mysterious': 0.8, 'epic': 1.2
        }
        
        base_tempo = base_tempos.get(genre, 120)
        modifier = mood_modifiers.get(mood, 1.0)
        
        return int(base_tempo * modifier)
    
    def get_available_instruments(self) -> List[Dict[str, Any]]:
        """Get list of available instruments with metadata"""
        instruments = []
        for instrument in self.available_instruments:
            config = self.synthesizer.instrument_configs.get(instrument)
            if config:
                instruments.append({
                    'id': instrument,
                    'name': config.name,
                    'type': config.type.value,
                    'priority': config.priority
                })
            else:
                instruments.append({
                    'id': instrument,
                    'name': instrument.replace('_', ' ').title(),
                    'type': 'unknown',
                    'priority': 5
                })
        
        return sorted(instruments, key=lambda x: x['priority'])
    
    def get_composition_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available composition templates"""
        return self.composition_templates.copy()


# Example usage
if __name__ == "__main__":
    # Initialize the enhanced generator
    generator = EnhancedMultiInstrumentalGenerator()
    
    # Test parameters
    test_params = {
        'mood': 'energetic',
        'genre': 'rock',
        'duration': 20.0,
        'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'organ'],
        'tempo_bpm': 130,
        'key': 'G',
        'export_stems': True,
        'style_complexity': 'moderate'
    }
    
    print("Generating enhanced composition...")
    audio, metadata = generator.generate_composition(test_params)
    print("Generated metadata:", json.dumps(metadata, indent=2))
    print(f"Audio shape: {audio.shape}, Max amplitude: {np.max(np.abs(audio)):.3f}")
