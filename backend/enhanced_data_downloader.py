"""
Enhanced Training Data Downloader for AI Music Platform
Downloads diverse music data from multiple sources and stores metadata
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import traceback
import requests
import hashlib
import time
from pathlib import Path

# Audio processing imports
try:
    import librosa
    import numpy as np
    AUDIO_PROCESSING_AVAILABLE = True
    print("🔗 Audio processing libraries loaded successfully")
except ImportError as e:
    AUDIO_PROCESSING_AVAILABLE = False
    print(f"⚠️ Audio processing libraries not available: {e}")

# Azure Storage imports
try:
    from azure.storage.blob import BlobServiceClient
    AZURE_STORAGE_AVAILABLE = True
    print("🔗 Azure Storage SDK loaded successfully")
except ImportError as e:
    AZURE_STORAGE_AVAILABLE = False
    print(f"⚠️ Azure Storage SDK not available: {e}")

class EnhancedMusicDataDownloader:
    def __init__(self):
        self.storage_connection = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.training_container = os.getenv('TRAINING_DATA_CONTAINER', 'training-data')
        self.blob_client = None
        
        # Music data sources
        self.data_sources = {
            'freesound': {
                'api_key': os.getenv('FREESOUND_API_KEY'),
                'base_url': 'https://freesound.org/apiv2/',
                'enabled': bool(os.getenv('FREESOUND_API_KEY'))
            },
            'jamendo': {
                'client_id': os.getenv('JAMENDO_CLIENT_ID'),
                'base_url': 'https://api.jamendo.com/v3.0/',
                'enabled': bool(os.getenv('JAMENDO_CLIENT_ID'))
            },
            'musicbrainz': {
                'base_url': 'https://musicbrainz.org/ws/2/',
                'enabled': True  # No API key needed
            }
        }
        
        # Genre mapping for different sources
        self.genre_mapping = {
            'electronic': ['electronic', 'edm', 'techno', 'house', 'dubstep', 'trance'],
            'rock': ['rock', 'alternative', 'indie-rock', 'punk', 'metal', 'hard-rock'],
            'pop': ['pop', 'dance-pop', 'electropop', 'indie-pop', 'synth-pop'],
            'jazz': ['jazz', 'fusion', 'bebop', 'smooth-jazz', 'acid-jazz'],
            'classical': ['classical', 'orchestral', 'chamber', 'opera', 'symphony'],
            'hip-hop': ['hip-hop', 'rap', 'trap', 'drill', 'lo-fi-hip-hop'],
            'folk': ['folk', 'country', 'bluegrass', 'americana', 'world'],
            'ambient': ['ambient', 'chillout', 'downtempo', 'new-age', 'meditation'],
            'reggae': ['reggae', 'dub', 'ska', 'dancehall'],
            'latin': ['latin', 'salsa', 'bossa-nova', 'tango', 'flamenco'],
            'blues': ['blues', 'delta-blues', 'chicago-blues', 'electric-blues'],
            'funk': ['funk', 'soul', 'rnb', 'disco', 'p-funk']
        }
        
        self.local_storage_path = '/tmp/training_data'
        Path(self.local_storage_path).mkdir(parents=True, exist_ok=True)
    
    def initialize_storage(self) -> bool:
        """Initialize Azure Blob Storage client"""
        if not AZURE_STORAGE_AVAILABLE or not self.storage_connection:
            print("❌ Azure Storage not available or not configured")
            return False
            
        try:
            self.blob_client = BlobServiceClient.from_connection_string(self.storage_connection)
            
            # Ensure container exists
            try:
                self.blob_client.create_container(self.training_container)
            except:
                pass  # Container might already exist
                
            print("✅ Azure Storage initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Azure Storage initialization failed: {e}")
            return False
    
    def download_freesound_samples(self, genre: str, count: int = 50) -> List[Dict]:
        """Download samples from Freesound API"""
        if not self.data_sources['freesound']['enabled']:
            print("❌ Freesound API not configured")
            return []
            
        samples = []
        try:
            # Map genre to Freesound tags
            search_tags = self.genre_mapping.get(genre, [genre])
            
            for tag in search_tags[:3]:  # Limit to first 3 tags
                url = f"{self.data_sources['freesound']['base_url']}search/text/"
                params = {
                    'query': tag,
                    'filter': 'duration:[10.0 TO 60.0] type:wav',  # 10-60 second WAV files
                    'sort': 'downloads_desc',
                    'page_size': min(count // len(search_tags), 150),
                    'fields': 'id,name,username,duration,filesize,download,previews,tags,license',
                    'token': self.data_sources['freesound']['api_key']
                }
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    for sound in data.get('results', []):
                        if len(samples) >= count:
                            break
                            
                        sample_info = {
                            'source': 'freesound',
                            'id': sound['id'],
                            'name': sound['name'],
                            'artist': sound['username'],
                            'genre': genre,
                            'duration': sound['duration'],
                            'filesize': sound['filesize'],
                            'download_url': sound['download'],
                            'preview_url': sound['previews']['preview-lq-mp3'],
                            'tags': sound['tags'],
                            'license': sound['license'],
                            'quality_score': min(1.0, sound.get('downloads', 0) / 1000)  # Rough quality estimate
                        }
                        samples.append(sample_info)
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"❌ Freesound download failed: {e}")
            
        return samples
    
    def download_jamendo_tracks(self, genre: str, count: int = 30) -> List[Dict]:
        """Download tracks from Jamendo API"""
        if not self.data_sources['jamendo']['enabled']:
            print("❌ Jamendo API not configured")
            return []
            
        tracks = []
        try:
            # Map genre to Jamendo genres
            jamendo_genres = self.genre_mapping.get(genre, [genre])
            
            for jamendo_genre in jamendo_genres[:2]:  # Limit to first 2 genres
                url = f"{self.data_sources['jamendo']['base_url']}tracks/"
                params = {
                    'client_id': self.data_sources['jamendo']['client_id'],
                    'format': 'json',
                    'limit': count // len(jamendo_genres),
                    'tags': jamendo_genre,
                    'include': 'musicinfo',
                    'audioformat': 'mp32'
                }
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    for track in data.get('results', []):
                        if len(tracks) >= count:
                            break
                            
                        track_info = {
                            'source': 'jamendo',
                            'id': track['id'],
                            'name': track['name'],
                            'artist': track['artist_name'],
                            'genre': genre,
                            'duration': track.get('duration', 0),
                            'download_url': track.get('audio', ''),
                            'license': 'CC',  # Jamendo uses Creative Commons
                            'quality_score': min(1.0, track.get('popularity', 0) / 100)
                        }
                        tracks.append(track_info)
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"❌ Jamendo download failed: {e}")
            
        return tracks
    
    def analyze_audio_features(self, file_path: str) -> Dict:
        """Analyze audio features using librosa"""
        if not AUDIO_PROCESSING_AVAILABLE:
            return {}
            
        try:
            # Load audio file
            y, sr = librosa.load(file_path, duration=30)  # Analyze first 30 seconds
            
            # Extract features
            features = {}
            
            # Basic features
            features['sample_rate'] = int(sr)
            features['duration'] = float(librosa.get_duration(y=y, sr=sr))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            
            zero_crossings = librosa.feature.zero_crossing_rate(y)
            features['zero_crossing_rate_mean'] = float(np.mean(zero_crossings))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfccs_mean'] = [float(x) for x in np.mean(mfccs, axis=1)]
            
            # Tempo and beat
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            
            # Harmonic and percussive components
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            features['harmonic_energy'] = float(np.sum(y_harmonic**2))
            features['percussive_energy'] = float(np.sum(y_percussive**2))
            
            # Chroma features (key/harmony)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma_mean'] = [float(x) for x in np.mean(chroma, axis=1)]
            
            # Energy in different frequency bands
            stft = np.abs(librosa.stft(y))
            features['low_energy'] = float(np.mean(stft[:stft.shape[0]//3]))
            features['mid_energy'] = float(np.mean(stft[stft.shape[0]//3:2*stft.shape[0]//3]))
            features['high_energy'] = float(np.mean(stft[2*stft.shape[0]//3:]))
            
            return features
            
        except Exception as e:
            print(f"❌ Audio analysis failed for {file_path}: {e}")
            return {}
    
    def download_and_process_track(self, track_info: Dict) -> Optional[Dict]:
        """Download a track and process it"""
        try:
            # Create filename
            safe_name = "".join(c for c in track_info['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{track_info['source']}_{track_info['id']}_{safe_name[:50]}.wav"
            local_path = os.path.join(self.local_storage_path, filename)
            
            # Download file
            download_url = track_info['download_url']
            if track_info['source'] == 'freesound':
                # Freesound requires API key in header
                headers = {'Authorization': f"Token {self.data_sources['freesound']['api_key']}"}
                response = requests.get(download_url, headers=headers, stream=True, timeout=60)
            else:
                response = requests.get(download_url, stream=True, timeout=60)
            
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Analyze audio features
                audio_features = self.analyze_audio_features(local_path)
                
                # Upload to Azure Storage if available
                blob_path = f"training/{track_info['genre']}/{filename}"
                if self.blob_client:
                    blob_client = self.blob_client.get_blob_client(
                        container=self.training_container,
                        blob=blob_path
                    )
                    with open(local_path, 'rb') as data:
                        blob_client.upload_blob(data, overwrite=True)
                    
                    # Clean up local file
                    os.remove(local_path)
                    file_path = f"azure://{self.training_container}/{blob_path}"
                else:
                    file_path = local_path
                
                # Create processed track info
                processed_info = {
                    **track_info,
                    'file_path': file_path,
                    'file_size_bytes': os.path.getsize(local_path) if os.path.exists(local_path) else 0,
                    'audio_format': 'wav',
                    'audio_features': audio_features,
                    'processed_at': datetime.now().isoformat(),
                    'is_processed': True
                }
                
                return processed_info
                
        except Exception as e:
            print(f"❌ Failed to download/process track {track_info.get('name', 'unknown')}: {e}")
            
        return None
    
    def download_genre_data(self, genre: str, total_count: int = 100) -> List[Dict]:
        """Download training data for a specific genre"""
        print(f"🎵 Downloading training data for genre: {genre}")
        
        all_tracks = []
        
        # Download from Freesound (focus on samples and loops)
        freesound_count = min(total_count // 2, 50)
        if self.data_sources['freesound']['enabled']:
            print(f"📦 Downloading {freesound_count} samples from Freesound...")
            freesound_tracks = self.download_freesound_samples(genre, freesound_count)
            all_tracks.extend(freesound_tracks)
        
        # Download from Jamendo (focus on full tracks)
        jamendo_count = min(total_count // 3, 30)
        if self.data_sources['jamendo']['enabled']:
            print(f"🎼 Downloading {jamendo_count} tracks from Jamendo...")
            jamendo_tracks = self.download_jamendo_tracks(genre, jamendo_count)
            all_tracks.extend(jamendo_tracks)
        
        print(f"✅ Found {len(all_tracks)} tracks for {genre}")
        
        # Process tracks (download and analyze)
        processed_tracks = []
        for i, track in enumerate(all_tracks):
            print(f"🔄 Processing track {i+1}/{len(all_tracks)}: {track['name']}")
            processed_track = self.download_and_process_track(track)
            if processed_track:
                processed_tracks.append(processed_track)
            
            # Rate limiting
            time.sleep(0.5)
        
        print(f"✅ Successfully processed {len(processed_tracks)} tracks for {genre}")
        return processed_tracks
    
    def download_all_genres(self, tracks_per_genre: int = 50) -> Dict[str, List[Dict]]:
        """Download training data for all genres"""
        if not self.initialize_storage():
            print("❌ Storage not available, using local storage only")
        
        all_data = {}
        
        # Core genres to focus on
        priority_genres = [
            'electronic', 'pop', 'rock', 'hip-hop', 'jazz', 'classical',
            'ambient', 'folk', 'blues', 'funk', 'reggae', 'latin'
        ]
        
        for genre in priority_genres:
            try:
                genre_data = self.download_genre_data(genre, tracks_per_genre)
                all_data[genre] = genre_data
                
                # Save metadata locally
                metadata_file = os.path.join(self.local_storage_path, f"{genre}_metadata.json")
                with open(metadata_file, 'w') as f:
                    json.dump(genre_data, f, indent=2)
                
                print(f"💾 Saved metadata for {genre}: {len(genre_data)} tracks")
                
            except Exception as e:
                print(f"❌ Failed to download data for {genre}: {e}")
                all_data[genre] = []
        
        # Save summary
        summary = {
            'total_genres': len(all_data),
            'total_tracks': sum(len(tracks) for tracks in all_data.values()),
            'genre_counts': {genre: len(tracks) for genre, tracks in all_data.items()},
            'download_date': datetime.now().isoformat(),
            'sources_used': [source for source, config in self.data_sources.items() if config['enabled']]
        }
        
        summary_file = os.path.join(self.local_storage_path, 'download_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"🎉 Download complete! Total tracks: {summary['total_tracks']}")
        return all_data

def main():
    """Main function for standalone execution"""
    downloader = EnhancedMusicDataDownloader()
    
    # Download data for all genres
    all_data = downloader.download_all_genres(tracks_per_genre=20)  # Start with smaller number for testing
    
    print("📊 Download Summary:")
    for genre, tracks in all_data.items():
        print(f"  {genre}: {len(tracks)} tracks")

if __name__ == "__main__":
    main()
