import azure.functions as func
import json
import logging
import os
import pyodbc
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Music library endpoint triggered.')
    
    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
    
    try:
        if req.method == 'GET':
            # Get user's music library
            user_id = req.params.get('user_id', 'demo_user')
            page = int(req.params.get('page', 1))
            limit = int(req.params.get('limit', 20))
            genre_filter = req.params.get('genre')
            mood_filter = req.params.get('mood')
            
            tracks = get_user_tracks(user_id, page, limit, genre_filter, mood_filter)
            
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "tracks": tracks,
                    "page": page,
                    "limit": limit,
                    "total": len(tracks)
                }),
                status_code=200,
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            
        elif req.method == 'POST':
            # Save track to library
            request_json = req.get_json()
            if not request_json:
                return func.HttpResponse(
                    json.dumps({"success": False, "error": "No JSON data provided"}),
                    status_code=400,
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                )
            
            track_id = request_json.get('track_id')
            user_id = request_json.get('user_id', 'demo_user')
            
            if not track_id:
                return func.HttpResponse(
                    json.dumps({"success": False, "error": "Track ID is required"}),
                    status_code=400,
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                )
            
            result = save_track_to_library(user_id, track_id)
            
            return func.HttpResponse(
                json.dumps(result),
                status_code=200 if result['success'] else 400,
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            
        elif req.method == 'DELETE':
            # Remove track from library
            track_id = req.params.get('track_id')
            user_id = req.params.get('user_id', 'demo_user')
            
            if not track_id:
                return func.HttpResponse(
                    json.dumps({"success": False, "error": "Track ID is required"}),
                    status_code=400,
                    headers={
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    }
                )
            
            result = remove_track_from_library(user_id, track_id)
            
            return func.HttpResponse(
                json.dumps(result),
                status_code=200 if result['success'] else 400,
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        
    except Exception as e:
        logging.error(f"Music library error: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False, 
                "error": f"Music library operation failed: {str(e)}"
            }),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )

def get_user_tracks(user_id, page=1, limit=20, genre_filter=None, mood_filter=None):
    """Get user's tracks from database"""
    try:
        connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")
        if not connection_string:
            # Return mock data if database not configured
            return get_mock_tracks(page, limit, genre_filter, mood_filter)
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
        SELECT t.track_id, t.title, t.duration, t.genre, t.mood, t.tempo,
               t.key_signature, t.instruments, t.vocals, t.structure,
               t.lyrics_style, t.custom_tags, t.lyrics, t.prompt,
               t.created_at, t.status, t.progress, ul.saved_at
        FROM tracks t
        INNER JOIN user_library ul ON t.track_id = ul.track_id
        WHERE ul.user_id = ?
        """
        
        params = [user_id]
        
        if genre_filter:
            query += " AND t.genre = ?"
            params.append(genre_filter)
        
        if mood_filter:
            query += " AND t.mood = ?"
            params.append(mood_filter)
        
        query += " ORDER BY ul.saved_at DESC"
        query += f" OFFSET {(page - 1) * limit} ROWS FETCH NEXT {limit} ROWS ONLY"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        tracks = []
        for row in rows:
            track = {
                "id": row[0],
                "title": row[1],
                "duration": row[2],
                "genre": row[3],
                "mood": row[4],
                "tempo": row[5],
                "key": row[6],
                "instruments": json.loads(row[7]) if row[7] else [],
                "vocals": row[8],
                "structure": row[9],
                "lyrics_style": row[10],
                "custom_tags": json.loads(row[11]) if row[11] else [],
                "lyrics": row[12],
                "prompt": row[13],
                "created_at": row[14],
                "status": row[15],
                "progress": row[16],
                "saved_at": row[17],
                "url": f"https://portalaimusicdev.blob.core.windows.net/audio/{row[0]}.mp3",
                "download_url": f"https://portalaimusicdev.blob.core.windows.net/audio/{row[0]}.wav"
            }
            tracks.append(track)
        
        conn.close()
        return tracks
        
    except Exception as e:
        logging.error(f"Database query error: {str(e)}")
        return get_mock_tracks(page, limit, genre_filter, mood_filter)

def get_mock_tracks(page=1, limit=20, genre_filter=None, mood_filter=None):
    """Return mock track data for testing"""
    mock_tracks = [
        {
            "id": "track_20250125_001",
            "title": "Epic Journey",
            "duration": 180,
            "genre": "orchestral",
            "mood": "epic",
            "tempo": 120,
            "key": "C",
            "instruments": ["orchestra", "choir"],
            "vocals": True,
            "structure": "intro-verse-chorus-bridge-chorus-outro",
            "lyrics_style": "narrative",
            "custom_tags": ["cinematic", "adventure"],
            "lyrics": "Verse 1: The journey begins...\nChorus: We rise above...",
            "prompt": "Create an epic orchestral piece about a heroic journey",
            "created_at": "2025-01-25T10:30:00Z",
            "status": "completed",
            "progress": 100,
            "saved_at": "2025-01-25T10:35:00Z",
            "url": "https://portalaimusicdev.blob.core.windows.net/audio/track_20250125_001.mp3",
            "download_url": "https://portalaimusicdev.blob.core.windows.net/audio/track_20250125_001.wav"
        },
        {
            "id": "track_20250125_002",
            "title": "Midnight Jazz",
            "duration": 240,
            "genre": "jazz",
            "mood": "smooth",
            "tempo": 100,
            "key": "Bb",
            "instruments": ["piano", "saxophone", "bass", "drums"],
            "vocals": False,
            "structure": "intro-theme-improvisation-theme-outro",
            "lyrics_style": None,
            "custom_tags": ["smooth", "midnight", "instrumental"],
            "lyrics": None,
            "prompt": "Create a smooth jazz piece for late night listening",
            "created_at": "2025-01-25T09:15:00Z",
            "status": "completed",
            "progress": 100,
            "saved_at": "2025-01-25T09:20:00Z",
            "url": "https://portalaimusicdev.blob.core.windows.net/audio/track_20250125_002.mp3",
            "download_url": "https://portalaimusicdev.blob.core.windows.net/audio/track_20250125_002.wav"
        }
    ]
    
    # Apply filters
    filtered_tracks = mock_tracks
    if genre_filter:
        filtered_tracks = [t for t in filtered_tracks if t['genre'] == genre_filter]
    if mood_filter:
        filtered_tracks = [t for t in filtered_tracks if t['mood'] == mood_filter]
    
    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    return filtered_tracks[start_idx:end_idx]

def save_track_to_library(user_id, track_id):
    """Save track to user's library"""
    try:
        connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")
        if not connection_string:
            return {"success": True, "message": "Track saved to library (mock)"}
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if already saved
        check_query = "SELECT COUNT(*) FROM user_library WHERE user_id = ? AND track_id = ?"
        cursor.execute(check_query, (user_id, track_id))
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            return {"success": False, "error": "Track already in library"}
        
        # Save to library
        insert_query = """
        INSERT INTO user_library (user_id, track_id, saved_at)
        VALUES (?, ?, ?)
        """
        cursor.execute(insert_query, (user_id, track_id, datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Track saved to library"}
        
    except Exception as e:
        logging.error(f"Save track error: {str(e)}")
        return {"success": False, "error": str(e)}

def remove_track_from_library(user_id, track_id):
    """Remove track from user's library"""
    try:
        connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")
        if not connection_string:
            return {"success": True, "message": "Track removed from library (mock)"}
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Remove from library
        delete_query = "DELETE FROM user_library WHERE user_id = ? AND track_id = ?"
        cursor.execute(delete_query, (user_id, track_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": "Track not found in library"}
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Track removed from library"}
        
    except Exception as e:
        logging.error(f"Remove track error: {str(e)}")
        return {"success": False, "error": str(e)}
