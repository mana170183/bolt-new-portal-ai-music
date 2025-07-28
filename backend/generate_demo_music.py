#!/usr/bin/env python3
"""
Generate demo music tracks for the AI Music Portal
Creates Electronic Dreams, Acoustic Serenity, and Jazz Fusion demo tracks
"""

import numpy as np
import wave
import struct
import os

def generate_tone(frequency, duration, sample_rate=44100, volume=0.5):
    """Generate a simple tone"""
    frames = int(duration * sample_rate)
    arr = []
    for i in range(frames):
        value = volume * np.sin(2 * np.pi * frequency * i / sample_rate)
        arr.append(value)
    return arr

def generate_chord(frequencies, duration, sample_rate=44100, volume=0.3):
    """Generate a chord by combining multiple frequencies"""
    frames = int(duration * sample_rate)
    arr = []
    for i in range(frames):
        value = 0
        for freq in frequencies:
            value += volume * np.sin(2 * np.pi * freq * i / sample_rate)
        value /= len(frequencies)  # Normalize
        arr.append(value)
    return arr

def add_envelope(arr, attack=0.1, decay=0.1, sustain=0.7, release=0.2):
    """Add ADSR envelope to the sound"""
    total_frames = len(arr)
    attack_frames = int(attack * total_frames)
    decay_frames = int(decay * total_frames)
    release_frames = int(release * total_frames)
    sustain_frames = total_frames - attack_frames - decay_frames - release_frames
    
    result = []
    for i, sample in enumerate(arr):
        if i < attack_frames:
            # Attack phase
            envelope = i / attack_frames
        elif i < attack_frames + decay_frames:
            # Decay phase
            envelope = 1.0 - (1.0 - sustain) * (i - attack_frames) / decay_frames
        elif i < attack_frames + decay_frames + sustain_frames:
            # Sustain phase
            envelope = sustain
        else:
            # Release phase
            envelope = sustain * (1.0 - (i - attack_frames - decay_frames - sustain_frames) / release_frames)
        
        result.append(sample * envelope)
    
    return result

def save_wav(filename, audio_data, sample_rate=44100):
    """Save audio data as WAV file"""
    with wave.open(filename, 'w') as wav_file:
        nchannels = 1
        sampwidth = 2
        framerate = sample_rate
        nframes = len(audio_data)
        comptype = "NONE"
        compname = "not compressed"
        
        wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
        
        for sample in audio_data:
            # Clamp the sample to prevent overflow
            clamped_sample = max(-1.0, min(1.0, sample))
            wav_file.writeframes(struct.pack('<h', int(clamped_sample * 32767)))

def generate_electronic_dreams():
    """Generate Electronic Dreams - Electronic/Synth track"""
    print("🎵 Generating Electronic Dreams...")
    
    # Electronic chord progressions with synth-like sounds
    chords = [
        [130.81, 164.81, 196.00],  # C minor
        [146.83, 174.61, 220.00],  # D minor
        [164.81, 196.00, 246.94],  # E flat major
        [130.81, 164.81, 196.00],  # C minor
    ]
    
    audio = []
    
    # Main progression
    for i in range(2):  # Repeat twice
        for chord in chords:
            # Add some detuning for electronic feel
            detuned_chord = [f + np.random.uniform(-2, 2) for f in chord]
            chord_audio = generate_chord(detuned_chord, 1.0, volume=0.2)
            chord_audio = add_envelope(chord_audio, attack=0.05, decay=0.1, sustain=0.8, release=0.05)
            audio.extend(chord_audio)
    
    # Add electronic lead melody
    lead_notes = [523.25, 587.33, 659.25, 698.46, 783.99, 698.46, 659.25, 587.33]  # C5 to G5
    for note in lead_notes:
        # Add vibrato
        note_audio = []
        duration = 0.5
        for i in range(int(44100 * duration)):
            vibrato = 1 + 0.05 * np.sin(2 * np.pi * 6 * i / 44100)
            value = 0.15 * np.sin(2 * np.pi * note * vibrato * i / 44100)
            note_audio.append(value)
        
        note_audio = add_envelope(note_audio, attack=0.01, decay=0.1, sustain=0.9, release=0.0)
        
        # Overlay on the chord progression
        start_pos = len(audio) - len(note_audio)
        if start_pos >= 0:
            for i, sample in enumerate(note_audio):
                if start_pos + i < len(audio):
                    audio[start_pos + i] += sample
    
    return audio

def generate_acoustic_serenity():
    """Generate Acoustic Serenity - Calm acoustic track"""
    print("🎵 Generating Acoustic Serenity...")
    
    # Acoustic guitar-like chord progressions
    chords = [
        [196.00, 246.94, 293.66],  # G major
        [220.00, 277.18, 329.63],  # A minor
        [246.94, 311.13, 369.99],  # B minor
        [196.00, 246.94, 293.66],  # G major
    ]
    
    audio = []
    
    # Gentle arpeggiated chords
    for i in range(3):  # Repeat 3 times for longer track
        for chord in chords:
            # Arpeggiate the chord
            for note in chord:
                note_audio = generate_tone(note, 0.4, volume=0.15)
                note_audio = add_envelope(note_audio, attack=0.02, decay=0.2, sustain=0.6, release=0.18)
                audio.extend(note_audio)
            
            # Add some silence between chords
            silence = [0] * int(44100 * 0.2)
            audio.extend(silence)
    
    return audio

def generate_jazz_fusion():
    """Generate Jazz Fusion - Complex jazz harmonies"""
    print("🎵 Generating Jazz Fusion...")
    
    # Jazz chord progressions with 7ths and extensions
    chords = [
        [196.00, 246.94, 293.66, 369.99],  # G major 7
        [220.00, 277.18, 329.63, 415.30],  # A minor 7
        [261.63, 329.63, 392.00, 493.88],  # C major 7
        [196.00, 246.94, 293.66, 369.99],  # G major 7
    ]
    
    audio = []
    
    # Walking bass line
    bass_notes = [98.00, 110.00, 123.47, 130.81, 146.83, 164.81, 174.61, 196.00]
    
    for i in range(2):  # Repeat twice
        for j, chord in enumerate(chords):
            # Bass note
            bass_note = bass_notes[j % len(bass_notes)]
            bass_audio = generate_tone(bass_note, 1.0, volume=0.15)
            bass_audio = add_envelope(bass_audio, attack=0.01, decay=0.1, sustain=0.8, release=0.09)
            
            # Jazz chord
            chord_audio = generate_chord(chord, 1.0, volume=0.1)
            chord_audio = add_envelope(chord_audio, attack=0.1, decay=0.1, sustain=0.7, release=0.1)
            
            # Combine bass and chord
            combined = []
            for k in range(max(len(bass_audio), len(chord_audio))):
                bass_val = bass_audio[k] if k < len(bass_audio) else 0
                chord_val = chord_audio[k] if k < len(chord_audio) else 0
                combined.append(bass_val + chord_val)
            
            audio.extend(combined)
    
    # Add improvised melody line
    melody_notes = [392.00, 440.00, 493.88, 523.25, 587.33, 523.25, 493.88, 440.00]
    for i, note in enumerate(melody_notes):
        # Add swing rhythm
        duration = 0.6 if i % 2 == 0 else 0.4
        note_audio = generate_tone(note, duration, volume=0.12)
        note_audio = add_envelope(note_audio, attack=0.05, decay=0.1, sustain=0.7, release=0.15)
        
        # Overlay on existing audio
        start_pos = int(len(audio) * 0.3) + i * int(44100 * 0.5)
        for j, sample in enumerate(note_audio):
            if start_pos + j < len(audio):
                audio[start_pos + j] += sample
    
    return audio

def convert_wav_to_mp3(wav_file, mp3_file):
    """Convert WAV to MP3 using ffmpeg if available"""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-i', wav_file, '-acodec', 'mp3', '-y', mp3_file], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            os.remove(wav_file)  # Remove WAV file
            return True
        else:
            print(f"FFmpeg conversion failed: {result.stderr}")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg not available, keeping WAV format")
        return False

def main():
    """Generate all demo tracks"""
    print("🎼 Generating AI Music Portal Demo Tracks")
    print("=" * 50)
    
    # Generate tracks
    tracks = {
        'demo1': ('Electronic Dreams', generate_electronic_dreams),
        'demo2': ('Acoustic Serenity', generate_acoustic_serenity),
        'demo3': ('Jazz Fusion', generate_jazz_fusion)
    }
    
    for file_prefix, (title, generator_func) in tracks.items():
        print(f"\n🎵 Creating {title}...")
        
        # Generate audio
        audio_data = generator_func()
        
        # Save as WAV first
        wav_file = f"{file_prefix}.wav"
        save_wav(wav_file, audio_data)
        print(f"✅ Saved {wav_file} ({len(audio_data)/44100:.1f} seconds)")
        
        # Try to convert to MP3
        mp3_file = f"{file_prefix}.mp3"
        if convert_wav_to_mp3(wav_file, mp3_file):
            print(f"✅ Converted to {mp3_file}")
        else:
            # Rename WAV to MP3 (browsers can play WAV too)
            os.rename(wav_file, mp3_file)
            print(f"✅ Renamed to {mp3_file}")
    
    print("\n" + "=" * 50)
    print("🎉 All demo tracks generated successfully!")
    print("\nTracks created:")
    print("• demo1.mp3 - Electronic Dreams (Electronic/Synth)")
    print("• demo2.mp3 - Acoustic Serenity (Calm/Acoustic)")
    print("• demo3.mp3 - Jazz Fusion (Complex/Jazz)")

if __name__ == "__main__":
    main()
