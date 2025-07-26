import azure.functions as func
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Moods endpoint triggered.')
    
    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
    
    try:
        # Music moods from the original backend
        moods = [
            {"id": "happy", "name": "Happy", "description": "Upbeat and joyful"},
            {"id": "sad", "name": "Sad", "description": "Melancholic and emotional"},
            {"id": "energetic", "name": "Energetic", "description": "High energy and motivating"},
            {"id": "calm", "name": "Calm", "description": "Peaceful and relaxing"},
            {"id": "romantic", "name": "Romantic", "description": "Love and romance"},
            {"id": "mysterious", "name": "Mysterious", "description": "Dark and intriguing"},
            {"id": "epic", "name": "Epic", "description": "Grand and cinematic"},
            {"id": "nostalgic", "name": "Nostalgic", "description": "Reminiscent and wistful"}
        ]
        
        response_data = {
            "success": True,
            "moods": moods
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
        
    except Exception as e:
        logging.error(f"Moods error: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False, 
                "error": f"Failed to get moods: {str(e)}"
            }),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )
