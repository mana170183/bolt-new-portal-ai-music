"""
Azure Integration Module for AI Music Portal
Comprehensive integration with Azure SQL, Blob Storage, OpenAI, and Key Vault
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

# Azure SDK imports
try:
    import pyodbc
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    import openai
    from azure.ai.openai import AzureOpenAI
    AZURE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Azure SDK not available: {e}")
    AZURE_AVAILABLE = False

from azure_config import (
    AZURE_CREDENTIALS, 
    AZURE_SQL_CONFIG, 
    AZURE_STORAGE_CONFIG, 
    AZURE_OPENAI_CONFIG,
    AZURE_KEYVAULT_CONFIG,
    DB_SCHEMA,
    FREE_MUSIC_APIS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureIntegrationManager:
    """Comprehensive Azure integration manager"""
    
    def __init__(self):
        self.credential = None
        self.sql_connection = None
        self.blob_service_client = None
        self.secret_client = None
        self.openai_client = None
        self.initialized = False
        
        if AZURE_AVAILABLE:
            self._initialize_azure_clients()
    
    def _initialize_azure_clients(self):
        """Initialize all Azure service clients"""
        try:
            # Initialize Azure credential
            self.credential = ClientSecretCredential(
                tenant_id=AZURE_CREDENTIALS['SP_TENANT'],
                client_id=AZURE_CREDENTIALS['SP_APP_ID'],
                client_secret=AZURE_CREDENTIALS['SP_PASSWORD']
            )
            
            # Initialize Blob Storage client
            if AZURE_STORAGE_CONFIG['connection_string']:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    AZURE_STORAGE_CONFIG['connection_string']
                )
                logger.info("✅ Azure Blob Storage client initialized")
            
            # Initialize Key Vault client
            self.secret_client = SecretClient(
                vault_url=AZURE_KEYVAULT_CONFIG['vault_url'],
                credential=self.credential
            )
            logger.info("✅ Azure Key Vault client initialized")
            
            # Initialize OpenAI client
            if AZURE_OPENAI_CONFIG['api_key']:
                self.openai_client = AzureOpenAI(
                    api_key=AZURE_OPENAI_CONFIG['api_key'],
                    api_version=AZURE_OPENAI_CONFIG['api_version'],
                    azure_endpoint=AZURE_OPENAI_CONFIG['endpoint']
                )
                logger.info("✅ Azure OpenAI client initialized")
            
            self.initialized = True
            logger.info("🚀 Azure Integration Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure clients: {e}")
            self.initialized = False
    
    def get_sql_connection(self):
        """Get SQL database connection"""
        if not AZURE_AVAILABLE:
            return None
            
        try:
            if not self.sql_connection or self.sql_connection.closed:
                self.sql_connection = pyodbc.connect(
                    AZURE_SQL_CONFIG['connection_string']
                )
                logger.info("✅ Azure SQL connection established")
            return self.sql_connection
        except Exception as e:
            logger.error(f"❌ Failed to connect to Azure SQL: {e}")
            return None
    
    async def initialize_database_schema(self):
        """Initialize database tables"""
        if not AZURE_AVAILABLE:
            return False
            
        try:
            conn = self.get_sql_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            for table_name, schema in DB_SCHEMA.items():
                try:
                    cursor.execute(schema)
                    conn.commit()
                    logger.info(f"✅ Table '{table_name}' created/verified")
                except Exception as e:
                    logger.warning(f"⚠️ Table '{table_name}' creation warning: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database schema: {e}")
            return False
    
    async def create_storage_containers(self):
        """Create necessary blob storage containers"""
        if not self.blob_service_client:
            return False
            
        containers = [
            AZURE_STORAGE_CONFIG['container_name'],
            AZURE_STORAGE_CONFIG['container_name_uploads'],
            AZURE_STORAGE_CONFIG['container_name_demos']
        ]
        
        try:
            for container_name in containers:
                try:
                    container_client = self.blob_service_client.get_container_client(container_name)
                    if not container_client.exists():
                        container_client.create_container()
                        logger.info(f"✅ Container '{container_name}' created")
                    else:
                        logger.info(f"✅ Container '{container_name}' exists")
                except Exception as e:
                    logger.warning(f"⚠️ Container '{container_name}' warning: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create storage containers: {e}")
            return False
    
    async def upload_audio_to_blob(self, audio_data: bytes, filename: str, container: str = None) -> Optional[str]:
        """Upload audio file to blob storage"""
        if not self.blob_service_client:
            return None
            
        try:
            container_name = container or AZURE_STORAGE_CONFIG['container_name']
            blob_name = f"tracks/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
            
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            
            blob_client.upload_blob(
                audio_data, 
                overwrite=True,
                content_settings={
                    'content_type': 'audio/wav',
                    'cache_control': 'max-age=3600'
                }
            )
            
            blob_url = blob_client.url
            logger.info(f"✅ Audio uploaded to blob: {blob_url}")
            return blob_url
            
        except Exception as e:
            logger.error(f"❌ Failed to upload audio to blob: {e}")
            return None
    
    async def save_track_to_database(self, track_data: Dict) -> bool:
        """Save generated track to database"""
        if not AZURE_AVAILABLE:
            return False
            
        try:
            conn = self.get_sql_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO tracks (id, user_id, title, prompt, genre, mood, duration, file_url, blob_name, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(insert_query, (
                track_data.get('id'),
                track_data.get('user_id'),
                track_data.get('title'),
                track_data.get('prompt'),
                track_data.get('genre'),
                track_data.get('mood'),
                track_data.get('duration'),
                track_data.get('file_url'),
                track_data.get('blob_name'),
                json.dumps(track_data.get('metadata', {})),
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"✅ Track saved to database: {track_data.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save track to database: {e}")
            return False
    
    async def get_user_tracks(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's tracks from database"""
        if not AZURE_AVAILABLE:
            return []
            
        try:
            conn = self.get_sql_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            
            query = """
                SELECT id, title, genre, mood, duration, file_url, created_at, metadata
                FROM tracks 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            
            cursor.execute(query, (user_id, limit))
            rows = cursor.fetchall()
            
            tracks = []
            for row in rows:
                track = {
                    'id': row[0],
                    'title': row[1],
                    'genre': row[2],
                    'mood': row[3],
                    'duration': row[4],
                    'url': row[5],  # Using 'url' instead of 'audioUrl' for consistency
                    'created_at': row[6].isoformat() if row[6] else None,
                    'metadata': json.loads(row[7]) if row[7] else {}
                }
                tracks.append(track)
            
            logger.info(f"✅ Retrieved {len(tracks)} tracks for user {user_id}")
            return tracks
            
        except Exception as e:
            logger.error(f"❌ Failed to get user tracks: {e}")
            return []
    
    async def get_demo_tracks(self, limit: int = 10) -> List[Dict]:
        """Get demo tracks for the hero section"""
        if not AZURE_AVAILABLE:
            return self._get_fallback_demo_tracks()
            
        try:
            conn = self.get_sql_connection()
            if not conn:
                return self._get_fallback_demo_tracks()
                
            cursor = conn.cursor()
            
            query = """
                SELECT id, title, genre, duration, file_url, play_count
                FROM demo_tracks 
                WHERE featured = 1
                ORDER BY play_count DESC, created_at DESC
                LIMIT ?
            """
            
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            
            demo_tracks = []
            for row in rows:
                track = {
                    'id': row[0],
                    'title': row[1],
                    'genre': row[2],
                    'duration': row[3],
                    'url': row[4],  # Using 'url' instead of 'audioUrl'
                    'play_count': row[5]
                }
                demo_tracks.append(track)
            
            if not demo_tracks:
                return self._get_fallback_demo_tracks()
            
            logger.info(f"✅ Retrieved {len(demo_tracks)} demo tracks")
            return demo_tracks
            
        except Exception as e:
            logger.error(f"❌ Failed to get demo tracks: {e}")
            return self._get_fallback_demo_tracks()
    
    def _get_fallback_demo_tracks(self) -> List[Dict]:
        """Fallback demo tracks when database is not available"""
        return [
            {
                'id': 'demo_1',
                'title': 'Epic Orchestral Journey',
                'genre': 'Cinematic',
                'duration': 45,
                'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'
            },
            {
                'id': 'demo_2',
                'title': 'Chill Lo-Fi Vibes',
                'genre': 'Electronic',
                'duration': 38,
                'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'
            },
            {
                'id': 'demo_3',
                'title': 'Energetic Rock Anthem',
                'genre': 'Rock',
                'duration': 52,
                'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'
            }
        ]
    
    async def generate_lyrics_with_openai(self, prompt: str, genre: str, mood: str) -> Optional[str]:
        """Generate lyrics using Azure OpenAI"""
        if not self.openai_client:
            return None
            
        try:
            system_prompt = f"""
            You are a professional songwriter. Generate creative, original lyrics for a {genre} song with a {mood} mood.
            The lyrics should be appropriate, engaging, and follow the typical structure of the genre.
            Keep the lyrics suitable for all audiences.
            """
            
            response = self.openai_client.chat.completions.create(
                model=AZURE_OPENAI_CONFIG['deployment_name'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create lyrics for: {prompt}"}
                ],
                max_tokens=AZURE_OPENAI_CONFIG['max_tokens'],
                temperature=AZURE_OPENAI_CONFIG['temperature']
            )
            
            lyrics = response.choices[0].message.content
            logger.info("✅ Lyrics generated successfully with Azure OpenAI")
            return lyrics
            
        except Exception as e:
            logger.error(f"❌ Failed to generate lyrics: {e}")
            return None
    
    async def update_user_quota(self, user_id: str, tracks_used: int = 1) -> bool:
        """Update user quota after track generation"""
        if not AZURE_AVAILABLE:
            return True  # Allow in demo mode
            
        try:
            conn = self.get_sql_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Update quota
            update_query = """
                UPDATE users 
                SET quota_daily_used = quota_daily_used + ?
                WHERE id = ?
            """
            
            cursor.execute(update_query, (tracks_used, user_id))
            conn.commit()
            
            logger.info(f"✅ Updated quota for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update user quota: {e}")
            return False
    
    async def get_user_quota(self, user_id: str) -> Dict:
        """Get user quota information"""
        if not AZURE_AVAILABLE:
            return {
                'daily_remaining': 50,
                'daily_limit': 50,
                'plan': 'free'
            }
            
        try:
            conn = self.get_sql_connection()
            if not conn:
                return {'daily_remaining': 50, 'daily_limit': 50, 'plan': 'free'}
                
            cursor = conn.cursor()
            
            query = """
                SELECT quota_daily_limit, quota_daily_used, plan
                FROM users 
                WHERE id = ?
            """
            
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row:
                daily_limit, daily_used, plan = row
                return {
                    'daily_remaining': max(0, daily_limit - daily_used),
                    'daily_limit': daily_limit,
                    'daily_used': daily_used,
                    'plan': plan
                }
            else:
                # Create new user with default quota
                await self.create_user(user_id, plan='free')
                return {
                    'daily_remaining': 50,
                    'daily_limit': 50,
                    'daily_used': 0,
                    'plan': 'free'
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get user quota: {e}")
            return {'daily_remaining': 50, 'daily_limit': 50, 'plan': 'free'}
    
    async def create_user(self, user_id: str, email: str = None, plan: str = 'free') -> bool:
        """Create new user in database"""
        if not AZURE_AVAILABLE:
            return True
            
        try:
            conn = self.get_sql_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO users (id, email, plan, quota_daily_limit, quota_daily_used, quota_reset_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            daily_limit = 50 if plan == 'free' else 500 if plan == 'creator' else 9999
            
            cursor.execute(insert_query, (
                user_id,
                email,
                plan,
                daily_limit,
                0,
                datetime.now().date(),
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"✅ User created: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            return False

# Global instance
azure_manager = AzureIntegrationManager()

# Initialization function
async def initialize_azure_services():
    """Initialize all Azure services"""
    if not azure_manager.initialized:
        logger.warning("⚠️ Azure services not initialized, running in demo mode")
        return False
        
    success = True
    
    # Initialize database schema
    if not await azure_manager.initialize_database_schema():
        logger.warning("⚠️ Failed to initialize database schema")
        success = False
    
    # Create storage containers
    if not await azure_manager.create_storage_containers():
        logger.warning("⚠️ Failed to create storage containers")
        success = False
    
    return success

# Export main functions
__all__ = [
    'azure_manager',
    'initialize_azure_services',
    'AzureIntegrationManager'
]

if __name__ == "__main__":
    # Test the Azure integration
    async def test_azure():
        print("🧪 Testing Azure Integration...")
        await initialize_azure_services()
        
        # Test demo tracks
        demo_tracks = await azure_manager.get_demo_tracks()
        print(f"📀 Demo tracks: {len(demo_tracks)}")
        
        # Test user quota
        quota = await azure_manager.get_user_quota('test_user')
        print(f"📊 User quota: {quota}")
    
    asyncio.run(test_azure())
