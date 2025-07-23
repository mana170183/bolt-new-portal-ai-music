"""
Database connection and operations for AI Music Platform
Handles SQL Server connectivity and data operations
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import traceback

# Database connectivity imports
try:
    import pymssql
    import pyodbc
    DATABASE_AVAILABLE = True
    print("🔗 Database drivers loaded successfully")
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"⚠️ Database drivers not available: {e}")

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv('AZURE_SQL_CONNECTION_STRING') or os.getenv('SQL_CONNECTION_STRING')
        self.connection = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """Establish database connection"""
        if not DATABASE_AVAILABLE:
            print("❌ Database drivers not available")
            return False
            
        if not self.connection_string:
            print("❌ No database connection string found")
            return False
            
        try:
            # Try pyodbc first (more reliable for Azure SQL)
            if 'driver=' in self.connection_string.lower() or 'odbc' in self.connection_string.lower():
                self.connection = pyodbc.connect(self.connection_string)
                print("✅ Connected to database via pyodbc")
            else:
                # Parse connection string for pymssql
                parts = dict(item.split('=') for item in self.connection_string.split(';') if '=' in item)
                server = parts.get('Server', parts.get('server'))
                database = parts.get('Database', parts.get('database'))
                username = parts.get('User Id', parts.get('uid'))
                password = parts.get('Password', parts.get('pwd'))
                
                self.connection = pymssql.connect(
                    server=server,
                    database=database,
                    user=username,
                    password=password
                )
                print("✅ Connected to database via pymssql")
                
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.is_connected = False
            return False
    
    def ensure_connection(self) -> bool:
        """Ensure database connection is active"""
        if not self.is_connected or not self.connection:
            return self.connect()
        return True
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        if not self.ensure_connection():
            return []
            
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all rows and convert to list of dictionaries
            rows = cursor.fetchall()
            results = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    row_dict[column] = row[i]
                results.append(row_dict)
            
            cursor.close()
            return results
            
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            traceback.print_exc()
            return []
    
    def execute_non_query(self, query: str, params: tuple = None) -> bool:
        """Execute INSERT/UPDATE/DELETE query"""
        if not self.ensure_connection():
            return False
            
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"❌ Non-query execution failed: {e}")
            traceback.print_exc()
            return False
    
    def get_genres(self) -> List[Dict]:
        """Get all genres from database"""
        query = """
        SELECT genre_code, name, description, bpm_range_min, bpm_range_max,
               key_signatures, chord_progressions, instruments, production_style
        FROM genres
        ORDER BY name
        """
        results = self.execute_query(query)
        
        # Parse JSON fields
        for result in results:
            for json_field in ['key_signatures', 'chord_progressions', 'instruments', 'production_style']:
                if result.get(json_field):
                    try:
                        result[json_field] = json.loads(result[json_field])
                    except:
                        result[json_field] = []
        
        return results
    
    def get_moods(self) -> List[Dict]:
        """Get all moods from database"""
        query = """
        SELECT mood_code, name, description, energy_level, valence, arousal,
               audio_parameters, color_code
        FROM moods
        ORDER BY name
        """
        results = self.execute_query(query)
        
        # Parse JSON audio_parameters
        for result in results:
            if result.get('audio_parameters'):
                try:
                    result['audio_parameters'] = json.loads(result['audio_parameters'])
                except:
                    result['audio_parameters'] = {}
        
        return results
    
    def get_genre_by_code(self, genre_code: str) -> Optional[Dict]:
        """Get specific genre by code"""
        query = """
        SELECT genre_code, name, description, bpm_range_min, bpm_range_max,
               key_signatures, chord_progressions, instruments, production_style
        FROM genres
        WHERE genre_code = ?
        """
        results = self.execute_query(query, (genre_code,))
        
        if results:
            result = results[0]
            # Parse JSON fields
            for json_field in ['key_signatures', 'chord_progressions', 'instruments', 'production_style']:
                if result.get(json_field):
                    try:
                        result[json_field] = json.loads(result[json_field])
                    except:
                        result[json_field] = []
            return result
        return None
    
    def get_mood_by_code(self, mood_code: str) -> Optional[Dict]:
        """Get specific mood by code"""
        query = """
        SELECT mood_code, name, description, energy_level, valence, arousal,
               audio_parameters, color_code
        FROM moods
        WHERE mood_code = ?
        """
        results = self.execute_query(query, (mood_code,))
        
        if results:
            result = results[0]
            if result.get('audio_parameters'):
                try:
                    result['audio_parameters'] = json.loads(result['audio_parameters'])
                except:
                    result['audio_parameters'] = {}
            return result
        return None
    
    def get_training_tracks(self, genre_code: str = None, mood_code: str = None, limit: int = 100) -> List[Dict]:
        """Get training tracks filtered by genre/mood"""
        query = """
        SELECT t.track_name, t.artist_name, t.duration_seconds, t.bpm,
               t.key_signature, t.audio_features, t.file_path,
               g.genre_code, g.name as genre_name,
               m.mood_code, m.name as mood_name
        FROM training_tracks t
        LEFT JOIN genres g ON t.genre_id = g.id
        LEFT JOIN moods m ON t.mood_id = m.id
        WHERE t.is_processed = 1
        """
        params = []
        
        if genre_code:
            query += " AND g.genre_code = ?"
            params.append(genre_code)
            
        if mood_code:
            query += " AND m.mood_code = ?"
            params.append(mood_code)
            
        query += f" ORDER BY t.quality_score DESC, t.created_at DESC OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
        
        results = self.execute_query(query, tuple(params) if params else None)
        
        # Parse JSON audio_features
        for result in results:
            if result.get('audio_features'):
                try:
                    result['audio_features'] = json.loads(result['audio_features'])
                except:
                    result['audio_features'] = {}
        
        return results
    
    def save_generated_track(self, track_data: Dict) -> bool:
        """Save generated track metadata to database"""
        query = """
        INSERT INTO generated_tracks 
        (track_id, user_prompt, genre_id, mood_id, duration_seconds, parameters,
         file_path, file_size_bytes, audio_format, generation_model, generation_time_seconds)
        SELECT ?, ?, g.id, m.id, ?, ?, ?, ?, ?, ?, ?
        FROM genres g, moods m
        WHERE g.genre_code = ? AND m.mood_code = ?
        """
        
        params = (
            track_data.get('track_id'),
            track_data.get('user_prompt', ''),
            track_data.get('duration_seconds'),
            json.dumps(track_data.get('parameters', {})),
            track_data.get('file_path'),
            track_data.get('file_size_bytes'),
            track_data.get('audio_format', 'wav'),
            track_data.get('generation_model', 'ai_music_core'),
            track_data.get('generation_time_seconds'),
            track_data.get('genre_code'),
            track_data.get('mood_code')
        )
        
        return self.execute_non_query(query, params)
    
    def get_composition_templates(self, genre_code: str = None) -> List[Dict]:
        """Get composition templates"""
        query = """
        SELECT t.template_name, t.structure, t.description, t.difficulty_level,
               t.instruments, g.genre_code, g.name as genre_name
        FROM composition_templates t
        LEFT JOIN genres g ON t.genre_id = g.id
        WHERE 1=1
        """
        params = []
        
        if genre_code:
            query += " AND g.genre_code = ?"
            params.append(genre_code)
            
        query += " ORDER BY t.difficulty_level, t.template_name"
        
        results = self.execute_query(query, tuple(params) if params else None)
        
        # Parse JSON fields
        for result in results:
            for json_field in ['structure', 'instruments']:
                if result.get(json_field):
                    try:
                        result[json_field] = json.loads(result[json_field])
                    except:
                        result[json_field] = []
        
        return results
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.is_connected = False

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> DatabaseManager:
    """Get database manager instance"""
    return db_manager

def init_database() -> bool:
    """Initialize database connection"""
    return db_manager.connect()
