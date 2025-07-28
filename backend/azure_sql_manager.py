"""
Enhanced Azure SQL Database Integration
Complete schema for AI Music Portal with metadata management
Supports fine-tuning data, user management, and music generation tracking
"""

import pyodbc
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

logger = logging.getLogger(__name__)

class AzureSQLManager:
    """Enhanced Azure SQL Database manager for AI Music Portal"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.is_connected = False
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test database connection"""
        try:
            with pyodbc.connect(self.connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                self.is_connected = True
                logger.info("✅ Azure SQL Database connected successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Azure SQL connection failed: {e}")
            self.is_connected = False
            return False
    
    def create_database_schema(self) -> bool:
        """Create complete database schema for AI Music Portal"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
                    CREATE TABLE users (
                        id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                        email NVARCHAR(255) UNIQUE NOT NULL,
                        username NVARCHAR(100) UNIQUE NOT NULL,
                        password_hash NVARCHAR(255) NOT NULL,
                        plan NVARCHAR(50) DEFAULT 'free',
                        subscription_status NVARCHAR(50) DEFAULT 'active',
                        created_at DATETIME2 DEFAULT GETUTCDATE(),
                        updated_at DATETIME2 DEFAULT GETUTCDATE(),
                        last_login DATETIME2,
                        profile_data NVARCHAR(MAX), -- JSON
                        quota_daily INT DEFAULT 50,
                        quota_monthly INT DEFAULT 500,
                        quota_used_daily INT DEFAULT 0,
                        quota_used_monthly INT DEFAULT 0,
                        quota_reset_date DATETIME2 DEFAULT DATEADD(day, 1, GETUTCDATE())
                    )
                """)
                
                # Music tracks table (main repository)
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tracks' AND xtype='U')
                    CREATE TABLE tracks (
                        id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                        title NVARCHAR(255) NOT NULL,
                        artist NVARCHAR(255),
                        genre NVARCHAR(100),
                        mood NVARCHAR(100),
                        duration INT, -- in seconds
                        bpm INT,
                        key_signature NVARCHAR(10),
                        audio_url NVARCHAR(500),
                        download_url NVARCHAR(500),
                        preview_url NVARCHAR(500),
                        waveform_data NVARCHAR(MAX), -- JSON array
                        lyrics NVARCHAR(MAX),
                        description NVARCHAR(MAX),
                        tags NVARCHAR(MAX), -- JSON array
                        source NVARCHAR(100), -- jamendo, freesound, generated, etc.
                        source_id NVARCHAR(255),
                        license_type NVARCHAR(100),
                        license_url NVARCHAR(500),
                        is_public BIT DEFAULT 1,
                        is_featured BIT DEFAULT 0,
                        play_count INT DEFAULT 0,
                        download_count INT DEFAULT 0,
                        like_count INT DEFAULT 0,
                        created_at DATETIME2 DEFAULT GETUTCDATE(),
                        updated_at DATETIME2 DEFAULT GETUTCDATE(),
                        metadata NVARCHAR(MAX) -- JSON for additional metadata
                    )
                """)
                
                # User tracks (personal music library)
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='user_tracks' AND xtype='U')
                    CREATE TABLE user_tracks (
                        id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                        user_id UNIQUEIDENTIFIER NOT NULL,
                        track_id UNIQUEIDENTIFIER NOT NULL,
                        is_favorite BIT DEFAULT 0,
                        is_private BIT DEFAULT 0,
                        playlist_position INT,
                        created_at DATETIME2 DEFAULT GETUTCDATE(),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
                        UNIQUE(user_id, track_id)
                    )
                """)
                
                # Music generation requests
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='generation_requests' AND xtype='U')
                    CREATE TABLE generation_requests (
                        id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                        user_id UNIQUEIDENTIFIER NOT NULL,
                        prompt NVARCHAR(MAX) NOT NULL,
                        genre NVARCHAR(100),
                        mood NVARCHAR(100),
                        duration INT,
                        tempo INT,
                        key_signature NVARCHAR(10),
                        instruments NVARCHAR(MAX), -- JSON array
                        vocals BIT DEFAULT 0,
                        structure NVARCHAR(500),
                        lyrics_style NVARCHAR(100),
                        custom_tags NVARCHAR(MAX), -- JSON array
                        status NVARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
                        result_track_id UNIQUEIDENTIFIER,
                        error_message NVARCHAR(MAX),
                        processing_time_ms INT,
                        created_at DATETIME2 DEFAULT GETUTCDATE(),
                        completed_at DATETIME2,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (result_track_id) REFERENCES tracks(id)
                    )
                """)
                
                # AI training data (for fine-tuning)
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ai_training_data' AND xtype='U')
                    CREATE TABLE ai_training_data (
                        id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                        track_id UNIQUEIDENTIFIER NOT NULL,
                        prompt_used NVARCHAR(MAX),
                        generation_parameters NVARCHAR(MAX), -- JSON
                        user_feedback NVARCHAR(MAX), -- JSON
                        quality_score FLOAT,
                        usage_count INT DEFAULT 0,
                        is_approved_for_training BIT DEFAULT 0,
                        created_at DATETIME2 DEFAULT GETUTCDATE(),
                        FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
                    )
                """)
                
                # Free music data sources
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='free_music_sources' AND xtype='U')
                    CREATE TABLE free_music_sources (
                        id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                        source_name NVARCHAR(100) NOT NULL,
                        api_endpoint NVARCHAR(500),
                        last_sync_date DATETIME2,
                        total_tracks_synced INT DEFAULT 0,
                        sync_status NVARCHAR(50) DEFAULT 'pending',
                        api_key_required BIT DEFAULT 0,
                        rate_limit_per_second FLOAT DEFAULT 1.0,
                        is_active BIT DEFAULT 1,
                        created_at DATETIME2 DEFAULT GETUTCDATE(),
                        configuration NVARCHAR(MAX) -- JSON
                    )
                """)
                
                # User analytics and behavior tracking
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='user_analytics' AND xtype='U')
                    CREATE TABLE user_analytics (
                        id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                        user_id UNIQUEIDENTIFIER NOT NULL,
                        event_type NVARCHAR(100) NOT NULL, -- play, download, generate, like, etc.
                        track_id UNIQUEIDENTIFIER,
                        session_id NVARCHAR(255),
                        ip_address NVARCHAR(45),
                        user_agent NVARCHAR(500),
                        event_data NVARCHAR(MAX), -- JSON
                        created_at DATETIME2 DEFAULT GETUTCDATE(),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (track_id) REFERENCES tracks(id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_tracks_genre_mood')
                    CREATE INDEX IX_tracks_genre_mood ON tracks(genre, mood)
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_tracks_created_at')
                    CREATE INDEX IX_tracks_created_at ON tracks(created_at DESC)
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_user_tracks_user_id')
                    CREATE INDEX IX_user_tracks_user_id ON user_tracks(user_id)
                """)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_generation_requests_user_status')
                    CREATE INDEX IX_generation_requests_user_status ON generation_requests(user_id, status)
                """)
                
                conn.commit()
                logger.info("✅ Database schema created successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to create database schema: {e}")
            return False
    
    def insert_free_music_data(self, tracks_data: List[Dict]) -> int:
        """Insert free music data into the database"""
        if not self.is_connected:
            logger.error("❌ Database not connected")
            return 0
        
        inserted_count = 0
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                for track in tracks_data:
                    try:
                        # Check if track already exists
                        cursor.execute(
                            "SELECT id FROM tracks WHERE source = ? AND source_id = ?",
                            (track.get('source'), track.get('id'))
                        )
                        
                        if cursor.fetchone():
                            continue  # Skip if already exists
                        
                        # Insert new track
                        track_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO tracks (
                                id, title, artist, genre, mood, duration, audio_url, 
                                download_url, description, tags, source, source_id, 
                                license_type, license_url, metadata
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            track_id,
                            track.get('title', 'Unknown'),
                            track.get('artist', 'Unknown'),
                            track.get('genre', 'Various'),
                            track.get('mood', 'Neutral'),
                            track.get('duration', 0),
                            track.get('url', ''),
                            track.get('download_url', ''),
                            track.get('description', ''),
                            json.dumps(track.get('tags', [])),
                            track.get('source', 'unknown'),
                            track.get('id', ''),
                            track.get('license', 'Unknown'),
                            track.get('license', ''),
                            json.dumps(track.get('metadata', {}))
                        ))
                        
                        inserted_count += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to insert track {track.get('id')}: {e}")
                        continue
                
                conn.commit()
                logger.info(f"✅ Inserted {inserted_count} tracks into database")
                return inserted_count
                
        except Exception as e:
            logger.error(f"❌ Failed to insert free music data: {e}")
            return 0
    
    def get_user_music_library(self, user_id: str, genre: str = None, limit: int = 50) -> List[Dict]:
        """Get user's music library from database"""
        if not self.is_connected:
            return []
        
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT t.id, t.title, t.artist, t.genre, t.mood, t.duration, 
                           t.audio_url, t.created_at, t.tags, ut.is_favorite
                    FROM tracks t
                    INNER JOIN user_tracks ut ON t.id = ut.track_id
                    WHERE ut.user_id = ?
                """
                
                params = [user_id]
                
                if genre and genre != 'all':
                    query += " AND t.genre = ?"
                    params.append(genre)
                
                query += " ORDER BY t.created_at DESC"
                
                if limit:
                    query = f"SELECT TOP {limit} * FROM ({query}) AS limited_results"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                tracks = []
                for row in rows:
                    track = {
                        'id': str(row.id),
                        'title': row.title,
                        'artist': row.artist,
                        'genre': row.genre,
                        'mood': row.mood,
                        'duration': row.duration,
                        'url': row.audio_url,
                        'created_at': row.created_at.isoformat() if row.created_at else None,
                        'tags': json.loads(row.tags) if row.tags else [],
                        'is_favorite': bool(row.is_favorite)
                    }
                    tracks.append(track)
                
                return tracks
                
        except Exception as e:
            logger.error(f"❌ Failed to get user music library: {e}")
            return []
    
    def get_public_tracks(self, genre: str = None, limit: int = 50) -> List[Dict]:
        """Get public tracks for music library"""
        if not self.is_connected:
            return []
        
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT TOP (?) id, title, artist, genre, mood, duration, 
                           audio_url, created_at, tags, play_count
                    FROM tracks
                    WHERE is_public = 1
                """
                
                params = [limit]
                
                if genre and genre != 'all':
                    query += " AND genre = ?"
                    params.append(genre)
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                tracks = []
                for row in rows:
                    track = {
                        'id': str(row.id),
                        'title': row.title,
                        'artist': row.artist,
                        'genre': row.genre,
                        'mood': row.mood,
                        'duration': row.duration,
                        'url': row.audio_url,
                        'created_at': row.created_at.isoformat() if row.created_at else None,
                        'tags': json.loads(row.tags) if row.tags else [],
                        'play_count': row.play_count,
                        'is_favorite': False  # Default for public tracks
                    }
                    tracks.append(track)
                
                return tracks
                
        except Exception as e:
            logger.error(f"❌ Failed to get public tracks: {e}")
            return []
    
    def save_generation_request(self, user_id: str, generation_params: Dict) -> str:
        """Save music generation request to database"""
        if not self.is_connected:
            return None
        
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                request_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO generation_requests (
                        id, user_id, prompt, genre, mood, duration, tempo, 
                        key_signature, instruments, vocals, structure, 
                        lyrics_style, custom_tags, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request_id,
                    user_id,
                    generation_params.get('prompt', ''),
                    generation_params.get('genre', ''),
                    generation_params.get('mood', ''),
                    generation_params.get('duration', 30),
                    generation_params.get('tempo', 120),
                    generation_params.get('key', 'C'),
                    json.dumps(generation_params.get('instruments', [])),
                    generation_params.get('vocals', False),
                    generation_params.get('structure', ''),
                    generation_params.get('lyricsStyle', ''),
                    json.dumps(generation_params.get('customTags', [])),
                    'pending'
                ))
                
                conn.commit()
                logger.info(f"✅ Generation request saved: {request_id}")
                return request_id
                
        except Exception as e:
            logger.error(f"❌ Failed to save generation request: {e}")
            return None
    
    def update_generation_status(self, request_id: str, status: str, track_id: str = None, error: str = None):
        """Update generation request status"""
        if not self.is_connected:
            return False
        
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE generation_requests 
                    SET status = ?, result_track_id = ?, error_message = ?, completed_at = GETUTCDATE()
                    WHERE id = ?
                """, (status, track_id, error, request_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to update generation status: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        if not self.is_connected:
            return {}
        
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count tracks
                cursor.execute("SELECT COUNT(*) FROM tracks")
                stats['total_tracks'] = cursor.fetchone()[0]
                
                # Count users
                cursor.execute("SELECT COUNT(*) FROM users")
                stats['total_users'] = cursor.fetchone()[0]
                
                # Count generation requests
                cursor.execute("SELECT COUNT(*) FROM generation_requests")
                stats['total_generations'] = cursor.fetchone()[0]
                
                # Count by status
                cursor.execute("SELECT status, COUNT(*) FROM generation_requests GROUP BY status")
                status_counts = cursor.fetchall()
                stats['generation_status'] = {row[0]: row[1] for row in status_counts}
                
                # Count by genre
                cursor.execute("SELECT genre, COUNT(*) FROM tracks GROUP BY genre ORDER BY COUNT(*) DESC")
                genre_counts = cursor.fetchall()
                stats['tracks_by_genre'] = {row[0]: row[1] for row in genre_counts[:10]}
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {}
