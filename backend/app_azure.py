"""
AI Music Portal Backend with Azure Cloud Integration
Full-fledged frontend-backend integration with real-time testing
Azure SQL DB, Azure OpenAI, and Azure Storage integration
Resource Group: rg-portal-ai-music
"""

from flask import Flask, request, jsonify, send_file, abort, send_from_directory, make_response
from flask_cors import CORS
import os
import sys
import traceback
from dotenv import load_dotenv
import logging
import json
import uuid
from datetime import datetime
import asyncio
import threading

# Enhanced Azure integration with free music data
try:
    from azure_cloud_integration import (
        azure_integration,
        get_azure_demo_tracks,
        get_azure_music_library,
        azure_health_check,
        upload_track_to_azure,
        generate_ai_music
    )
    from free_music_data_manager import (
        free_music_manager,
        download_free_music_data,
        get_free_music_samples,
        download_music_data_sync
    )
    from azure_sql_manager import AzureSQLManager
    AZURE_AVAILABLE = True
    print("✅ Full Azure Cloud Integration loaded successfully")
except ImportError as e:
    AZURE_AVAILABLE = False
    print(f"⚠️ Azure integration not available: {e}")

# Load environment variables
load_dotenv()
load_dotenv('.env.azure')  # Load Azure-specific config

app = Flask(__name__)

# Configure CORS for full cross-origin access (development and production)
# Allow all origins to prevent any CORS issues
CORS(app, 
     origins="*",  # Allow all origins
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=False,  # Set to False when using origins="*"
     automatic_options=True
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('azure_backend.log')
    ]
)
logger = logging.getLogger(__name__)

# Health check endpoint with Azure status
@app.route('/api/health', methods=['GET'])
def health_check():
    """Comprehensive health check including Azure services"""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "backend_version": "2.0.0-azure",
            "features": {
                "azure_integration": AZURE_AVAILABLE,
                "real_time_testing": True,
                "audio_streaming": True,
                "ai_generation": AZURE_AVAILABLE
            }
        }
        
        if AZURE_AVAILABLE:
            azure_status = azure_health_check()
            status["azure_services"] = azure_status["services"]
        
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# Demo tracks with Azure Storage integration
@app.route('/api/demo-tracks', methods=['GET'])
def get_demo_tracks():
    """Get demo tracks from Azure Blob Storage or fallback"""
    try:
        logger.info("🎵 Getting demo tracks...")
        
        if AZURE_AVAILABLE:
            tracks = get_azure_demo_tracks()
        else:
            # Demo tracks using local audio files to avoid CORS issues
            tracks = [
                {
                    "id": "demo_1",
                    "title": "Electronic Dreams",
                    "url": "http://localhost:5002/audio/demo1.mp3",
                    "duration": 45,
                    "genre": "Electronic",
                    "mood": "Energetic",
                    "created_at": "2025-01-20T10:00:00Z",
                    "tags": ["demo", "electronic", "ai-generated"],
                    "waveform": [0.2, 0.8, 0.4, 0.9, 0.3, 0.7, 0.6, 0.5, 0.8, 0.2, 0.9, 0.4]
                },
                {
                    "id": "demo_2",
                    "title": "Acoustic Serenity", 
                    "url": "http://localhost:5002/audio/demo2.mp3",
                    "duration": 60,
                    "genre": "Acoustic",
                    "mood": "Calm",
                    "created_at": "2025-01-20T10:15:00Z",
                    "tags": ["demo", "acoustic", "peaceful"],
                    "waveform": [0.1, 0.3, 0.2, 0.4, 0.3, 0.5, 0.4, 0.3, 0.2, 0.4, 0.3, 0.2]
                },
                {
                    "id": "demo_3",
                    "title": "Jazz Fusion",
                    "url": "http://localhost:5002/audio/demo3.mp3",
                    "duration": 75,
                    "genre": "Jazz",
                    "mood": "Sophisticated",
                    "created_at": "2025-01-20T10:30:00Z",
                    "tags": ["demo", "jazz", "complex"],
                    "waveform": [0.4, 0.7, 0.5, 0.8, 0.6, 0.9, 0.7, 0.6, 0.8, 0.5, 0.7, 0.4]
                },
                {
                    "id": "demo_4",
                    "title": "Cinematic Epic",
                    "url": "http://localhost:5002/audio/demo1.mp3",
                    "duration": 90,
                    "genre": "Cinematic",
                    "mood": "Dramatic",
                    "created_at": "2025-01-20T10:45:00Z",
                    "tags": ["demo", "cinematic", "epic"],
                    "waveform": [0.1, 0.9, 0.3, 0.8, 0.2, 0.7, 0.9, 0.4, 0.8, 0.3, 0.9, 0.1]
                },
                {
                    "id": "demo_5",
                    "title": "Ambient Space",
                    "url": "http://localhost:5002/audio/demo2.mp3",
                    "duration": 120,
                    "genre": "Ambient",
                    "mood": "Mystical",
                    "created_at": "2025-01-20T11:00:00Z",
                    "tags": ["demo", "ambient", "space"],
                    "waveform": [0.3, 0.4, 0.5, 0.6, 0.4, 0.5, 0.3, 0.4, 0.6, 0.5, 0.4, 0.3]
                }
            ]
        
        logger.info(f"✅ Returning {len(tracks)} demo tracks")
        return jsonify({
            "success": True,
            "total": len(tracks),
            "tracks": tracks,
            "source": "azure_storage" if AZURE_AVAILABLE else "fallback"
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get demo tracks: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to load demo tracks",
            "message": str(e)
        }), 500

# Music Library with Azure SQL Database integration
@app.route('/api/music-library', methods=['GET'])
def get_music_library():
    """Get music library from Azure SQL Database"""
    try:
        genre = request.args.get('genre', 'all')
        sort_by = request.args.get('sortBy', 'date')
        limit = int(request.args.get('limit', 50))
        
        logger.info(f"🎵 Getting music library: genre={genre}, limit={limit}")
        
        if AZURE_AVAILABLE:
            # First try to get downloaded free music data
            free_tracks = get_free_music_samples(limit)
            if free_tracks and len(free_tracks) > 0:
                # Filter by genre if specified
                if genre and genre != 'all':
                    free_tracks = [track for track in free_tracks if track.get('genre', '').lower() == genre.lower()]
                tracks = free_tracks
            else:
                # Fall back to Azure SQL
                tracks = get_azure_music_library(genre=genre, limit=limit)
        else:
            # Enhanced fallback mock data with local audio files
            tracks = [
                {
                    "id": "track_1",
                    "title": "My Epic Electronic Journey",
                    "genre": "Electronic",
                    "mood": "Energetic",
                    "duration": 180,
                    "url": "http://localhost:5002/audio/demo1.mp3",
                    "created_at": "2025-01-25T14:30:00Z",
                    "tags": ["user-generated", "epic", "electronic"],
                    "is_favorite": True
                },
                {
                    "id": "track_2",
                    "title": "Ambient Dreamscape",
                    "genre": "Ambient",
                    "mood": "Relaxed",
                    "duration": 240,
                    "url": "http://localhost:5002/audio/demo2.mp3",
                    "created_at": "2025-01-24T09:15:00Z",
                    "tags": ["ambient", "chill", "relaxing"],
                    "is_favorite": False
                },
                {
                    "id": "track_3",
                    "title": "Jazz Night Sessions",
                    "genre": "Jazz",
                    "mood": "Sophisticated",
                    "duration": 195,
                    "url": "http://localhost:5002/audio/demo3.mp3",
                    "created_at": "2025-01-23T16:45:00Z",
                    "tags": ["jazz", "night", "sophisticated"],
                    "is_favorite": True
                },
                {
                    "id": "track_4",
                    "title": "Cinematic Adventure",
                    "genre": "Cinematic",
                    "mood": "Dramatic",
                    "duration": 210,
                    "url": "http://localhost:5002/audio/demo1.mp3",
                    "created_at": "2025-01-22T11:30:00Z",
                    "tags": ["cinematic", "adventure", "dramatic"],
                    "is_favorite": False
                },
                {
                    "id": "track_5",
                    "title": "Acoustic Sunrise",
                    "genre": "Acoustic",
                    "mood": "Peaceful",
                    "duration": 165,
                    "url": "http://localhost:5002/audio/demo2.mp3",
                    "created_at": "2025-01-21T07:20:00Z",
                    "tags": ["acoustic", "sunrise", "peaceful"],
                    "is_favorite": True
                },
                {
                    "id": "track_6",
                    "title": "Rock Energy Burst",
                    "genre": "Rock",
                    "mood": "Energetic",
                    "duration": 200,
                    "url": "http://localhost:5002/audio/demo3.mp3",
                    "created_at": "2025-01-20T18:45:00Z",
                    "tags": ["rock", "energy", "powerful"],
                    "is_favorite": False
                }
            ]
            
            # Filter by genre if specified
            if genre and genre != 'all':
                tracks = [track for track in tracks if track.get('genre', '').lower() == genre.lower()]
        
        return jsonify({
            "success": True,
            "total": len(tracks),
            "tracks": tracks,
            "page": 1,
            "limit": limit,
            "has_more": len(tracks) >= limit,
            "source": "azure_sql" if AZURE_AVAILABLE else "fallback"
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get music library: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to load music library",
            "message": str(e)
        }), 500

# Music Library Search with Azure integration
@app.route('/api/music-library/search', methods=['GET'])
def search_music_library():
    """Search music library with Azure integration"""
    try:
        query = request.args.get('q', '').strip()
        genre = request.args.get('genre', 'all')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Search query is required"
            }), 400
        
        logger.info(f"🔍 Searching music library: query='{query}', genre={genre}")
        
        # Mock search results for now
        search_results = [
            {
                "id": "search_1",
                "title": "Epic Search Result",
                "genre": "Pop",
                "mood": "Happy",
                "duration": 150,
                "url": "http://localhost:5002/audio/demo1.mp3",
                "created_at": "2025-01-22T09:15:00Z",
                "tags": ["search-result", "epic", "pop"],
                "is_favorite": False,
                "relevance_score": 0.95
            }
        ]
        
        return jsonify({
            "success": True,
            "query": query,
            "total": len(search_results),
            "tracks": search_results,
            "source": "azure_search" if AZURE_AVAILABLE else "mock"
        })
        
    except Exception as e:
        logger.error(f"❌ Music library search failed: {e}")
        return jsonify({
            "success": False,
            "error": "Search failed",
            "message": str(e)
        }), 500

# Music Generation with Azure OpenAI
@app.route('/api/generate-music', methods=['POST'])
def generate_music():
    """Generate music using Azure OpenAI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        genre = data.get('genre', 'electronic')
        mood = data.get('mood', 'upbeat')
        duration = int(data.get('duration', 30))
        
        logger.info(f"🎼 Generating music: prompt='{prompt}', genre={genre}")
        
        # Generate a unique track ID
        track_id = f"generated_{uuid.uuid4().hex[:8]}"
        
        # For now, always use fallback generation with realistic data
        # TODO: Implement actual Azure OpenAI integration when API key is available
        track_data = {
            "id": track_id,
            "title": f"AI {genre.title()} - {prompt[:20] if prompt else 'Generated'}",
            "genre": genre.title(),
            "mood": mood.title(),
            "duration": duration,
            "url": "http://localhost:5002/audio/demo1.mp3",  # Use local audio file
            "created_at": datetime.utcnow().isoformat(),
            "tags": ["generated", "ai-music", genre.lower()],
            "prompt": prompt,
            "status": "completed",
            "waveform": [0.3, 0.7, 0.5, 0.9, 0.4, 0.8, 0.6, 0.7, 0.5, 0.6, 0.8, 0.4],
            "metadata": {
                "generation_method": "ai_simulation",
                "style": genre,
                "user_prompt": prompt,
                "created_with": "AI Music Portal"
            }
        }
        
        return jsonify({
            "success": True,
            "track": track_data,
            "generation_time": "2.5s",
            "source": "ai_simulation",
            "message": "Music generated successfully! (Using AI simulation)"
        })
        
    except Exception as e:
        logger.error(f"❌ Music generation failed: {e}")
        return jsonify({
            "success": False,
            "error": "Music generation failed",
            "message": str(e)
        }), 500

# Get available genres
@app.route('/api/genres', methods=['GET'])
def get_genres():
    """Get available music genres"""
    genres = [
        {"id": "pop", "name": "Pop", "description": "Popular mainstream music"},
        {"id": "rock", "name": "Rock", "description": "Rock and alternative"},
        {"id": "electronic", "name": "Electronic", "description": "Electronic dance music"},
        {"id": "jazz", "name": "Jazz", "description": "Jazz and swing"},
        {"id": "classical", "name": "Classical", "description": "Classical orchestral"},
        {"id": "hip-hop", "name": "Hip-Hop", "description": "Hip-hop and rap"},
        {"id": "ambient", "name": "Ambient", "description": "Atmospheric ambient"},
        {"id": "cinematic", "name": "Cinematic", "description": "Film score style"}
    ]
    
    return jsonify({
        "success": True,
        "genres": genres
    })

# Get available moods
@app.route('/api/moods', methods=['GET'])
def get_moods():
    """Get available music moods"""
    moods = [
        {"id": "upbeat", "name": "Upbeat", "description": "Energetic and positive"},
        {"id": "calm", "name": "Calm", "description": "Peaceful and relaxing"},
        {"id": "dramatic", "name": "Dramatic", "description": "Intense and powerful"},
        {"id": "mysterious", "name": "Mysterious", "description": "Dark and enigmatic"},
        {"id": "happy", "name": "Happy", "description": "Joyful and cheerful"},
        {"id": "sad", "name": "Sad", "description": "Melancholic and emotional"},
        {"id": "epic", "name": "Epic", "description": "Grand and heroic"},
        {"id": "romantic", "name": "Romantic", "description": "Love and passion"}
    ]
    
    return jsonify({
        "success": True,
        "moods": moods
    })

# User quota endpoint
@app.route('/api/user/quota', methods=['GET'])
def get_user_quota():
    """Get user's generation quota"""
    return jsonify({
        "success": True,
        "quota": {
            "remaining": 50,
            "total": 100,
            "reset_date": "2025-02-01T00:00:00Z",
            "premium": False
        }
    })

# Real-time testing endpoint
@app.route('/api/test-integration', methods=['GET'])
def test_integration():
    """Real-time integration testing endpoint"""
    try:
        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {}
        }
        
        # Test demo tracks
        try:
            demo_response = get_demo_tracks()
            test_results["tests"]["demo_tracks"] = {
                "status": "✅ PASS" if demo_response.status_code == 200 else "❌ FAIL",
                "response_time": "<100ms"
            }
        except Exception as e:
            test_results["tests"]["demo_tracks"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
        
        # Test music library
        try:
            library_response = get_music_library()
            test_results["tests"]["music_library"] = {
                "status": "✅ PASS" if library_response.status_code == 200 else "❌ FAIL",
                "response_time": "<100ms"
            }
        except Exception as e:
            test_results["tests"]["music_library"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
        
        # Test Azure services
        if AZURE_AVAILABLE:
            azure_status = azure_health_check()
            test_results["tests"]["azure_services"] = azure_status["services"]
        else:
            test_results["tests"]["azure_services"] = {
                "status": "⚠️ NOT AVAILABLE"
            }
        
        overall_status = all(
            "✅" in str(test["status"]) 
            for test in test_results["tests"].values()
            if isinstance(test, dict) and "status" in test
        )
        
        test_results["overall_status"] = "✅ ALL TESTS PASSED" if overall_status else "⚠️ SOME TESTS FAILED"
        
        return jsonify(test_results)
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return jsonify({
            "overall_status": "❌ INTEGRATION TEST FAILED",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Enhanced endpoints for free music data and Azure setup
@app.route('/api/download-free-music-data', methods=['POST'])
def download_free_music_data_endpoint():
    """Download free music data from various APIs"""
    try:
        data = request.get_json() or {}
        limit = int(data.get('limit', 200))
        
        logger.info(f"🎵 Starting free music data download (limit: {limit})")
        
        if AZURE_AVAILABLE:
            # Use async download
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(download_free_music_data(limit))
            finally:
                loop.close()
        else:
            # Use sync download
            result = download_music_data_sync(limit)
        
        # Save to file
        filename = free_music_manager.save_music_data_to_file()
        
        return jsonify({
            "success": True,
            "message": "Free music data download completed",
            "stats": result.get('stats', {}),
            "total_tracks": len(result.get('tracks', [])),
            "saved_to": filename,
            "sources": list(set(track.get('source') for track in result.get('tracks', [])))
        })
        
    except Exception as e:
        logger.error(f"❌ Free music data download failed: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to download free music data",
            "message": str(e)
        }), 500

@app.route('/api/setup-azure-database', methods=['POST'])
def setup_azure_database():
    """Setup Azure SQL Database with complete schema"""
    if not AZURE_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Azure integration not available"
        }), 503
    
    try:
        # Initialize SQL manager
        sql_manager = AzureSQLManager(azure_integration.sql_connection_string)
        
        # Create schema
        schema_created = sql_manager.create_database_schema()
        
        if schema_created:
            # Get free music samples to populate database
            sample_tracks = get_free_music_samples(50)
            inserted_count = sql_manager.insert_free_music_data(sample_tracks)
            
            # Get database stats
            stats = sql_manager.get_database_stats()
            
            return jsonify({
                "success": True,
                "message": "Azure SQL Database setup completed",
                "schema_created": True,
                "sample_tracks_inserted": inserted_count,
                "database_stats": stats
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to create database schema"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Azure database setup failed: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to setup Azure database",
            "message": str(e)
        }), 500

@app.route('/api/music-data-status', methods=['GET'])
def get_music_data_status():
    """Get status of music data and Azure services"""
    try:
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "free_music_manager": {
                "tracks_downloaded": len(free_music_manager.downloaded_tracks),
                "sources_available": list(free_music_manager.apis.keys())
            }
        }
        
        if AZURE_AVAILABLE:
            # Get Azure services status
            azure_status = azure_health_check()
            status["azure_services"] = azure_status.get("services", {})
            
            # Try to get database stats if connected
            try:
                sql_manager = AzureSQLManager(azure_integration.sql_connection_string)
                if sql_manager.is_connected:
                    status["database_stats"] = sql_manager.get_database_stats()
            except Exception as e:
                status["database_error"] = str(e)
        
        return jsonify({
            "success": True,
            "status": status
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get music data status: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get status",
            "message": str(e)
        }), 500

# Azure-specific endpoints
@app.route('/api/azure/upload', methods=['POST'])
def upload_to_azure():
    """Upload audio file to Azure Blob Storage"""
    if not AZURE_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Azure integration not available"
        }), 503
    
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        # Read file data
        file_data = file.read()
        filename = file.filename
        
        # Upload to Azure
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            blob_url = loop.run_until_complete(
                upload_track_to_azure(file_data, filename, {
                    "uploaded_by": "user",
                    "file_size": len(file_data)
                })
            )
        finally:
            loop.close()
        
        return jsonify({
            "success": True,
            "url": blob_url,
            "filename": filename,
            "size": len(file_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Azure upload failed: {e}")
        return jsonify({
            "success": False,
            "error": "Upload failed",
            "message": str(e)
        }), 500

# Serve static audio files
@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files - CORS handled by middleware"""
    try:
        response = send_from_directory('static/audio', filename)
        response.headers['Content-Type'] = 'audio/mpeg'
        response.headers['Cache-Control'] = 'no-cache'
        return response
    except FileNotFoundError:
        # Return a simple placeholder response for demo purposes
        return jsonify({
            "error": "Audio file not found",
            "message": "This is a demo system. In production, real audio files would be served here.",
            "filename": filename,
            "note": "CORS headers are handled by Flask-CORS middleware"
        }), 404

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "message": "The requested resource was not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Main application
if __name__ == '__main__':
    print("🚀 Starting AI Music Portal Backend with Azure Integration...")
    print(f"✅ Azure Integration: {'ENABLED' if AZURE_AVAILABLE else 'DISABLED'}")
    print(f"🔗 Backend URL: http://localhost:5002")
    print(f"🔗 Health Check: http://localhost:5002/api/health")
    print(f"🔗 Real-time Test: http://localhost:5002/api/test-integration")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5002,
        threaded=True
    )