"""
Azure Services Integration for AI Music Portal
Handles Azure SQL Database, Azure Blob Storage, and Azure OpenAI integration
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import json
import uuid
import asyncio
from typing import Optional, Dict, List, Any

# Azure imports
try:
    import pyodbc
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.keyvault.secrets import SecretClient
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError as e:
    print(f"Azure SDK not available: {e}", file=sys.stderr)
    AZURE_AVAILABLE = False

# Configuration from environment variables (UPDATED WITH PROVIDED CREDENTIALS)
AZURE_CONFIG = {
    'SP_APP_ID': "6a069624-67ed-4bfe-b4e6-301f6e02a853",
    'SP_PASSWORD': "Q9a8Q~XRiQ3hKIHKUCFn6ka.jZ3udfNwyI.s2aC5",
    'SP_TENANT': "bca013b2-c163-4a0d-ad43-e6f1d3cda34b",
    'RESOURCE_GROUP': "rg-portal-ai-music",
    'SUBSCRIPTION_ID': os.getenv('AZURE_SUBSCRIPTION_ID', ''),
    
    # Storage Account
    'STORAGE_ACCOUNT_NAME': "portalaimusicstg",
    'STORAGE_CONTAINER': "audio-files",
    'STORAGE_CONNECTION_STRING': os.getenv('AZURE_STORAGE_CONNECTION_STRING', ''),
    
    # SQL Database
    'SQL_SERVER': "portal-ai-music-sql.database.windows.net",
    'SQL_DATABASE': "portal-ai-music-db",
    'SQL_USERNAME': os.getenv('AZURE_SQL_USERNAME', 'sqladmin'),
    'SQL_PASSWORD': os.getenv('AZURE_SQL_PASSWORD', ''),
    
    # Key Vault (optional)
    'KEY_VAULT_URL': os.getenv('AZURE_KEY_VAULT_URL', 'https://portal-ai-music-kv.vault.azure.net/'),
    
    # OpenAI (if using Azure OpenAI)
    'OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT', ''),
    'OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY', ''),
    'OPENAI_DEPLOYMENT': os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4'),
}

class AzureStorageManager:
    """Manages Azure Blob Storage operations for audio files"""
    
    def __init__(self):
        self.blob_service_client = None
        self.container_client = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize Azure Blob Storage client"""
        if not AZURE_AVAILABLE:
            print("Azure SDK not available for storage operations", file=sys.stderr)
            return
        
        try:
            # Try connection string first
            if AZURE_CONFIG['STORAGE_CONNECTION_STRING']:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    AZURE_CONFIG['STORAGE_CONNECTION_STRING']
                )
            else:
                # Use service principal authentication
                credential = ClientSecretCredential(
                    tenant_id=AZURE_CONFIG['SP_TENANT'],
                    client_id=AZURE_CONFIG['SP_APP_ID'],
                    client_secret=AZURE_CONFIG['SP_PASSWORD']
                )
                
                account_url = f"https://{AZURE_CONFIG['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=credential
                )
            
            # Get container client
            self.container_client = self.blob_service_client.get_container_client(
                AZURE_CONFIG['STORAGE_CONTAINER']
            )
            
            # Ensure container exists
            try:
                self.container_client.create_container()
                print(f"✅ Created container: {AZURE_CONFIG['STORAGE_CONTAINER']}")
            except Exception:
                print(f"✅ Container already exists: {AZURE_CONFIG['STORAGE_CONTAINER']}")
            
            print("✅ Azure Blob Storage initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Azure Blob Storage: {e}", file=sys.stderr)
            self.blob_service_client = None
            self.container_client = None
    
    def upload_audio_file(self, file_path: str, blob_name: str) -> Optional[str]:
        """Upload audio file to Azure Blob Storage"""
        if not self.container_client:
            print("❌ Azure Blob Storage not available", file=sys.stderr)
            return None
        
        try:
            with open(file_path, 'rb') as data:
                blob_client = self.container_client.upload_blob(
                    name=blob_name,
                    data=data,
                    overwrite=True,
                    content_settings={
                        'content_type': 'audio/wav'
                    }
                )
            
            # Return public URL
            blob_url = f"https://{AZURE_CONFIG['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net/{AZURE_CONFIG['STORAGE_CONTAINER']}/{blob_name}"
            print(f"✅ Uploaded audio file: {blob_url}")
            return blob_url
            
        except Exception as e:
            print(f"❌ Failed to upload audio file: {e}", file=sys.stderr)
            return None
    
    def delete_audio_file(self, blob_name: str) -> bool:
        """Delete audio file from Azure Blob Storage"""
        if not self.container_client:
            return False
        
        try:
            self.container_client.delete_blob(blob_name)
            print(f"✅ Deleted audio file: {blob_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete audio file: {e}", file=sys.stderr)
            return False
    
    def list_audio_files(self) -> List[str]:
        """List all audio files in storage"""
        if not self.container_client:
            return []
        
        try:
            blobs = self.container_client.list_blobs()
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"❌ Failed to list audio files: {e}", file=sys.stderr)
            return []

class AzureSQLManager:
    """Manages Azure SQL Database operations"""
    
    def __init__(self):
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize Azure SQL Database connection"""
        if not AZURE_AVAILABLE:
            print("Azure SDK not available for database operations", file=sys.stderr)
            return
        
        try:
            # Connection string for Azure SQL
            connection_string = (
                f"Driver={{ODBC Driver 18 for SQL Server}};"
                f"Server=tcp:{AZURE_CONFIG['SQL_SERVER']},1433;"
                f"Database={AZURE_CONFIG['SQL_DATABASE']};"
                f"Uid={AZURE_CONFIG['SQL_USERNAME']};"
                f"Pwd={AZURE_CONFIG['SQL_PASSWORD']};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout=30;"
            )
            
            self.connection = pyodbc.connect(connection_string)
            print("✅ Azure SQL Database connected successfully")
            
            # Create tables if they don't exist
            self._create_tables()
            
        except Exception as e:
            print(f"❌ Failed to connect to Azure SQL: {e}", file=sys.stderr)
            self.connection = None
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Users table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
                CREATE TABLE users (
                    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                    email NVARCHAR(255) UNIQUE NOT NULL,
                    plan NVARCHAR(50) DEFAULT 'free',
                    quota_used INT DEFAULT 0,
                    quota_limit INT DEFAULT 10,
                    created_at DATETIME2 DEFAULT GETDATE(),
                    updated_at DATETIME2 DEFAULT GETDATE()
                )
            """)
            
            # Tracks table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tracks' AND xtype='U')
                CREATE TABLE tracks (
                    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                    user_id UNIQUEIDENTIFIER REFERENCES users(id),
                    title NVARCHAR(255) NOT NULL,
                    prompt NTEXT,
                    genre NVARCHAR(100),
                    mood NVARCHAR(100),
                    duration INT,
                    tempo INT,
                    key_signature NVARCHAR(10),
                    instruments NTEXT,
                    effects NTEXT,
                    structure NVARCHAR(255),
                    audio_url NVARCHAR(500),
                    blob_name NVARCHAR(255),
                    file_size INT,
                    created_at DATETIME2 DEFAULT GETDATE(),
                    updated_at DATETIME2 DEFAULT GETDATE()
                )
            """)
            
            # User library table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='user_library' AND xtype='U')
                CREATE TABLE user_library (
                    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                    user_id UNIQUEIDENTIFIER REFERENCES users(id),
                    track_id UNIQUEIDENTIFIER REFERENCES tracks(id),
                    is_favorite BIT DEFAULT 0,
                    playlist_id UNIQUEIDENTIFIER NULL,
                    added_at DATETIME2 DEFAULT GETDATE()
                )
            """)
            
            # Playlists table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='playlists' AND xtype='U')
                CREATE TABLE playlists (
                    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                    user_id UNIQUEIDENTIFIER REFERENCES users(id),
                    name NVARCHAR(255) NOT NULL,
                    description NTEXT,
                    is_public BIT DEFAULT 0,
                    created_at DATETIME2 DEFAULT GETDATE(),
                    updated_at DATETIME2 DEFAULT GETDATE()
                )
            """)
            
            self.connection.commit()
            print("✅ Database tables created/verified successfully")
            
        except Exception as e:
            print(f"❌ Failed to create database tables: {e}", file=sys.stderr)
            if self.connection:
                self.connection.rollback()
    
    def create_user(self, email: str, plan: str = 'free') -> Optional[str]:
        """Create a new user"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor()
            user_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO users (id, email, plan)
                VALUES (?, ?, ?)
            """, (user_id, email, plan))
            
            self.connection.commit()
            print(f"✅ Created user: {email}")
            return user_id
            
        except Exception as e:
            print(f"❌ Failed to create user: {e}", file=sys.stderr)
            if self.connection:
                self.connection.rollback()
            return None
    
    def save_track(self, track_data: Dict[str, Any]) -> Optional[str]:
        """Save a generated track to database"""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor()
            track_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO tracks (
                    id, user_id, title, prompt, genre, mood, duration,
                    tempo, key_signature, instruments, effects, structure,
                    audio_url, blob_name, file_size
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track_id,
                track_data.get('user_id'),
                track_data.get('title'),
                track_data.get('prompt'),
                track_data.get('genre'),
                track_data.get('mood'),
                track_data.get('duration'),
                track_data.get('tempo'),
                track_data.get('key'),
                json.dumps(track_data.get('instruments', [])),
                json.dumps(track_data.get('effects', [])),
                track_data.get('structure'),
                track_data.get('audio_url'),
                track_data.get('blob_name'),
                track_data.get('file_size')
            ))
            
            self.connection.commit()
            print(f"✅ Saved track: {track_data.get('title')}")
            return track_id
            
        except Exception as e:
            print(f"❌ Failed to save track: {e}", file=sys.stderr)
            if self.connection:
                self.connection.rollback()
            return None
    
    def get_user_tracks(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's tracks from database"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    id, title, prompt, genre, mood, duration, tempo,
                    key_signature, instruments, effects, structure,
                    audio_url, created_at
                FROM tracks
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            tracks = []
            for row in cursor.fetchall():
                tracks.append({
                    'id': str(row[0]),
                    'title': row[1],
                    'prompt': row[2],
                    'genre': row[3],
                    'mood': row[4],
                    'duration': row[5],
                    'tempo': row[6],
                    'key': row[7],
                    'instruments': json.loads(row[8]) if row[8] else [],
                    'effects': json.loads(row[9]) if row[9] else [],
                    'structure': row[10],
                    'url': row[11],
                    'created_at': row[12].isoformat() if row[12] else None
                })
            
            return tracks
            
        except Exception as e:
            print(f"❌ Failed to get user tracks: {e}", file=sys.stderr)
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

class AzureIntegration:
    """Main Azure integration class"""
    
    def __init__(self):
        self.storage = AzureStorageManager()
        self.database = AzureSQLManager()
        self.enabled = AZURE_AVAILABLE and (
            self.storage.blob_service_client is not None or 
            self.database.connection is not None
        )
    
    def is_available(self) -> bool:
        """Check if Azure integration is available"""
        return self.enabled
    
    def save_generated_track(self, audio_file_path: str, track_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save a generated track to Azure (both storage and database)"""
        try:
            # Generate unique blob name
            blob_name = f"tracks/{uuid.uuid4()}.wav"
            
            # Upload to Azure Blob Storage
            audio_url = None
            if self.storage.blob_service_client:
                audio_url = self.storage.upload_audio_file(audio_file_path, blob_name)
            
            # Save metadata to Azure SQL
            track_data = {
                **track_metadata,
                'audio_url': audio_url,
                'blob_name': blob_name,
                'file_size': os.path.getsize(audio_file_path) if os.path.exists(audio_file_path) else 0
            }
            
            track_id = None
            if self.database.connection:
                track_id = self.database.save_track(track_data)
            
            return {
                'track_id': track_id,
                'audio_url': audio_url,
                'blob_name': blob_name,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Failed to save track to Azure: {e}", file=sys.stderr)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_music_library(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's music library from Azure SQL"""
        if self.database.connection:
            return self.database.get_user_tracks(user_id)
        return []
    
    def cleanup(self):
        """Clean up Azure connections"""
        if self.database:
            self.database.close()

# Global Azure integration instance
azure_integration = AzureIntegration()

def get_azure_integration() -> AzureIntegration:
    """Get the global Azure integration instance"""
    return azure_integration

# Test Azure connectivity
def test_azure_connectivity():
    """Test Azure services connectivity"""
    print("🧪 Testing Azure connectivity...")
    
    integration = get_azure_integration()
    
    if integration.is_available():
        print("✅ Azure integration is available")
        
        # Test storage
        if integration.storage.blob_service_client:
            files = integration.storage.list_audio_files()
            print(f"✅ Azure Blob Storage: {len(files)} files found")
        else:
            print("❌ Azure Blob Storage: Not available")
        
        # Test database
        if integration.database.connection:
            print("✅ Azure SQL Database: Connected")
        else:
            print("❌ Azure SQL Database: Not available")
    else:
        print("❌ Azure integration is not available")
    
    return integration.is_available()

if __name__ == "__main__":
    # Test connectivity when run directly
    test_azure_connectivity()
