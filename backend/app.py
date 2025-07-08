from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import logging
from datetime import datetime, timedelta
import jwt
from functools import wraps
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enhanced CORS configuration for production
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://*.azurestaticapps.net",
            "https://localhost:3000",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Environment variables for production
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'music-files')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')

# Initialize Azure Blob Storage
if AZURE_CONNECTION_STRING:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
else:
    logger.warning("Azure connection string not configured - using mock mode")
    blob_service_client = None
    container_client = None

# Rate limiting storage (in production, use Redis)
user_requests = {}

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        
        if not token and ENVIRONMENT == 'production':
            return jsonify({'error': 'Token is missing'}), 401
        
        if token:
            try:
                data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
                current_user = data['user_id']
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Token is invalid'}), 401
        else:
            # Development mode - allow without token
            current_user = 'dev_user'
        
        return f(current_user, *args, **kwargs)
    return decorated

# Rate limiting decorator
def rate_limit(max_requests=5, window=3600):  # 5 requests per hour for free tier
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = args[0] if args else 'anonymous'
            current_time = time.time()
            
            if user_id not in user_requests:
                user_requests[user_id] = []
            
            # Clean old requests
            user_requests[user_id] = [
                req_time for req_time in user_requests[user_id] 
                if current_time - req_time < window
            ]
            
            if len(user_requests[user_id]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per hour allowed'
                }), 429
            
            user_requests[user_id].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Portal AI Music API',
        'version': '1.0.0',
        'environment': ENVIRONMENT
    }
    
    # Check Azure Blob Storage connectivity
    if blob_service_client:
        try:
            container_client.get_container_properties()
            health_status['storage'] = 'connected'
        except Exception as e:
            health_status['storage'] = 'disconnected'
            health_status['storage_error'] = str(e)
            logger.error(f"Storage health check failed: {e}")
    else:
        health_status['storage'] = 'not_configured'
    
    return jsonify(health_status)

@app.route('/api/auth/token', methods=['POST'])
def generate_token():
    """Generate JWT token for API access (simplified for demo)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'demo_user')
        plan = data.get('plan', 'free')  # free, creator, professional
        
        # In production, validate user credentials here
        payload = {
            'user_id': user_id,
            'plan': plan,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'status': 'success',
            'token': token,
            'expires_in': 86400  # 24 hours
        })
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate token'
        }), 500

@app.route('/api/generate-music', methods=['POST'])
@token_required
@rate_limit(max_requests=10, window=3600)  # 10 requests per hour
def generate_music(current_user):
    """Generate music based on text prompt and parameters"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        
        # Extract and validate parameters
        prompt = data.get('prompt', '').strip()
        duration = data.get('duration', 30)
        genre = data.get('genre', 'pop')
        mood = data.get('mood', 'upbeat')
        
        # Enhanced validation
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if len(prompt) > 500:
            return jsonify({'error': 'Prompt must be less than 500 characters'}), 400
        
        if not isinstance(duration, int) or duration < 10 or duration > 300:
            return jsonify({'error': 'Duration must be between 10 and 300 seconds'}), 400
        
        logger.info(f"Generating music for user {current_user}: prompt='{prompt}', duration={duration}, genre={genre}, mood={mood}")
        
        # In production, this would use actual AI model (MusicGen)
        # For now, simulate processing time and return mock data
        time.sleep(2)  # Simulate AI processing
        
        track_id = str(uuid.uuid4())
        track_title = f"{mood.title()} {genre.title()} Track"
        
        # Generate secure download URL
        if blob_service_client:
            # In production: save actual generated audio to blob storage
            blob_name = f"music/{current_user}/{track_id}.wav"
            
            # Generate SAS URL for secure download (valid for 24 hours)
            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=CONTAINER_NAME,
                blob_name=blob_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=24)
            )
            download_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{blob_name}?{sas_token}"
        else:
            # Mock URL for development
            download_url = f'https://example.com/tracks/{track_id}.wav'
        
        response_data = {
            'status': 'success',
            'track': {
                'id': track_id,
                'title': track_title,
                'duration': duration,
                'genre': genre,
                'mood': mood,
                'prompt': prompt,
                'url': f'https://example.com/tracks/{track_id}.mp3',
                'download_url': download_url,
                'created_at': datetime.utcnow().isoformat(),
                'user_id': current_user,
                'license': 'royalty_free'
            }
        }
        
        logger.info(f"Successfully generated track: {track_id} for user: {current_user}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating music for user {current_user}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate music. Please try again.'
        }), 500

@app.route('/api/tracks', methods=['GET'])
@token_required
def get_user_tracks(current_user):
    """Get user's generated tracks"""
    try:
        # In production, fetch from database
        sample_tracks = [
            {
                'id': 'track_001',
                'title': 'Upbeat Pop Energy',
                'duration': 30,
                'genre': 'pop',
                'mood': 'upbeat',
                'url': 'https://example.com/sample1.mp3',
                'download_url': 'https://example.com/download/sample1.wav',
                'created_at': '2024-01-15T10:30:00.000Z',
                'user_id': current_user
            },
            {
                'id': 'track_002', 
                'title': 'Calm Ambient Waves',
                'duration': 60,
                'genre': 'ambient',
                'mood': 'calm',
                'url': 'https://example.com/sample2.mp3',
                'download_url': 'https://example.com/download/sample2.wav',
                'created_at': '2024-01-15T11:00:00.000Z',
                'user_id': current_user
            }
        ]
        
        return jsonify({
            'status': 'success',
            'tracks': sample_tracks,
            'total': len(sample_tracks)
        })
    except Exception as e:
        logger.error(f"Error fetching tracks for user {current_user}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch tracks'
        }), 500

@app.route('/api/genres', methods=['GET'])
def get_genres():
    """Get available music genres"""
    genres = [
        {'id': 'pop', 'name': 'Pop', 'description': 'Catchy, mainstream melodies'},
        {'id': 'rock', 'name': 'Rock', 'description': 'Guitar-driven, energetic'},
        {'id': 'electronic', 'name': 'Electronic', 'description': 'Synthesized, digital sounds'},
        {'id': 'classical', 'name': 'Classical', 'description': 'Orchestral, traditional'},
        {'id': 'jazz', 'name': 'Jazz', 'description': 'Improvisational, sophisticated'},
        {'id': 'hip-hop', 'name': 'Hip Hop', 'description': 'Rhythmic, urban beats'},
        {'id': 'country', 'name': 'Country', 'description': 'Folk-inspired, storytelling'},
        {'id': 'folk', 'name': 'Folk', 'description': 'Acoustic, traditional'},
        {'id': 'ambient', 'name': 'Ambient', 'description': 'Atmospheric, meditative'},
        {'id': 'cinematic', 'name': 'Cinematic', 'description': 'Epic, movie-like'},
        {'id': 'blues', 'name': 'Blues', 'description': 'Soulful, expressive'},
        {'id': 'reggae', 'name': 'Reggae', 'description': 'Relaxed, Caribbean rhythm'}
    ]
    return jsonify({
        'status': 'success',
        'genres': genres
    })

@app.route('/api/moods', methods=['GET'])
def get_moods():
    """Get available music moods"""
    moods = [
        {'id': 'upbeat', 'name': 'Upbeat', 'description': 'Happy, energetic feeling'},
        {'id': 'calm', 'name': 'Calm', 'description': 'Peaceful, relaxing'},
        {'id': 'energetic', 'name': 'Energetic', 'description': 'High-energy, motivating'},
        {'id': 'melancholic', 'name': 'Melancholic', 'description': 'Sad, reflective'},
        {'id': 'mysterious', 'name': 'Mysterious', 'description': 'Dark, intriguing'},
        {'id': 'romantic', 'name': 'Romantic', 'description': 'Love-themed, emotional'},
        {'id': 'epic', 'name': 'Epic', 'description': 'Grand, heroic'},
        {'id': 'peaceful', 'name': 'Peaceful', 'description': 'Serene, tranquil'},
        {'id': 'dramatic', 'name': 'Dramatic', 'description': 'Intense, theatrical'},
        {'id': 'playful', 'name': 'Playful', 'description': 'Fun, lighthearted'}
    ]
    return jsonify({
        'status': 'success',
        'moods': moods
    })

@app.route('/api/user/quota', methods=['GET'])
@token_required
def get_user_quota(current_user):
    """Get user's current usage quota"""
    try:
        # In production, fetch from database
        current_time = time.time()
        user_usage = len(user_requests.get(current_user, []))
        
        # Mock quota based on plan (would come from database)
        quotas = {
            'free': {'daily': 5, 'monthly': 50, 'max_duration': 30},
            'creator': {'daily': 100, 'monthly': 1000, 'max_duration': 180},
            'professional': {'daily': -1, 'monthly': -1, 'max_duration': 600}  # -1 = unlimited
        }
        
        user_plan = 'free'  # Would fetch from database
        quota_info = quotas.get(user_plan, quotas['free'])
        
        return jsonify({
            'status': 'success',
            'quota': {
                'plan': user_plan,
                'used_today': user_usage,
                'daily_limit': quota_info['daily'],
                'monthly_limit': quota_info['monthly'],
                'max_duration': quota_info['max_duration'],
                'remaining_today': max(0, quota_info['daily'] - user_usage) if quota_info['daily'] > 0 else -1
            }
        })
    except Exception as e:
        logger.error(f"Error fetching quota for user {current_user}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch quota information'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'code': 404
    }), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'status': 'error',
        'message': 'Rate limit exceeded. Please try again later.',
        'code': 429
    }), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'code': 500
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Portal AI Music API on port {port}")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Azure Storage: {'Configured' if AZURE_CONNECTION_STRING else 'Not configured'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)