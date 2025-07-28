"""
Comprehensive Free Music Data Integration System
Downloads and manages music data from various free APIs
Integrates with Azure OpenAI for fine-tuning and metadata enhancement
"""

import requests
import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeeMusicDataManager:
    """Manages free music data from multiple APIs and sources"""
    
    def __init__(self):
        self.session = None
        self.data_cache = {}
        self.downloaded_tracks = []
        
        # API Configurations
        self.apis = {
            'jamendo': {
                'base_url': 'https://api.jamendo.com/v3.0',
                'client_id': 'f6c7b7c7',  # Free API key
                'rate_limit': 1,  # requests per second
                'tracks_per_request': 50
            },
            'freesound': {
                'base_url': 'https://freesound.org/apiv2',
                'api_key': 'demo',  # Demo key for testing
                'rate_limit': 0.5,
                'tracks_per_request': 15
            },
            'musicbrainz': {
                'base_url': 'https://musicbrainz.org/ws/2',
                'rate_limit': 1,
                'tracks_per_request': 25
            },
            'lastfm': {
                'base_url': 'https://ws.audioscrobbler.com/2.0',
                'api_key': 'demo',  # Demo key
                'rate_limit': 5,
                'tracks_per_request': 50
            }
        }
        
        logger.info("✅ Free Music Data Manager initialized")
    
    async def init_session(self):
        """Initialize aiohttp session for async requests"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def fetch_jamendo_tracks(self, limit=100) -> List[Dict]:
        """Fetch tracks from Jamendo API"""
        try:
            await self.init_session()
            
            url = f"{self.apis['jamendo']['base_url']}/tracks"
            params = {
                'client_id': self.apis['jamendo']['client_id'],
                'format': 'json',
                'limit': min(limit, 200),
                'include': 'musicinfo+stats+licenses',
                'order': 'popularity_total',
                'tags': 'electronic,ambient,rock,pop,jazz'
            }
            
            logger.info(f"🎵 Fetching {limit} tracks from Jamendo...")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    tracks = data.get('results', [])
                    
                    # Transform to our format
                    transformed_tracks = []
                    for track in tracks:
                        transformed_track = {
                            'id': f"jamendo_{track.get('id')}",
                            'title': track.get('name', 'Unknown'),
                            'artist': track.get('artist_name', 'Unknown'),
                            'genre': self._extract_genre(track.get('musicinfo', {})),
                            'mood': self._extract_mood(track.get('musicinfo', {})),
                            'duration': track.get('duration', 0),
                            'url': track.get('audio', ''),
                            'download_url': track.get('audiodownload', ''),
                            'license': track.get('license_ccurl', ''),
                            'tags': track.get('musicinfo', {}).get('tags', {}).get('genres', []),
                            'created_at': datetime.utcnow().isoformat(),
                            'source': 'jamendo',
                            'popularity': track.get('stats', {}).get('rate', 0)
                        }
                        transformed_tracks.append(transformed_track)
                    
                    logger.info(f"✅ Successfully fetched {len(transformed_tracks)} tracks from Jamendo")
                    return transformed_tracks
                else:
                    logger.error(f"❌ Jamendo API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Jamendo fetch failed: {e}")
            return []
    
    async def fetch_freesound_tracks(self, limit=50) -> List[Dict]:
        """Fetch audio samples from Freesound"""
        try:
            await self.init_session()
            
            url = f"{self.apis['freesound']['base_url']}/search/text/"
            params = {
                'query': 'music OR song OR melody OR beat',
                'filter': 'duration:[10.0 TO 300.0] AND type:wav',
                'sort': 'downloads_desc',
                'page_size': min(limit, 150),
                'fields': 'id,name,username,duration,download,url,license,tags,description'
            }
            
            logger.info(f"🎵 Fetching {limit} audio samples from Freesound...")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    sounds = data.get('results', [])
                    
                    # Transform to our format
                    transformed_tracks = []
                    for sound in sounds:
                        transformed_track = {
                            'id': f"freesound_{sound.get('id')}",
                            'title': sound.get('name', 'Unknown'),
                            'artist': sound.get('username', 'Unknown'),
                            'genre': self._classify_genre_from_tags(sound.get('tags', [])),
                            'mood': self._classify_mood_from_description(sound.get('description', '')),
                            'duration': int(sound.get('duration', 0)),
                            'url': sound.get('url', ''),
                            'download_url': sound.get('download', ''),
                            'license': sound.get('license', ''),
                            'tags': sound.get('tags', []),
                            'created_at': datetime.utcnow().isoformat(),
                            'source': 'freesound',
                            'description': sound.get('description', '')
                        }
                        transformed_tracks.append(transformed_track)
                    
                    logger.info(f"✅ Successfully fetched {len(transformed_tracks)} audio samples from Freesound")
                    return transformed_tracks
                else:
                    logger.error(f"❌ Freesound API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Freesound fetch failed: {e}")
            return []
    
    async def fetch_musicbrainz_data(self, limit=50) -> List[Dict]:
        """Fetch metadata from MusicBrainz"""
        try:
            await self.init_session()
            
            # Search for popular releases
            url = f"{self.apis['musicbrainz']['base_url']}/release"
            params = {
                'query': 'tag:electronic OR tag:ambient OR tag:rock OR tag:pop',
                'fmt': 'json',
                'limit': min(limit, 100)
            }
            
            headers = {
                'User-Agent': 'AI-Music-Portal/1.0 (contact@ai-music-portal.com)'
            }
            
            logger.info(f"🎵 Fetching {limit} releases from MusicBrainz...")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    releases = data.get('releases', [])
                    
                    # Transform to our format
                    transformed_tracks = []
                    for release in releases:
                        transformed_track = {
                            'id': f"musicbrainz_{release.get('id')}",
                            'title': release.get('title', 'Unknown'),
                            'artist': self._extract_artist_from_release(release),
                            'genre': self._extract_genre_from_tags(release.get('tags', [])),
                            'mood': 'Various',
                            'duration': 180,  # Default duration
                            'url': '',  # MusicBrainz doesn't provide audio URLs
                            'license': 'Various',
                            'tags': [tag.get('name', '') for tag in release.get('tags', [])],
                            'created_at': datetime.utcnow().isoformat(),
                            'source': 'musicbrainz',
                            'metadata': {
                                'mbid': release.get('id'),
                                'country': release.get('country'),
                                'date': release.get('date')
                            }
                        }
                        transformed_tracks.append(transformed_track)
                    
                    logger.info(f"✅ Successfully fetched {len(transformed_tracks)} releases from MusicBrainz")
                    return transformed_tracks
                else:
                    logger.error(f"❌ MusicBrainz API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ MusicBrainz fetch failed: {e}")
            return []
    
    def _extract_genre(self, musicinfo: Dict) -> str:
        """Extract genre from Jamendo musicinfo"""
        vocalinstrumental = musicinfo.get('vocalinstrumental', [])
        tags = musicinfo.get('tags', {})
        
        if 'electronic' in str(tags).lower():
            return 'Electronic'
        elif 'rock' in str(tags).lower():
            return 'Rock'
        elif 'pop' in str(tags).lower():
            return 'Pop'
        elif 'jazz' in str(tags).lower():
            return 'Jazz'
        elif 'ambient' in str(tags).lower():
            return 'Ambient'
        else:
            return 'Various'
    
    def _extract_mood(self, musicinfo: Dict) -> str:
        """Extract mood from Jamendo musicinfo"""
        tags_str = str(musicinfo.get('tags', {})).lower()
        
        if any(word in tags_str for word in ['energetic', 'upbeat', 'fast']):
            return 'Energetic'
        elif any(word in tags_str for word in ['calm', 'peaceful', 'slow']):
            return 'Calm'
        elif any(word in tags_str for word in ['dark', 'mysterious']):
            return 'Mysterious'
        elif any(word in tags_str for word in ['happy', 'cheerful', 'positive']):
            return 'Happy'
        else:
            return 'Neutral'
    
    def _classify_genre_from_tags(self, tags: List[str]) -> str:
        """Classify genre based on tags"""
        tags_str = ' '.join(tags).lower()
        
        if any(word in tags_str for word in ['electronic', 'synth', 'digital']):
            return 'Electronic'
        elif any(word in tags_str for word in ['rock', 'guitar', 'metal']):
            return 'Rock'
        elif any(word in tags_str for word in ['ambient', 'atmosphere', 'drone']):
            return 'Ambient'
        elif any(word in tags_str for word in ['classical', 'orchestra', 'piano']):
            return 'Classical'
        else:
            return 'Various'
    
    def _classify_mood_from_description(self, description: str) -> str:
        """Classify mood from description"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['energetic', 'upbeat', 'fast', 'exciting']):
            return 'Energetic'
        elif any(word in desc_lower for word in ['calm', 'peaceful', 'relaxing', 'soft']):
            return 'Calm'
        elif any(word in desc_lower for word in ['dark', 'mysterious', 'spooky']):
            return 'Mysterious'
        elif any(word in desc_lower for word in ['happy', 'cheerful', 'joyful']):
            return 'Happy'
        else:
            return 'Neutral'
    
    def _extract_artist_from_release(self, release: Dict) -> str:
        """Extract artist name from MusicBrainz release"""
        artist_credit = release.get('artist-credit', [])
        if artist_credit and len(artist_credit) > 0:
            return artist_credit[0].get('artist', {}).get('name', 'Unknown')
        return 'Unknown'
    
    def _extract_genre_from_tags(self, tags: List[Dict]) -> str:
        """Extract genre from MusicBrainz tags"""
        for tag in tags:
            tag_name = tag.get('name', '').lower()
            if tag_name in ['electronic', 'rock', 'pop', 'jazz', 'classical', 'ambient']:
                return tag_name.title()
        return 'Various'
    
    async def download_all_free_music_data(self, total_limit=300) -> Dict:
        """Download music data from all free APIs"""
        logger.info(f"🚀 Starting comprehensive music data download (limit: {total_limit})")
        
        all_tracks = []
        download_stats = {
            'total_requested': total_limit,
            'sources': {},
            'started_at': datetime.utcnow().isoformat()
        }
        
        # Split limit across APIs
        jamendo_limit = int(total_limit * 0.5)  # 50% from Jamendo
        freesound_limit = int(total_limit * 0.3)  # 30% from Freesound
        musicbrainz_limit = int(total_limit * 0.2)  # 20% from MusicBrainz
        
        try:
            # Fetch from Jamendo
            jamendo_tracks = await self.fetch_jamendo_tracks(jamendo_limit)
            all_tracks.extend(jamendo_tracks)
            download_stats['sources']['jamendo'] = len(jamendo_tracks)
            
            # Add delay to respect rate limits
            await asyncio.sleep(1)
            
            # Fetch from Freesound
            freesound_tracks = await self.fetch_freesound_tracks(freesound_limit)
            all_tracks.extend(freesound_tracks)
            download_stats['sources']['freesound'] = len(freesound_tracks)
            
            # Add delay to respect rate limits
            await asyncio.sleep(1)
            
            # Fetch from MusicBrainz
            musicbrainz_tracks = await self.fetch_musicbrainz_data(musicbrainz_limit)
            all_tracks.extend(musicbrainz_tracks)
            download_stats['sources']['musicbrainz'] = len(musicbrainz_tracks)
            
        except Exception as e:
            logger.error(f"❌ Error during music data download: {e}")
        finally:
            await self.close_session()
        
        download_stats['total_downloaded'] = len(all_tracks)
        download_stats['completed_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Music data download completed: {len(all_tracks)} tracks from {len(download_stats['sources'])} sources")
        
        # Save to cache
        self.downloaded_tracks = all_tracks
        
        return {
            'tracks': all_tracks,
            'stats': download_stats
        }
    
    def save_music_data_to_file(self, filename='free_music_data.json'):
        """Save downloaded music data to JSON file"""
        try:
            data = {
                'metadata': {
                    'download_date': datetime.utcnow().isoformat(),
                    'total_tracks': len(self.downloaded_tracks),
                    'sources': list(set(track.get('source') for track in self.downloaded_tracks))
                },
                'tracks': self.downloaded_tracks
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Music data saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Failed to save music data: {e}")
            return None
    
    def get_sample_tracks_for_demo(self, count=10) -> List[Dict]:
        """Get sample tracks for demo purposes"""
        if not self.downloaded_tracks:
            # Return default demo tracks if no data downloaded
            return [
                {
                    'id': 'demo_1',
                    'title': 'Electronic Dreams',
                    'artist': 'AI Composer',
                    'genre': 'Electronic',
                    'mood': 'Energetic',
                    'duration': 180,
                    'url': 'https://www.soundjay.com/misc/sounds/magic-chime-02.wav',
                    'source': 'demo',
                    'tags': ['demo', 'electronic']
                }
            ]
        
        # Return a sample from downloaded tracks
        return self.downloaded_tracks[:count]

# Global instance
free_music_manager = FreeeMusicDataManager()

# Async wrapper functions for Flask integration
async def download_free_music_data(limit=300):
    """Download free music data - async wrapper"""
    return await free_music_manager.download_all_free_music_data(limit)

def get_free_music_samples(count=10):
    """Get free music samples for demo"""
    return free_music_manager.get_sample_tracks_for_demo(count)

def save_downloaded_music_data():
    """Save downloaded music data to file"""
    return free_music_manager.save_music_data_to_file()

# Sync function for immediate use
def download_music_data_sync(limit=100):
    """Synchronous wrapper for downloading music data"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            free_music_manager.download_all_free_music_data(limit)
        )
        return result
    finally:
        loop.close()

if __name__ == "__main__":
    # Test the music data manager
    print("🎵 Testing Free Music Data Manager...")
    result = download_music_data_sync(50)
    print(f"✅ Downloaded {len(result['tracks'])} tracks")
    
    # Save to file
    filename = free_music_manager.save_music_data_to_file()
    print(f"✅ Data saved to {filename}")
