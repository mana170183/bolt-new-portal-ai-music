import azure.functions as func
import datetime
import json
import logging
import base64
import os
from typing import Optional, Dict, List, Any

app = func.FunctionApp()

# CORS headers for all responses
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

def create_response(data: Any, status_code: int = 200, additional_headers: Dict = None) -> func.HttpResponse:
    """Create a standardized HTTP response with CORS headers"""
    headers = {'Content-Type': 'application/json', **CORS_HEADERS}
    if additional_headers:
        headers.update(additional_headers)
    
    return func.HttpResponse(
        json.dumps(data, default=str),
        status_code=status_code,
        headers=headers
    )

def handle_options(req: func.HttpRequest) -> func.HttpResponse:
    """Handle OPTIONS requests for CORS preflight"""
    return func.HttpResponse("", status_code=200, headers=CORS_HEADERS)

# Health Check Endpoint
@app.route(route="health", methods=["GET", "OPTIONS"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Health check endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        response_data = {
            "status": "healthy",
            "message": "AI Music Backend API is running",
            "version": "1.0.0"
        }
        return create_response(response_data)
    except Exception as e:
        logging.error(f"Health check error: {str(e)}")
        return create_response({"status": "error", "message": str(e)}, 500)

# Status Endpoint - Architecture and component status
@app.route(route="status", methods=["GET", "OPTIONS"])
def status(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Status endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        # Mock status check for demo
        status_data = {
            "system": {
                "status": "operational",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "version": "1.0.0"
            },
            "components": {
                "azure_openai": {
                    "status": "healthy",
                    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "demo_endpoint"),
                    "model": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
                },
                "azure_sql": {
                    "status": "healthy",
                    "connection": "demo_connection_ok"
                },
                "azure_storage": {
                    "status": "healthy", 
                    "container": os.getenv("AZURE_STORAGE_CONTAINER_NAME", "music-files")
                },
                "external_apis": {
                    "spotify": {"status": "configured"},
                    "musicbrainz": {"status": "available"},
                    "freesound": {"status": "configured"},
                    "jamendo": {"status": "configured"}
                }
            },
            "architecture": {
                "backend": "Azure Functions (Python)",
                "database": "Azure SQL Database",
                "storage": "Azure Blob Storage",
                "ai": "Azure OpenAI",
                "frontend": "React + Vite"
            }
        }
        return create_response(status_data)
    except Exception as e:
        logging.error(f"Status check error: {str(e)}")
        return create_response({"status": "error", "message": str(e)}, 500)

# Generate Music Endpoint
@app.route(route="generate-music", methods=["POST", "OPTIONS"])
def generate_music(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Generate music endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        req_body = req.get_json()
        
        # Extract parameters
        prompt = req_body.get('prompt', '')
        duration = req_body.get('duration', 30)
        genre = req_body.get('genre', 'electronic')
        mood = req_body.get('mood', 'energetic')
        user_id = req_body.get('user_id', 'demo_user')
        
        # Mock music generation response
        generated_music = {
            "id": f"generated_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": f"AI Generated - {prompt[:30]}..." if len(prompt) > 30 else f"AI Generated - {prompt}",
            "prompt": prompt,
            "duration": duration,
            "genre": genre,
            "mood": mood,
            "user_id": user_id,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "file_url": f"https://demo-storage.blob.core.windows.net/music-files/generated_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "metadata": {
                "tempo": "120 BPM",
                "key": "C Major",
                "instruments": ["synthesizer", "drums", "bass"],
                "ai_model": "Azure OpenAI GPT-4",
                "generation_time": "15.2s"
            },
            "status": "completed"
        }
        
        return create_response(generated_music)
    except Exception as e:
        logging.error(f"Music generation error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Advanced Generate Music Endpoint
@app.route(route="advanced-generate", methods=["POST", "OPTIONS"])
def advanced_generate(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Advanced generate endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        req_body = req.get_json()
        
        # Enhanced parameters for advanced generation
        prompt = req_body.get('prompt', '')
        duration = req_body.get('duration', 60)
        genre = req_body.get('genre', 'electronic')
        mood = req_body.get('mood', 'energetic')
        tempo = req_body.get('tempo', 120)
        key = req_body.get('key', 'C Major')
        instruments = req_body.get('instruments', [])
        user_id = req_body.get('user_id', 'demo_user')
        advanced_options = req_body.get('advanced_options', {})
        
        # Mock advanced generation
        generated_music = {
            "id": f"advanced_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": f"Advanced AI - {prompt[:30]}..." if len(prompt) > 30 else f"Advanced AI - {prompt}",
            "prompt": prompt,
            "duration": duration,
            "genre": genre,
            "mood": mood,
            "tempo": tempo,
            "key": key,
            "instruments": instruments,
            "user_id": user_id,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "file_url": f"https://demo-storage.blob.core.windows.net/music-files/advanced_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
            "metadata": {
                "advanced_options": advanced_options,
                "ai_model": "Azure OpenAI GPT-4",
                "generation_time": "25.7s",
                "quality": "high",
                "sample_rate": "44.1kHz",
                "bit_depth": "24-bit"
            },
            "status": "completed"
        }
        
        return create_response(generated_music)
    except Exception as e:
        logging.error(f"Advanced generation error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Music Library Endpoint
@app.route(route="music-library", methods=["GET", "POST", "DELETE", "OPTIONS"])
def music_library(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Music library endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        user_id = req.params.get('user_id', 'demo_user')
        
        if req.method == "GET":
            # Mock user library
            library = {
                "user_id": user_id,
                "tracks": [
                    {
                        "id": "track_001",
                        "title": "My First AI Song",
                        "genre": "electronic",
                        "mood": "energetic",
                        "duration": 180,
                        "created_at": "2024-01-15T10:30:00Z",
                        "file_url": "https://demo-storage.blob.core.windows.net/music-files/track_001.mp3"
                    },
                    {
                        "id": "track_002", 
                        "title": "Ambient Dreamscape",
                        "genre": "ambient",
                        "mood": "relaxed",
                        "duration": 240,
                        "created_at": "2024-01-14T15:45:00Z",
                        "file_url": "https://demo-storage.blob.core.windows.net/music-files/track_002.mp3"
                    }
                ],
                "total_tracks": 2,
                "total_duration": 420
            }
            return create_response(library)
            
        elif req.method == "POST":
            req_body = req.get_json()
            track_data = {
                "id": f"track_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "user_id": user_id,
                "title": req_body.get('title', 'Untitled Track'),
                "genre": req_body.get('genre', 'unknown'),
                "mood": req_body.get('mood', 'neutral'),
                "duration": req_body.get('duration', 0),
                "created_at": datetime.datetime.utcnow().isoformat(),
                "status": "saved"
            }
            return create_response(track_data, 201)
            
        elif req.method == "DELETE":
            track_id = req.params.get('track_id')
            if not track_id:
                return create_response({"error": "track_id parameter required"}, 400)
            
            return create_response({"message": f"Track {track_id} deleted successfully"})
            
    except Exception as e:
        logging.error(f"Music library error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Root API Info Endpoint
@app.route(route="root", methods=["GET", "OPTIONS"])
def root(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Root endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    api_info = {
        "name": "AI Music Platform API",
        "version": "1.0.0",
        "description": "Azure Functions backend for AI music generation and management",
        "endpoints": {
            "/api/health": "Health check",
            "/api/status": "System status and architecture",
            "/api/generate-music": "Generate music with AI",
            "/api/advanced-generate": "Advanced music generation",
            "/api/music-library": "User music library management",
            "/api/music-catalog": "Music catalog with search",
            "/api/upload": "File upload to Azure Storage",
            "/api/music-apis": "External music API integration",
            "/api/user-profile": "User profile management",
            "/api/playlists": "Playlist management",
            "/api/auth-token": "Authentication token generation",
            "/api/user-quota": "User quota management",
            "/api/genres": "Available genres",
            "/api/moods": "Available moods"
        },
        "architecture": {
            "backend": "Azure Functions (Python)",
            "database": "Azure SQL Database", 
            "storage": "Azure Blob Storage",
            "ai": "Azure OpenAI",
            "frontend": "React + Vite"
        }
    }
    return create_response(api_info)

# Music Catalog Endpoint
@app.route(route="music-catalog", methods=["GET", "POST", "OPTIONS"])
def music_catalog(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Music catalog endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        if req.method == "GET":
            page = int(req.params.get('page', 1))
            limit = int(req.params.get('limit', 20))
            search = req.params.get('search', '')
            genre = req.params.get('genre', '')
            source = req.params.get('source', '')
            
            # Mock catalog data
            tracks = [
                {
                    "id": "catalog_001",
                    "title": "Electronic Symphony",
                    "artist": "AI Composer",
                    "genre": "electronic",
                    "mood": "energetic",
                    "duration": 195,
                    "source": "azure_openai",
                    "created_at": "2024-01-15T10:00:00Z",
                    "file_url": "https://demo-storage.blob.core.windows.net/catalog/electronic_symphony.mp3",
                    "popularity": 85
                },
                {
                    "id": "catalog_002",
                    "title": "Ambient Journey",
                    "artist": "Neural Networks",
                    "genre": "ambient",
                    "mood": "relaxed", 
                    "duration": 320,
                    "source": "azure_openai",
                    "created_at": "2024-01-14T16:30:00Z",
                    "file_url": "https://demo-storage.blob.core.windows.net/catalog/ambient_journey.mp3",
                    "popularity": 92
                }
            ]
            
            # Apply filters
            if search:
                tracks = [t for t in tracks if search.lower() in t['title'].lower() or search.lower() in t['artist'].lower()]
            if genre:
                tracks = [t for t in tracks if t['genre'] == genre]
            if source:
                tracks = [t for t in tracks if t['source'] == source]
            
            # Pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_tracks = tracks[start:end]
            
            catalog_response = {
                "tracks": paginated_tracks,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(tracks),
                    "pages": (len(tracks) + limit - 1) // limit
                },
                "filters": {
                    "search": search,
                    "genre": genre,
                    "source": source
                }
            }
            return create_response(catalog_response)
            
        elif req.method == "POST":
            req_body = req.get_json()
            new_track = {
                "id": f"catalog_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": req_body.get('title', 'Untitled'),
                "artist": req_body.get('artist', 'Unknown Artist'),
                "genre": req_body.get('genre', 'unknown'),
                "mood": req_body.get('mood', 'neutral'),
                "duration": req_body.get('duration', 0),
                "source": req_body.get('source', 'user_upload'),
                "created_at": datetime.datetime.utcnow().isoformat(),
                "popularity": 0
            }
            return create_response(new_track, 201)
            
    except Exception as e:
        logging.error(f"Music catalog error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Upload Endpoint
@app.route(route="upload", methods=["POST", "OPTIONS"])
def upload(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Upload endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        req_body = req.get_json()
        
        file_data = req_body.get('file_data', '')
        filename = req_body.get('filename', f'upload_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.mp3')
        content_type = req_body.get('content_type', 'audio/mpeg')
        user_id = req_body.get('user_id', 'demo_user')
        
        if not file_data:
            return create_response({"error": "file_data is required"}, 400)
        
        # Mock file upload to Azure Blob Storage
        upload_result = {
            "id": f"upload_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "filename": filename,
            "user_id": user_id,
            "content_type": content_type,
            "size": len(file_data),
            "url": f"https://demo-storage.blob.core.windows.net/music-files/{filename}",
            "uploaded_at": datetime.datetime.utcnow().isoformat(),
            "status": "uploaded"
        }
        
        return create_response(upload_result, 201)
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Music APIs Endpoint - List services
@app.route(route="music-apis", methods=["GET", "OPTIONS"])
def music_apis_list(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Music APIs list endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        # Return available services
        services = {
            "available_services": ["spotify", "musicbrainz", "freesound", "jamendo"],
            "endpoints": {
                "spotify": "/api/music-apis/spotify?query=search_term",
                "musicbrainz": "/api/music-apis/musicbrainz?query=search_term",
                "freesound": "/api/music-apis/freesound?query=search_term",
                "jamendo": "/api/music-apis/jamendo?query=search_term"
            }
        }
        return create_response(services)
    except Exception as e:
        logging.error(f"Music APIs error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Music APIs Endpoint - Specific service
@app.route(route="music-apis/{service}", methods=["GET", "OPTIONS"])
def music_apis_service(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Music APIs service endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        service = req.route_params.get('service', '')
        query = req.params.get('query', '')
        
        # Mock responses for different services
        if service == "spotify":
            mock_data = {
                "service": "spotify",
                "query": query,
                "results": [
                    {
                        "id": "spotify_track_1",
                        "title": f"Spotify Result for '{query}'",
                        "artist": "Demo Artist",
                        "album": "Demo Album",
                        "duration": 210,
                        "external_url": "https://open.spotify.com/track/demo"
                    }
                ]
            }
        elif service == "musicbrainz":
            mock_data = {
                "service": "musicbrainz",
                "query": query,
                "results": [
                    {
                        "id": "mb_track_1",
                        "title": f"MusicBrainz Result for '{query}'",
                        "artist": "Demo Artist",
                        "album": "Demo Album",
                        "release_date": "2024-01-01"
                    }
                ]
            }
        elif service == "freesound":
            mock_data = {
                "service": "freesound",
                "query": query,
                "results": [
                    {
                        "id": "fs_sound_1",
                        "title": f"Freesound Result for '{query}'",
                        "duration": 15.5,
                        "license": "CC BY 4.0",
                        "download_url": "https://freesound.org/demo"
                    }
                ]
            }
        elif service == "jamendo":
            mock_data = {
                "service": "jamendo",
                "query": query,
                "results": [
                    {
                        "id": "jamendo_track_1",
                        "title": f"Jamendo Result for '{query}'",
                        "artist": "Demo Artist",
                        "duration": 185,
                        "license": "CC BY-SA",
                        "stream_url": "https://jamendo.com/demo"
                    }
                ]
            }
        else:
            return create_response({"error": f"Service '{service}' not supported"}, 400)
        
        return create_response(mock_data)
    except Exception as e:
        logging.error(f"Music APIs error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# User Profile Endpoint
@app.route(route="user-profile", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def user_profile(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('User profile endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        user_id = req.params.get('user_id', 'demo_user')
        
        if req.method == "GET":
            include_stats = req.params.get('include_stats', 'false').lower() == 'true'
            
            profile = {
                "user_id": user_id,
                "username": f"user_{user_id}",
                "email": f"{user_id}@example.com",
                "plan": "free",
                "preferences": {
                    "favorite_genres": ["electronic", "ambient"],
                    "default_duration": 60,
                    "ai_model_preference": "gpt-4"
                },
                "created_at": "2024-01-01T00:00:00Z",
                "last_login": datetime.datetime.utcnow().isoformat()
            }
            
            if include_stats:
                profile["statistics"] = {
                    "total_tracks_generated": 15,
                    "total_playlists": 3,
                    "total_listening_time": 1800,
                    "favorite_genre": "electronic",
                    "generation_streak": 7
                }
            
            return create_response(profile)
            
        elif req.method == "POST":
            req_body = req.get_json()
            new_profile = {
                "user_id": user_id,
                "username": req_body.get('username', f"user_{user_id}"),
                "email": req_body.get('email', f"{user_id}@example.com"),
                "plan": req_body.get('plan', 'free'),
                "preferences": req_body.get('preferences', {}),
                "created_at": datetime.datetime.utcnow().isoformat(),
                "status": "created"
            }
            return create_response(new_profile, 201)
            
        elif req.method == "PUT":
            req_body = req.get_json()
            updated_profile = {
                "user_id": user_id,
                "updated_fields": list(req_body.keys()),
                "updated_at": datetime.datetime.utcnow().isoformat(),
                "status": "updated"
            }
            return create_response(updated_profile)
            
        elif req.method == "DELETE":
            return create_response({
                "user_id": user_id,
                "status": "deleted",
                "deleted_at": datetime.datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        logging.error(f"User profile error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Playlists Endpoint
@app.route(route="playlists", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def playlists(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Playlists endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        user_id = req.params.get('user_id', 'demo_user')
        playlist_id = req.params.get('playlist_id')
        
        if req.method == "GET":
            if playlist_id:
                # Get specific playlist
                playlist = {
                    "id": playlist_id,
                    "user_id": user_id,
                    "name": "My Favorite AI Tracks",
                    "description": "A collection of my best AI-generated music",
                    "tracks": [
                        {
                            "id": "track_001",
                            "title": "Electronic Dreams",
                            "duration": 180,
                            "added_at": "2024-01-15T10:00:00Z"
                        },
                        {
                            "id": "track_002",
                            "title": "Ambient Voyage",
                            "duration": 240,
                            "added_at": "2024-01-14T15:30:00Z"
                        }
                    ],
                    "created_at": "2024-01-10T12:00:00Z",
                    "updated_at": "2024-01-15T10:00:00Z",
                    "track_count": 2,
                    "total_duration": 420
                }
                return create_response(playlist)
            else:
                # Get user playlists
                playlists_data = {
                    "user_id": user_id,
                    "playlists": [
                        {
                            "id": "playlist_001",
                            "name": "My Favorite AI Tracks",
                            "description": "A collection of my best AI-generated music",
                            "track_count": 2,
                            "total_duration": 420,
                            "created_at": "2024-01-10T12:00:00Z"
                        },
                        {
                            "id": "playlist_002",
                            "name": "Ambient Collection",
                            "description": "Relaxing ambient tracks",
                            "track_count": 5,
                            "total_duration": 1200,
                            "created_at": "2024-01-08T09:00:00Z"
                        }
                    ],
                    "total_playlists": 2
                }
                return create_response(playlists_data)
                
        elif req.method == "POST":
            req_body = req.get_json()
            new_playlist = {
                "id": f"playlist_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "user_id": user_id,
                "name": req_body.get('name', 'Untitled Playlist'),
                "description": req_body.get('description', ''),
                "tracks": [],
                "created_at": datetime.datetime.utcnow().isoformat(),
                "track_count": 0,
                "total_duration": 0,
                "status": "created"
            }
            return create_response(new_playlist, 201)
            
        elif req.method == "PUT":
            if not playlist_id:
                return create_response({"error": "playlist_id parameter required"}, 400)
            
            req_body = req.get_json()
            updated_playlist = {
                "id": playlist_id,
                "user_id": user_id,
                "updated_fields": list(req_body.keys()),
                "updated_at": datetime.datetime.utcnow().isoformat(),
                "status": "updated"
            }
            return create_response(updated_playlist)
            
        elif req.method == "DELETE":
            if not playlist_id:
                return create_response({"error": "playlist_id parameter required"}, 400)
            
            return create_response({
                "id": playlist_id,
                "user_id": user_id,
                "status": "deleted",
                "deleted_at": datetime.datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        logging.error(f"Playlists error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Auth Token Endpoint
@app.route(route="auth-token", methods=["POST", "OPTIONS"])
def auth_token(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Auth token endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        req_body = req.get_json()
        user_id = req_body.get('user_id', req_body.get('username', 'demo_user'))
        plan = req_body.get('plan', 'free')
        
        # Mock token generation
        token_data = {
            "access_token": f"demo_token_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_id": user_id,
            "plan": plan,
            "issued_at": datetime.datetime.utcnow().isoformat()
        }
        
        return create_response(token_data)
    except Exception as e:
        logging.error(f"Auth token error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# User Quota Endpoint
@app.route(route="user-quota", methods=["GET", "OPTIONS"])
def user_quota(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('User quota endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    try:
        user_id = req.params.get('user_id', 'demo_user')
        
        quota_data = {
            "user_id": user_id,
            "plan": "free",
            "quotas": {
                "generation_limit": 10,
                "generation_used": 3,
                "generation_remaining": 7,
                "storage_limit": 100,  # MB
                "storage_used": 25,    # MB
                "storage_remaining": 75 # MB
            },
            "reset_date": "2024-02-01T00:00:00Z",
            "upgrade_available": True
        }
        
        return create_response(quota_data)
    except Exception as e:
        logging.error(f"User quota error: {str(e)}")
        return create_response({"error": str(e)}, 500)

# Genres Endpoint
@app.route(route="genres", methods=["GET", "OPTIONS"])
def genres(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Genres endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    genres_data = {
        "genres": [
            {"id": "electronic", "name": "Electronic", "description": "Electronic and synthesized music"},
            {"id": "ambient", "name": "Ambient", "description": "Atmospheric and environmental sounds"},
            {"id": "classical", "name": "Classical", "description": "Traditional classical music"},
            {"id": "jazz", "name": "Jazz", "description": "Jazz and improvisational music"},
            {"id": "rock", "name": "Rock", "description": "Rock and alternative music"},
            {"id": "pop", "name": "Pop", "description": "Popular and mainstream music"},
            {"id": "folk", "name": "Folk", "description": "Traditional and acoustic music"},
            {"id": "experimental", "name": "Experimental", "description": "Avant-garde and experimental sounds"}
        ],
        "total": 8
    }
    
    return create_response(genres_data)

# Moods Endpoint
@app.route(route="moods", methods=["GET", "OPTIONS"])
def moods(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Moods endpoint triggered.')
    
    if req.method == "OPTIONS":
        return handle_options(req)
    
    moods_data = {
        "moods": [
            {"id": "energetic", "name": "Energetic", "description": "High energy and upbeat"},
            {"id": "relaxed", "name": "Relaxed", "description": "Calm and peaceful"},
            {"id": "melancholic", "name": "Melancholic", "description": "Sad and contemplative"},
            {"id": "uplifting", "name": "Uplifting", "description": "Positive and inspiring"},
            {"id": "mysterious", "name": "Mysterious", "description": "Dark and enigmatic"},
            {"id": "romantic", "name": "Romantic", "description": "Love and emotional"},
            {"id": "aggressive", "name": "Aggressive", "description": "Intense and powerful"},
            {"id": "dreamy", "name": "Dreamy", "description": "Ethereal and floating"}
        ],
        "total": 8
    }
    
    return create_response(moods_data)