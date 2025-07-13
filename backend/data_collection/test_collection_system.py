#!/usr/bin/env python3
"""
Quick test script for the music data collection system
"""

import sys
import os
from pathlib import Path

# Add the data collection directory to the path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import librosa
        print("✅ librosa imported successfully")
    except ImportError as e:
        print(f"❌ librosa import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        from music_data_downloader import MusicDataDownloader
        print("✅ MusicDataDownloader imported successfully")
    except ImportError as e:
        print(f"❌ MusicDataDownloader import failed: {e}")
        return False
    
    try:
        from feature_extractor import MusicFeatureExtractor
        print("✅ MusicFeatureExtractor imported successfully")
    except ImportError as e:
        print(f"❌ MusicFeatureExtractor import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of the data collection system"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        # Test MusicDataDownloader
        from music_data_downloader import MusicDataDownloader
        downloader = MusicDataDownloader("test_music_data")
        print("✅ MusicDataDownloader initialized successfully")
        
        # Test directory creation
        assert downloader.base_dir.exists(), "Base directory not created"
        assert downloader.audio_dir.exists(), "Audio directory not created"
        assert downloader.features_dir.exists(), "Features directory not created"
        print("✅ Directory structure created successfully")
        
        # Test MusicFeatureExtractor
        from feature_extractor import MusicFeatureExtractor
        extractor = MusicFeatureExtractor("test_features.db")
        print("✅ MusicFeatureExtractor initialized successfully")
        
        # Test database creation
        assert Path("test_features.db").exists(), "Database file not created"
        print("✅ Database created successfully")
        
        # Cleanup test files
        import shutil
        if Path("test_music_data").exists():
            shutil.rmtree("test_music_data")
        if Path("test_features.db").exists():
            Path("test_features.db").unlink()
        print("✅ Test cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_feature_extraction():
    """Test feature extraction with a synthetic audio file"""
    print("\n🎵 Testing feature extraction...")
    
    try:
        import numpy as np
        from scipy.io.wavfile import write
        from feature_extractor import MusicFeatureExtractor
        
        # Create a synthetic audio file
        sample_rate = 22050
        duration = 2  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Generate a simple sine wave
        frequency = 440  # A4 note
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Save as WAV file
        test_audio_file = "test_audio.wav"
        write(test_audio_file, sample_rate, (audio * 32767).astype(np.int16))
        print("✅ Synthetic audio file created")
        
        # Test feature extraction
        extractor = MusicFeatureExtractor("test_features.db")
        features = extractor.extract_comprehensive_features(test_audio_file)
        
        # Check if features were extracted
        assert features, "No features extracted"
        assert 'duration' in features, "Duration not extracted"
        assert 'tempo' in features, "Tempo not extracted"
        assert 'mfcc_features' in features, "MFCC features not extracted"
        print("✅ Feature extraction successful")
        
        # Print some extracted features
        print(f"   Duration: {features['duration']:.2f} seconds")
        print(f"   Tempo: {features['tempo']:.1f} BPM")
        print(f"   Sample rate: {features['sample_rate']} Hz")
        print(f"   Predicted genre: {features['genre']}")
        print(f"   Predicted mood: {features['mood']}")
        
        # Cleanup
        Path(test_audio_file).unlink()
        Path("test_features.db").unlink()
        print("✅ Feature extraction test cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Feature extraction test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎵 Portal AI Music - Data Collection Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality Test", test_basic_functionality),
        ("Feature Extraction Test", test_feature_extraction)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The data collection system is ready to use.")
        print("\n📋 Next steps:")
        print("1. Run: python run_collection_pipeline.py")
        print("2. Add your own audio files to music_data/audio/")
        print("3. Configure API keys for additional data sources")
        return 0
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit(main())
