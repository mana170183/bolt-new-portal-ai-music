import os
import requests
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

if not supabase_url or not supabase_key:
    logger.error("Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_ANON_KEY")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

# Optional: Initialize Sentry for error tracking
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

# Optional: Initialize Redis for caching
redis_client = None
redis_url = os.getenv('REDIS_URL')
if redis_url:
    try:
        import redis
        redis_client = redis.from_url(redis_url)
        logger.info("Redis caching enabled")
    except ImportError:
        logger.warning("Redis not available - caching disabled")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "supabase": "connected",
            "redis": "connected" if redis_client else "disabled",
            "huggingface": "configured" if os.getenv('HUGGINGFACE_API_KEY') else "missing"
        }
    })

@app.route('/generate-music', methods=['POST'])
def generate_music():
    """Generate music using Hugging Face API"""
    try:
        data = request.json
        
        # Validate required fields
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing required field: prompt"}), 400
        
        user_id = data.get('user_id', 'anonymous')
        prompt = data.get('prompt', '')
        style = data.get('style', 'general')
        duration = min(data.get('duration', 30), 120)  # Limit to 2 minutes for free tier
        
        # Create unique generation ID
        generation_id = str(uuid.uuid4())
        
        logger.info(f"Generating music for user {user_id}: {prompt}")
        
        # Check cache first (if Redis is available)
        cache_key = f"music:{hash(f'{prompt}:{style}:{duration}')}"
        cached_result = None
        
        if redis_client:
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info("Returning cached result")
                    return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
        
        # Insert generation record into database
        try:
            result = supabase.table('music_generations').insert({
                'id': generation_id,
                'user_id': user_id,
                'prompt': prompt,
                'style': style,
                'duration': duration,
                'status': 'processing'
            }).execute()
        except Exception as e:
            logger.error(f"Database insert failed: {e}")
            return jsonify({"error": "Database error"}), 500
        
        # Call Hugging Face API
        hf_token = os.getenv('HUGGINGFACE_API_KEY')
        if not hf_token:
            return jsonify({"error": "AI service not configured"}), 500
        
        hf_url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {
            "inputs": f"{prompt} in {style} style",
            "parameters": {
                "max_new_tokens": duration * 50,  # Approximate tokens for duration
                "do_sample": True,
                "temperature": 0.8
            }
        }
        
        try:
            response = requests.post(hf_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                # Save audio file to Supabase storage
                audio_data = response.content
                file_name = f"generated/{generation_id}.wav"
                
                try:
                    storage_response = supabase.storage.from_('music-files').upload(
                        file_name, audio_data, {"content-type": "audio/wav"}
                    )
                    
                    # Get public URL
                    file_url_response = supabase.storage.from_('music-files').get_public_url(file_name)
                    file_url = file_url_response.get('publicURL')
                    
                    # Update database record
                    supabase.table('music_generations').update({
                        'file_url': file_url,
                        'status': 'completed'
                    }).eq('id', generation_id).execute()
                    
                    result_data = {
                        "id": generation_id,
                        "status": "completed",
                        "file_url": file_url,
                        "prompt": prompt,
                        "style": style,
                        "duration": duration
                    }
                    
                    # Cache successful result (if Redis is available)
                    if redis_client:
                        try:
                            redis_client.setex(cache_key, 3600, json.dumps(result_data))  # Cache for 1 hour
                        except Exception as e:
                            logger.warning(f"Cache write failed: {e}")
                    
                    logger.info(f"Successfully generated music: {generation_id}")
                    return jsonify(result_data)
                
                except Exception as e:
                    logger.error(f"Storage upload failed: {e}")
                    # Update status to failed
                    supabase.table('music_generations').update({
                        'status': 'failed'
                    }).eq('id', generation_id).execute()
                    return jsonify({"error": "Storage upload failed"}), 500
            
            elif response.status_code == 503:
                # Model is loading, return processing status
                return jsonify({
                    "id": generation_id,
                    "status": "processing",
                    "message": "AI model is loading, please try again in a few moments"
                }), 202
            
            else:
                logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                # Update status to failed
                supabase.table('music_generations').update({
                    'status': 'failed'
                }).eq('id', generation_id).execute()
                return jsonify({"error": "AI service error"}), 500
                
        except requests.exceptions.Timeout:
            logger.error("Hugging Face API timeout")
            return jsonify({"error": "Generation timeout - please try a shorter duration"}), 408
        except Exception as e:
            logger.error(f"Hugging Face API request failed: {e}")
            return jsonify({"error": "AI service unavailable"}), 503
            
    except Exception as e:
        logger.error(f"Unexpected error in generate_music: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/generations/<user_id>', methods=['GET'])
def get_user_generations(user_id):
    """Get all music generations for a user"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 records
        offset = int(request.args.get('offset', 0))
        
        result = supabase.table('music_generations').select('*').eq('user_id', user_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        return jsonify({
            "generations": result.data,
            "total": len(result.data),
            "limit": limit,
            "offset": offset
        })
    except Exception as e:
        logger.error(f"Error fetching user generations: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/generation/<generation_id>', methods=['GET'])
def get_generation(generation_id):
    """Get specific generation by ID"""
    try:
        result = supabase.table('music_generations').select('*').eq('id', generation_id).execute()
        
        if not result.data:
            return jsonify({"error": "Generation not found"}), 404
        
        return jsonify(result.data[0])
    except Exception as e:
        logger.error(f"Error fetching generation: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get basic usage statistics"""
    try:
        # Total generations
        total_result = supabase.table('music_generations').select('id', count='exact').execute()
        total_generations = total_result.count
        
        # Successful generations
        success_result = supabase.table('music_generations').select('id', count='exact').eq('status', 'completed').execute()
        successful_generations = success_result.count
        
        # Recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        recent_result = supabase.table('music_generations').select('id', count='exact').gte('created_at', yesterday).execute()
        recent_generations = recent_result.count
        
        return jsonify({
            "total_generations": total_generations,
            "successful_generations": successful_generations,
            "success_rate": round((successful_generations / total_generations * 100) if total_generations > 0 else 0, 2),
            "recent_24h": recent_generations
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({"error": "Database error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Portal AI Music API on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Supabase URL: {supabase_url}")
    logger.info(f"Redis enabled: {redis_client is not None}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
