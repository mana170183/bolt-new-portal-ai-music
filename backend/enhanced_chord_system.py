"""
🎵 Enhanced Chord Progression and Arrangement System
Part 2 of the Enhanced Multi-Instrumental Music Generation System
"""

import numpy as np
import random
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading

class AdvancedChordProgressionGenerator:
    """Advanced chord progression generator with complex harmonic structures"""
    
    def __init__(self):
        self.note_frequencies = self._initialize_note_frequencies()
        self.chord_definitions = self._initialize_chord_definitions()
        self.progression_templates = self._initialize_progression_templates()
        self.scale_patterns = self._initialize_scale_patterns()
        
    def _initialize_note_frequencies(self) -> Dict[str, float]:
        """Initialize comprehensive note frequency mapping"""
        # A4 = 440 Hz as reference
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        frequencies = {}
        
        # Generate frequencies for octaves 0-8
        for octave in range(9):
            for i, note in enumerate(notes):
                # Calculate frequency using equal temperament
                semitone = octave * 12 + i - 57  # A4 is at position 57
                freq = 440 * (2 ** (semitone / 12))
                frequencies[f"{note}{octave}"] = freq
                
        # Add enharmonic equivalents
        enharmonics = {
            'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
        }
        
        for octave in range(9):
            for flat_note, sharp_note in enharmonics.items():
                frequencies[f"{flat_note}{octave}"] = frequencies[f"{sharp_note}{octave}"]
                
        return frequencies
    
    def _initialize_chord_definitions(self) -> Dict[str, List[int]]:
        """Initialize comprehensive chord definitions (semitone intervals)"""
        return {
            # Triads
            'major': [0, 4, 7],
            'minor': [0, 3, 7],
            'diminished': [0, 3, 6],
            'augmented': [0, 4, 8],
            
            # Seventh chords
            '7': [0, 4, 7, 10],           # Dominant 7th
            'maj7': [0, 4, 7, 11],        # Major 7th
            'm7': [0, 3, 7, 10],          # Minor 7th
            'm7b5': [0, 3, 6, 10],        # Half diminished
            'dim7': [0, 3, 6, 9],         # Diminished 7th
            'mMaj7': [0, 3, 7, 11],       # Minor major 7th
            
            # Extended chords
            '9': [0, 4, 7, 10, 14],       # Dominant 9th
            'maj9': [0, 4, 7, 11, 14],    # Major 9th
            'm9': [0, 3, 7, 10, 14],      # Minor 9th
            '11': [0, 4, 7, 10, 14, 17],  # Dominant 11th
            '13': [0, 4, 7, 10, 14, 21],  # Dominant 13th
            
            # Suspended chords
            'sus2': [0, 2, 7],
            'sus4': [0, 5, 7],
            '7sus4': [0, 5, 7, 10],
            
            # Add chords
            'add9': [0, 4, 7, 14],
            'madd9': [0, 3, 7, 14],
            
            # Slash chords (bass note modifications handled separately)
            '6': [0, 4, 7, 9],
            'm6': [0, 3, 7, 9],
            '6/9': [0, 4, 7, 9, 14]
        }
    
    def _initialize_progression_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize genre-specific chord progression templates"""
        return {
            'pop': {
                'common_progressions': [
                    ['I', 'V', 'vi', 'IV'],      # 1-5-6-4 (very common)
                    ['vi', 'IV', 'I', 'V'],      # 6-4-1-5
                    ['I', 'vi', 'IV', 'V'],      # 1-6-4-5
                    ['IV', 'V', 'vi', 'I'],      # 4-5-6-1
                    ['I', 'IV', 'vi', 'V'],      # 1-4-6-5
                ],
                'chord_types': ['major', 'minor', '7', 'sus4'],
                'complexity': 'simple'
            },
            'rock': {
                'common_progressions': [
                    ['I', 'bVII', 'IV', 'I'],    # 1-♭7-4-1
                    ['I', 'IV', 'V', 'I'],       # 1-4-5-1
                    ['vi', 'IV', 'I', 'V'],      # 6-4-1-5
                    ['I', 'bVII', 'IV', 'V'],    # 1-♭7-4-5
                    ['I', 'V', 'IV', 'I'],       # 1-5-4-1
                ],
                'chord_types': ['major', 'minor', '7', 'sus4', 'add9'],
                'complexity': 'moderate'
            },
            'jazz': {
                'common_progressions': [
                    ['IIM7', 'V7', 'Imaj7', 'VImaj7'],     # ii-V-I-VI
                    ['Imaj7', 'VIm7', 'IIm7', 'V7'],      # I-vi-ii-V
                    ['IIIm7', 'VIm7', 'IIm7', 'V7'],      # iii-vi-ii-V
                    ['Imaj7', 'IVM7', 'VIIm7b5', 'IIIm7'], # I-IV-vii-iii
                    ['IIm7', 'V7', 'Imaj7', 'IIm7', 'V7'], # Extended ii-V-I
                ],
                'chord_types': ['maj7', 'm7', '7', 'm7b5', 'dim7', '9', '11', '13'],
                'complexity': 'complex'
            },
            'blues': {
                'common_progressions': [
                    ['I7', 'I7', 'I7', 'I7', 'IV7', 'IV7', 'I7', 'I7', 'V7', 'IV7', 'I7', 'V7'],  # 12-bar blues
                    ['I7', 'IV7', 'I7', 'I7', 'IV7', 'IV7', 'I7', 'I7', 'V7', 'V7', 'I7', 'I7'],  # Traditional 12-bar
                    ['I7', 'I7', 'I7', 'I7'],              # Single chord blues
                ],
                'chord_types': ['7', '9', '13', 'sus4'],
                'complexity': 'moderate'
            },
            'folk': {
                'common_progressions': [
                    ['I', 'IV', 'V', 'I'],       # 1-4-5-1
                    ['I', 'vi', 'IV', 'V'],      # 1-6-4-5
                    ['vi', 'I', 'V', 'I'],       # 6-1-5-1
                    ['I', 'V', 'vi', 'V'],       # 1-5-6-5
                ],
                'chord_types': ['major', 'minor', 'sus4', 'add9'],
                'complexity': 'simple'
            },
            'classical': {
                'common_progressions': [
                    ['I', 'ii', 'V', 'I'],       # Classical cadence
                    ['I', 'IV', 'ii', 'V', 'I'], # Extended classical
                    ['vi', 'ii', 'V', 'I'],      # Minor to major
                    ['I', 'V', 'vi', 'iii', 'IV', 'I', 'ii', 'V'], # Extended classical
                ],
                'chord_types': ['major', 'minor', '7', 'dim', 'sus4'],
                'complexity': 'complex'
            },
            'electronic': {
                'common_progressions': [
                    ['i', 'bVII', 'bVI', 'bVII'], # Minor electronic
                    ['i', 'iv', 'bVII', 'i'],     # Dark electronic
                    ['I', 'V', 'vi', 'IV'],       # Major electronic
                    ['vi', 'I', 'bVII', 'IV'],    # Progressive electronic
                ],
                'chord_types': ['minor', 'major', '7', 'sus2', 'add9'],
                'complexity': 'moderate'
            }
        }
    
    def _initialize_scale_patterns(self) -> Dict[str, List[int]]:
        """Initialize scale patterns for chord generation"""
        return {
            'major': [0, 2, 4, 5, 7, 9, 11],          # Ionian
            'minor': [0, 2, 3, 5, 7, 8, 10],          # Natural minor
            'dorian': [0, 2, 3, 5, 7, 9, 10],         # Dorian
            'mixolydian': [0, 2, 4, 5, 7, 9, 10],     # Mixolydian
            'lydian': [0, 2, 4, 6, 7, 9, 11],         # Lydian
            'phrygian': [0, 1, 3, 5, 7, 8, 10],       # Phrygian
            'locrian': [0, 1, 3, 5, 6, 8, 10],        # Locrian
            'harmonic_minor': [0, 2, 3, 5, 7, 8, 11], # Harmonic minor
            'melodic_minor': [0, 2, 3, 5, 7, 9, 11],  # Melodic minor
            'blues': [0, 3, 5, 6, 7, 10],             # Blues scale
            'pentatonic': [0, 2, 4, 7, 9],            # Major pentatonic
            'minor_pentatonic': [0, 3, 5, 7, 10]      # Minor pentatonic
        }
    
    def generate_progression(self, genre: str, mood: str, key: str = 'C', 
                           num_chords: int = 4, complexity: str = 'auto') -> List[Dict[str, Any]]:
        """Generate a chord progression based on genre, mood, and key"""
        
        # Get genre template
        if genre not in self.progression_templates:
            genre = 'pop'  # Default fallback
        
        template = self.progression_templates[genre]
        
        # Determine complexity
        if complexity == 'auto':
            complexity = template['complexity']
        
        # Select base progression
        base_progression = random.choice(template['common_progressions'])
        
        # Extend or truncate to desired length
        if len(base_progression) < num_chords:
            # Repeat progression to reach desired length
            multiplier = (num_chords // len(base_progression)) + 1
            extended = (base_progression * multiplier)[:num_chords]
        else:
            extended = base_progression[:num_chords]
        
        # Convert roman numerals to actual chords
        chord_sequence = []
        for roman_numeral in extended:
            chord_info = self._roman_to_chord(roman_numeral, key, template['chord_types'], mood)
            chord_sequence.append(chord_info)
        
        # Apply mood modifications
        chord_sequence = self._apply_mood_to_progression(chord_sequence, mood)
        
        return chord_sequence
    
    def _roman_to_chord(self, roman: str, key: str, available_types: List[str], mood: str) -> Dict[str, Any]:
        """Convert roman numeral to actual chord with note names and frequencies"""
        
        # Parse roman numeral
        degree, chord_type = self._parse_roman_numeral(roman)
        
        # Get scale for the key
        if mood in ['sad', 'mysterious', 'melancholic']:
            scale = self.scale_patterns['minor']
        else:
            scale = self.scale_patterns['major']
        
        # Get root note
        key_root = key[0].upper()
        if len(key) > 1 and key[1] in ['#', 'b']:
            key_root += key[1]
        
        # Calculate chord root
        chord_root_semitone = scale[degree - 1]
        chord_root = self._transpose_note(key_root, chord_root_semitone)
        
        # Determine chord type if not specified
        if not chord_type:
            if mood in ['sad', 'mysterious']:
                chord_type = 'minor' if degree in [1, 4, 5] else 'major'
            else:
                chord_type = 'major' if degree in [1, 4, 5] else 'minor'
        
        # Ensure chord type is available
        if chord_type not in available_types:
            chord_type = random.choice(available_types)
        
        # Generate chord
        chord_notes = self._build_chord(chord_root, chord_type)
        chord_frequencies = [self.note_frequencies.get(f"{note}4", 261.63) for note in chord_notes]
        
        return {
            'roman': roman,
            'root': chord_root,
            'type': chord_type,
            'notes': chord_notes,
            'frequencies': chord_frequencies,
            'degree': degree
        }
    
    def _parse_roman_numeral(self, roman: str) -> Tuple[int, str]:
        """Parse roman numeral to get degree and chord type"""
        
        # Roman numeral mappings
        roman_to_degree = {
            'I': 1, 'i': 1, 'II': 2, 'ii': 2, 'III': 3, 'iii': 3,
            'IV': 4, 'iv': 4, 'V': 5, 'v': 5, 'VI': 6, 'vi': 6,
            'VII': 7, 'vii': 7, 'bVII': 7, 'bVI': 6, 'bII': 2, 'bIII': 3
        }
        
        # Extract base roman numeral
        base_roman = roman.split('7')[0].split('9')[0].split('11')[0].split('13')[0]
        base_roman = base_roman.replace('maj', '').replace('m', '').replace('b5', '').replace('sus', '').replace('add', '').replace('dim', '')
        
        degree = roman_to_degree.get(base_roman, 1)
        
        # Determine chord type from roman numeral
        chord_type = None
        if 'maj7' in roman:
            chord_type = 'maj7'
        elif 'm7b5' in roman:
            chord_type = 'm7b5'
        elif 'dim7' in roman:
            chord_type = 'dim7'
        elif 'm7' in roman:
            chord_type = 'm7'
        elif '7sus4' in roman:
            chord_type = '7sus4'
        elif '7' in roman:
            chord_type = '7'
        elif 'sus4' in roman:
            chord_type = 'sus4'
        elif 'sus2' in roman:
            chord_type = 'sus2'
        elif 'add9' in roman:
            chord_type = 'add9'
        elif 'dim' in roman:
            chord_type = 'diminished'
        elif roman.islower() or 'm' in roman:
            chord_type = 'minor'
        else:
            chord_type = 'major'
        
        return degree, chord_type
    
    def _transpose_note(self, note: str, semitones: int) -> str:
        """Transpose a note by a given number of semitones"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Handle flat notes
        if 'b' in note:
            note = note.replace('b', '')
            note_index = notes.index(note) - 1
        else:
            note_index = notes.index(note)
        
        # Transpose
        new_index = (note_index + semitones) % 12
        return notes[new_index]
    
    def _build_chord(self, root: str, chord_type: str) -> List[str]:
        """Build chord notes from root and type"""
        if chord_type not in self.chord_definitions:
            chord_type = 'major'  # Default
        
        intervals = self.chord_definitions[chord_type]
        chord_notes = []
        
        for interval in intervals:
            note = self._transpose_note(root, interval)
            chord_notes.append(note)
        
        return chord_notes
    
    def _apply_mood_to_progression(self, progression: List[Dict[str, Any]], mood: str) -> List[Dict[str, Any]]:
        """Apply mood-specific modifications to chord progression"""
        
        mood_modifications = {
            'sad': {'substitute_major_with_minor': 0.3, 'add_seventh': 0.4},
            'happy': {'substitute_minor_with_major': 0.2, 'add_sus4': 0.2},
            'mysterious': {'add_seventh': 0.5, 'add_diminished': 0.2},
            'energetic': {'add_sus4': 0.3, 'increase_complexity': 0.2},
            'romantic': {'add_maj7': 0.4, 'add_ninth': 0.2},
            'epic': {'add_sus4': 0.4, 'increase_volume': 0.3},
            'calm': {'simplify_chords': 0.3, 'add_maj7': 0.2}
        }
        
        if mood not in mood_modifications:
            return progression
        
        modifications = mood_modifications[mood]
        modified_progression = []
        
        for chord in progression:
            modified_chord = chord.copy()
            
            # Apply random modifications based on mood
            for mod_type, probability in modifications.items():
                if random.random() < probability:
                    modified_chord = self._apply_chord_modification(modified_chord, mod_type)
            
            modified_progression.append(modified_chord)
        
        return modified_progression
    
    def _apply_chord_modification(self, chord: Dict[str, Any], modification: str) -> Dict[str, Any]:
        """Apply a specific modification to a chord"""
        new_chord = chord.copy()
        
        if modification == 'add_seventh' and chord['type'] in ['major', 'minor']:
            new_chord['type'] = 'maj7' if chord['type'] == 'major' else 'm7'
            new_chord['notes'] = self._build_chord(chord['root'], new_chord['type'])
            new_chord['frequencies'] = [self.note_frequencies.get(f"{note}4", 261.63) for note in new_chord['notes']]
        
        elif modification == 'add_sus4' and chord['type'] in ['major', 'minor']:
            new_chord['type'] = 'sus4'
            new_chord['notes'] = self._build_chord(chord['root'], new_chord['type'])
            new_chord['frequencies'] = [self.note_frequencies.get(f"{note}4", 261.63) for note in new_chord['notes']]
        
        elif modification == 'substitute_major_with_minor' and chord['type'] == 'major':
            new_chord['type'] = 'minor'
            new_chord['notes'] = self._build_chord(chord['root'], new_chord['type'])
            new_chord['frequencies'] = [self.note_frequencies.get(f"{note}4", 261.63) for note in new_chord['notes']]
        
        elif modification == 'substitute_minor_with_major' and chord['type'] == 'minor':
            new_chord['type'] = 'major'
            new_chord['notes'] = self._build_chord(chord['root'], new_chord['type'])
            new_chord['frequencies'] = [self.note_frequencies.get(f"{note}4", 261.63) for note in new_chord['notes']]
        
        return new_chord


class ArrangementEngine:
    """Advanced arrangement engine for creating sophisticated musical arrangements"""
    
    def __init__(self):
        self.arrangement_templates = self._load_arrangement_templates()
        self.instrument_roles = self._define_instrument_roles()
        
    def _load_arrangement_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load arrangement templates for different genres and sections"""
        return {
            'pop': {
                'intro': {
                    'length_bars': 4,
                    'instruments': ['acoustic_piano', 'acoustic_guitar'],
                    'dynamics': 'soft',
                    'pattern': 'simple'
                },
                'verse': {
                    'length_bars': 8,
                    'instruments': ['acoustic_piano', 'acoustic_guitar', 'bass_guitar', 'acoustic_drums'],
                    'dynamics': 'medium',
                    'pattern': 'steady'
                },
                'chorus': {
                    'length_bars': 8,
                    'instruments': ['acoustic_piano', 'electric_guitar', 'bass_guitar', 'acoustic_drums', 'strings'],
                    'dynamics': 'loud',
                    'pattern': 'full'
                },
                'bridge': {
                    'length_bars': 4,
                    'instruments': ['acoustic_piano', 'strings'],
                    'dynamics': 'medium',
                    'pattern': 'sparse'
                },
                'outro': {
                    'length_bars': 4,
                    'instruments': ['acoustic_piano', 'acoustic_guitar'],
                    'dynamics': 'fade',
                    'pattern': 'simple'
                }
            },
            'rock': {
                'intro': {
                    'length_bars': 4,
                    'instruments': ['electric_guitar', 'bass_guitar'],
                    'dynamics': 'medium',
                    'pattern': 'driving'
                },
                'verse': {
                    'length_bars': 8,
                    'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums'],
                    'dynamics': 'medium',
                    'pattern': 'steady'
                },
                'chorus': {
                    'length_bars': 8,
                    'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums', 'organ'],
                    'dynamics': 'loud',
                    'pattern': 'powerful'
                },
                'bridge': {
                    'length_bars': 4,
                    'instruments': ['acoustic_guitar', 'bass_guitar'],
                    'dynamics': 'soft',
                    'pattern': 'clean'
                },
                'outro': {
                    'length_bars': 8,
                    'instruments': ['electric_guitar', 'bass_guitar', 'acoustic_drums'],
                    'dynamics': 'fade',
                    'pattern': 'driving'
                }
            },
            'jazz': {
                'intro': {
                    'length_bars': 8,
                    'instruments': ['acoustic_piano', 'bass_guitar'],
                    'dynamics': 'soft',
                    'pattern': 'swing'
                },
                'verse': {
                    'length_bars': 16,
                    'instruments': ['acoustic_piano', 'bass_guitar', 'acoustic_drums', 'trumpet'],
                    'dynamics': 'medium',
                    'pattern': 'swing'
                },
                'chorus': {
                    'length_bars': 16,
                    'instruments': ['acoustic_piano', 'bass_guitar', 'acoustic_drums', 'trumpet', 'saxophone'],
                    'dynamics': 'medium_loud',
                    'pattern': 'full_swing'
                },
                'bridge': {
                    'length_bars': 8,
                    'instruments': ['acoustic_piano', 'bass_guitar'],
                    'dynamics': 'soft',
                    'pattern': 'solo'
                },
                'outro': {
                    'length_bars': 8,
                    'instruments': ['acoustic_piano', 'bass_guitar', 'acoustic_drums'],
                    'dynamics': 'fade',
                    'pattern': 'swing'
                }
            }
        }
    
    def _define_instrument_roles(self) -> Dict[str, Dict[str, Any]]:
        """Define roles and characteristics for each instrument"""
        return {
            'acoustic_piano': {
                'role': 'harmonic_lead',
                'priority': 1,
                'octave_range': (3, 6),
                'playing_styles': ['classical', 'jazz', 'rock'],
                'typical_patterns': ['chords', 'arpeggios', 'melody']
            },
            'electric_piano': {
                'role': 'harmonic_support',
                'priority': 2,
                'octave_range': (3, 5),
                'playing_styles': ['funk', 'soul', 'pop'],
                'typical_patterns': ['chords', 'rhythm']
            },
            'acoustic_guitar': {
                'role': 'harmonic_rhythm',
                'priority': 2,
                'octave_range': (2, 4),
                'playing_styles': ['strumming', 'fingerpicking', 'classical'],
                'typical_patterns': ['strums', 'arpeggios', 'melody']
            },
            'electric_guitar': {
                'role': 'lead_rhythm',
                'priority': 1,
                'octave_range': (2, 5),
                'playing_styles': ['clean', 'distorted', 'chorus'],
                'typical_patterns': ['chords', 'riffs', 'solos']
            },
            'bass_guitar': {
                'role': 'bass_foundation',
                'priority': 1,
                'octave_range': (1, 3),
                'playing_styles': ['fingered', 'picked', 'slapped'],
                'typical_patterns': ['root_notes', 'walking', 'rhythmic']
            },
            'acoustic_drums': {
                'role': 'rhythm_foundation',
                'priority': 1,
                'octave_range': (0, 0),
                'playing_styles': ['acoustic'],
                'typical_patterns': ['basic', 'complex', 'fills']
            },
            'strings': {
                'role': 'harmonic_texture',
                'priority': 3,
                'octave_range': (3, 6),
                'playing_styles': ['sustained', 'staccato', 'tremolo'],
                'typical_patterns': ['pads', 'melody', 'harmonies']
            }
        }
    
    def create_arrangement(self, genre: str, structure: List[str], total_duration: float) -> Dict[str, Any]:
        """Create a complete song arrangement with sections and instrument assignments"""
        
        if genre not in self.arrangement_templates:
            genre = 'pop'  # Default fallback
        
        template = self.arrangement_templates[genre]
        
        # Calculate section durations
        total_bars = int(total_duration / 2)  # Assuming 2 seconds per bar on average
        sections = []
        current_bar = 0
        
        for section_name in structure:
            if section_name in template:
                section_template = template[section_name]
                section_bars = section_template['length_bars']
                
                # Adjust if we're running out of bars
                remaining_bars = total_bars - current_bar
                if section_bars > remaining_bars:
                    section_bars = remaining_bars
                
                sections.append({
                    'name': section_name,
                    'start_bar': current_bar,
                    'length_bars': section_bars,
                    'instruments': section_template['instruments'],
                    'dynamics': section_template['dynamics'],
                    'pattern': section_template['pattern']
                })
                
                current_bar += section_bars
                
                if current_bar >= total_bars:
                    break
        
        return {
            'genre': genre,
            'total_bars': total_bars,
            'sections': sections,
            'structure': structure
        }
    
    def get_instrument_pattern(self, instrument: str, section: str, genre: str, 
                            chord_progression: List[Dict[str, Any]], tempo_bpm: int) -> Dict[str, Any]:
        """Get specific playing pattern for an instrument in a section"""
        
        if instrument not in self.instrument_roles:
            return {'pattern': 'simple', 'style': 'default'}
        
        role_info = self.instrument_roles[instrument]
        
        # Determine pattern complexity based on section and genre
        if section in ['intro', 'outro']:
            complexity = 'simple'
        elif section == 'verse':
            complexity = 'medium'
        elif section == 'chorus':
            complexity = 'full'
        else:
            complexity = 'medium'
        
        # Get style based on genre and instrument
        available_styles = role_info['playing_styles']
        if genre == 'rock' and 'distorted' in available_styles:
            style = 'distorted'
        elif genre == 'jazz' and 'jazz' in available_styles:
            style = 'jazz'
        elif genre == 'classical' and 'classical' in available_styles:
            style = 'classical'
        else:
            style = available_styles[0] if available_styles else 'default'
        
        return {
            'pattern': complexity,
            'style': style,
            'role': role_info['role'],
            'octave_range': role_info['octave_range'],
            'typical_patterns': role_info['typical_patterns']
        }


# Continue in next part...
