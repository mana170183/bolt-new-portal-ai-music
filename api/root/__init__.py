import azure.functions as func
import json
import logging
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Root endpoint triggered.')
    
    try:
        response_data = {
            "message": "AI Music Generation Backend API",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "architecture": "Frontend ↔ Azure Functions ↔ Azure OpenAI + Storage + SQL + Music APIs",
            "location": "West Europe",
            "endpoints": {
                "health": "/api/health",
                "generate_music": "/api/generate-music",
                "music_library": "/api/music-library",
                "genres": "/api/genres",
                "moods": "/api/moods",
                "auth_token": "/api/auth/token",
                "user_quota": "/api/user/quota"
            },
            "success": True
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
    except Exception as e:
        logging.error(f"Root endpoint error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )
