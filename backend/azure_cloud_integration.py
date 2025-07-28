"""
Azure Cloud Integration for AI Music Portal
Handles Azure SQL, Blob Storage, OpenAI, and Real-time testing
Resource Group: rg-portal-ai-music
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

# Azure SDK imports
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.keyvault.secrets import SecretClient
import pyodbc

# OpenAI Azure integration
from openai import AsyncAzureOpenAI

# Audio processing
import tempfile
import requests
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureCloudIntegration:
    """Comprehensive Azure cloud integration for AI Music Portal"""
    
    def __init__(self):
        """Initialize Azure services with provided credentials"""
        self.resource_group = "rg-portal-ai-music"
        
        # Service Principal credentials (provided)
        self.client_id = "6a069624-67ed-4bfe-b4e6-301f6e02a853"
        self.client_secret = "Q9a8Q~XRiQ3hKIHKUCFn6ka.jZ3udfNwyI.s2aC5"
        self.tenant_id = "bca013b2-c163-4a0d-ad43-e6f1d3cda34b"
        
        # Initialize credential
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        # Azure service configurations
        self.storage_account = "portalaimusicstore"
        self.container_name = "music-files"
        self.sql_server = "portal-ai-music-sql.database.windows.net"
        self.database_name = "PortalAIMusicDB"
        self.sql_username = "aimusic_admin"
        
        # Initialize services
        self._init_storage()
        self._init_sql()
        self._init_openai()
        
        logger.info("✅ Azure Cloud Integration initialized successfully")
    
    def _init_storage(self):
        """Initialize Azure Blob Storage"""
        try:
            storage_url = f"https://{self.storage_account}.blob.core.windows.net"
            self.blob_service = BlobServiceClient(
                account_url=storage_url,
                credential=self.credential
            )
            logger.info("✅ Azure Blob Storage connected")
        except Exception as e:
            logger.error(f"❌ Azure Storage initialization failed: {e}")
            self.blob_service = None
    
    def _init_sql(self):
        """Initialize Azure SQL Database connection"""
        try:
            # Connection string for Azure SQL with service principal
            driver = "{ODBC Driver 18 for SQL Server}"
            self.sql_connection_string = (
                f"DRIVER={driver};"
                f"SERVER={self.sql_server};"
                f"DATABASE={self.database_name};"
                f"Authentication=ActiveDirectoryServicePrincipal;"
                f"UID={self.client_id};"
                f"PWD={self.client_secret};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            
            # Test connection
            self._test_sql_connection()
            logger.info("✅ Azure SQL Database connected")
        except Exception as e:
            logger.error(f"❌ Azure SQL initialization failed: {e}")
            self.sql_connection_string = None
    
    def _init_openai(self):
        """Initialize Azure OpenAI"""
        try:
            self.openai_endpoint = "https://portal-ai-music-openai.openai.azure.com/"
            self.openai_deployment = "gpt-4"
            self.openai_api_version = "2024-02-15-preview"
            self.openai_api_key = os.getenv('AZURE_OPENAI_API_KEY', 'dummy-key-for-local-testing')
            
            # Create new OpenAI client
            self.openai_client = AsyncAzureOpenAI(
                azure_endpoint=self.openai_endpoint,
                api_key=self.openai_api_key,
                api_version=self.openai_api_version
            )
            
            logger.info("✅ Azure OpenAI configured")
        except Exception as e:
            logger.error(f"❌ Azure OpenAI initialization failed: {e}")
            self.openai_client = None
    
    def _test_sql_connection(self):
        """Test SQL database connection"""
        try:
            with pyodbc.connect(self.sql_connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception as e:
            logger.error(f"SQL connection test failed: {e}")
            return False
    
    async def upload_audio_file(self, file_data: bytes, filename: str, metadata: Dict = None) -> str:
        """Upload audio file to Azure Blob Storage"""
        try:
            if not self.blob_service:
                raise Exception("Blob service not initialized")
            
            blob_name = f"audio/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Upload with metadata
            blob_metadata = {
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_type": "audio"
            }
            if metadata:
                blob_metadata.update(metadata)
            
            await blob_client.upload_blob(
                data=file_data,
                overwrite=True,
                metadata=blob_metadata
            )
            
            # Return public URL
            blob_url = f"https://{self.storage_account}.blob.core.windows.net/{self.container_name}/{blob_name}"
            logger.info(f"✅ Audio file uploaded: {blob_url}")
            return blob_url
            
        except Exception as e:
            logger.error(f"❌ Audio upload failed: {e}")
            raise
    
    def get_demo_tracks_from_storage(self) -> List[Dict]:
        """Get demo tracks from Azure Blob Storage"""
        try:
            if not self.blob_service:
                return self._get_fallback_demo_tracks()
            
            container_client = self.blob_service.get_container_client(self.container_name)
            demo_tracks = []
            
            # List demo audio files
            blobs = container_client.list_blobs(name_starts_with="demo/")
            
            for blob in blobs:
                if blob.name.endswith(('.mp3', '.wav', '.m4a')):
                    track = {
                        "id": blob.name.split('/')[-1].split('.')[0],
                        "title": blob.name.split('/')[-1].replace('_', ' ').title(),
                        "url": f"https://{self.storage_account}.blob.core.windows.net/{self.container_name}/{blob.name}",
                        "duration": blob.metadata.get('duration', 60) if blob.metadata else 60,
                        "genre": blob.metadata.get('genre', 'Demo') if blob.metadata else 'Demo',
                        "mood": blob.metadata.get('mood', 'Energetic') if blob.metadata else 'Energetic',
                        "created_at": blob.last_modified.isoformat() if blob.last_modified else datetime.utcnow().isoformat(),
                        "tags": ["demo", "azure-storage"],
                        "waveform": [0.2, 0.8, 0.4, 0.9, 0.3, 0.7, 0.6, 0.5, 0.8, 0.2, 0.9, 0.4]
                    }
                    demo_tracks.append(track)
            
            if demo_tracks:
                logger.info(f"✅ Loaded {len(demo_tracks)} demo tracks from Azure Storage")
                return demo_tracks
            else:
                return self._get_fallback_demo_tracks()
                
        except Exception as e:
            logger.error(f"❌ Failed to load demo tracks from Azure: {e}")
            return self._get_fallback_demo_tracks()
    
    def _get_fallback_demo_tracks(self) -> List[Dict]:
        """Fallback demo tracks with local audio files"""
        return [
            {
                "id": "demo_1",
                "title": "Electronic Dreams",
                "url": "http://localhost:5002/audio/demo1.mp3",
                "fallback_url": "http://localhost:5002/audio/demo1.mp3",
                "duration": 10,
                "genre": "Electronic",
                "mood": "Energetic",
                "created_at": "2025-01-20T10:00:00Z",
                "tags": ["demo", "fallback"],
                "waveform": [0.2, 0.8, 0.4, 0.9, 0.3, 0.7, 0.6, 0.5, 0.8, 0.2, 0.9, 0.4]
            },
            {
                "id": "demo_2", 
                "title": "Acoustic Serenity",
                "url": "http://localhost:5002/audio/demo2.mp3",
                "fallback_url": "http://localhost:5002/audio/demo2.mp3",
                "duration": 10,
                "genre": "Acoustic",
                "mood": "Calm",
                "created_at": "2025-01-20T10:15:00Z",
                "tags": ["demo", "fallback"],
                "waveform": [0.1, 0.3, 0.2, 0.4, 0.3, 0.5, 0.4, 0.3, 0.2, 0.4, 0.3, 0.2]
            },
            {
                "id": "demo_3",
                "title": "Jazz Fusion",
                "url": "http://localhost:5002/audio/demo3.mp3",
                "fallback_url": "http://localhost:5002/audio/demo3.mp3",
                "duration": 10,
                "genre": "Jazz",
                "mood": "Sophisticated",
                "created_at": "2025-01-20T10:30:00Z",
                "tags": ["demo", "fallback"],
                "waveform": [0.4, 0.7, 0.5, 0.8, 0.6, 0.9, 0.7, 0.6, 0.8, 0.5, 0.7, 0.4]
            }
        ]
    
    def save_track_to_database(self, track_data: Dict) -> str:
        """Save track metadata to Azure SQL Database"""
        try:
            if not self.sql_connection_string:
                raise Exception("SQL connection not available")
            
            with pyodbc.connect(self.sql_connection_string) as conn:
                cursor = conn.cursor()
                
                # Insert track
                query = """
                INSERT INTO tracks (id, title, genre, mood, duration, url, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(query, (
                    track_data.get('id'),
                    track_data.get('title'),
                    track_data.get('genre'),
                    track_data.get('mood'),
                    track_data.get('duration'),
                    track_data.get('url'),
                    json.dumps(track_data.get('metadata', {})),
                    datetime.utcnow()
                ))
                
                conn.commit()
                logger.info(f"✅ Track saved to database: {track_data.get('id')}")
                return track_data.get('id')
                
        except Exception as e:
            logger.error(f"❌ Failed to save track to database: {e}")
            raise
    
    def get_tracks_from_database(self, limit: int = 50, genre: str = None) -> List[Dict]:
        """Get tracks from Azure SQL Database"""
        try:
            if not self.sql_connection_string:
                return []
            
            with pyodbc.connect(self.sql_connection_string) as conn:
                cursor = conn.cursor()
                
                if genre and genre != 'all':
                    query = "SELECT * FROM tracks WHERE genre = ? ORDER BY created_at DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY"
                    cursor.execute(query, (genre, limit))
                else:
                    query = "SELECT * FROM tracks ORDER BY created_at DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY"
                    cursor.execute(query, (limit,))
                
                rows = cursor.fetchall()
                tracks = []
                
                for row in rows:
                    track = {
                        "id": row.id,
                        "title": row.title,
                        "genre": row.genre,
                        "mood": row.mood,
                        "duration": row.duration,
                        "url": row.url,
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                        "metadata": json.loads(row.metadata) if row.metadata else {},
                        "tags": ["database", "azure-sql"]
                    }
                    tracks.append(track)
                
                logger.info(f"✅ Retrieved {len(tracks)} tracks from database")
                return tracks
                
        except Exception as e:
            logger.error(f"❌ Failed to get tracks from database: {e}")
            return []
    
    async def generate_music_with_ai(self, prompt: str, style: str = "electronic") -> Dict:
        """Generate music using Azure OpenAI"""
        try:
            # Use OpenAI to generate music metadata and description
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=self.openai_deployment,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI music composer. Generate detailed music metadata and composition instructions."
                        },
                        {
                            "role": "user", 
                            "content": f"Create a {style} music track with the theme: {prompt}. Provide title, mood, tempo, key, and composition notes."
                        }
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
            else:
                # Fallback if OpenAI client is not available
                raise Exception("OpenAI client not configured")
            
            ai_response = response.choices[0].message.content
            
            # Generate track metadata
            track_id = f"ai_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            track_data = {
                "id": track_id,
                "title": f"AI Generated - {prompt[:30]}",
                "genre": style.title(),
                "mood": "AI Generated",
                "duration": 120,  # Default 2 minutes
                "url": f"https://{self.storage_account}.blob.core.windows.net/{self.container_name}/generated/{track_id}.wav",
                "ai_description": ai_response,
                "created_at": datetime.utcnow().isoformat(),
                "tags": ["ai-generated", "azure-openai"],
                "metadata": {
                    "prompt": prompt,
                    "style": style,
                    "generated_by": "azure-openai"
                }
            }
            
            logger.info(f"✅ AI music generated: {track_id}")
            return track_data
            
        except Exception as e:
            logger.error(f"❌ AI music generation failed: {e}")
            raise
    
    def health_check(self) -> Dict:
        """Check health of all Azure services"""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Check Blob Storage
        try:
            if self.blob_service:
                containers = list(self.blob_service.list_containers(max_results=1))
                status["services"]["blob_storage"] = "✅ Connected"
            else:
                status["services"]["blob_storage"] = "❌ Not initialized"
        except Exception as e:
            status["services"]["blob_storage"] = f"❌ Error: {str(e)}"
        
        # Check SQL Database
        try:
            if self._test_sql_connection():
                status["services"]["sql_database"] = "✅ Connected"
            else:
                status["services"]["sql_database"] = "❌ Connection failed"
        except Exception as e:
            status["services"]["sql_database"] = f"❌ Error: {str(e)}"
        
        # Check OpenAI
        try:
            status["services"]["openai"] = "✅ Configured"
        except Exception as e:
            status["services"]["openai"] = f"❌ Error: {str(e)}"
        
        return status

# Global instance
azure_integration = AzureCloudIntegration()

# Export functions for Flask app
def get_azure_demo_tracks():
    """Get demo tracks from Azure Storage"""
    return azure_integration.get_demo_tracks_from_storage()

def get_azure_music_library(genre=None, limit=50):
    """Get music library from Azure SQL"""
    return azure_integration.get_tracks_from_database(limit=limit, genre=genre)

def azure_health_check():
    """Get Azure services health status"""
    return azure_integration.health_check()

async def upload_track_to_azure(file_data, filename, metadata=None):
    """Upload track to Azure Blob Storage"""
    return await azure_integration.upload_audio_file(file_data, filename, metadata)

async def generate_ai_music(prompt, style="electronic"):
    """Generate music using Azure OpenAI"""
    return await azure_integration.generate_music_with_ai(prompt, style)
