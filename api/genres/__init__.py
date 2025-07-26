import azure.functions as func
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Genres endpoint triggered.')
    
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
        # Music genres from the original backend
        genres = [
            {"id": "pop", "name": "Pop", "description": "Popular music with catchy melodies"},
            {"id": "rock", "name": "Rock", "description": "Guitar-driven energetic music"},
            {"id": "jazz", "name": "Jazz", "description": "Improvised, swing rhythms"},
            {"id": "classical", "name": "Classical", "description": "Orchestral and chamber music"},
            {"id": "electronic", "name": "Electronic", "description": "Synthesized and digital sounds"},
            {"id": "hip-hop", "name": "Hip Hop", "description": "Rhythmic spoken lyrics"},
            {"id": "country", "name": "Country", "description": "Rural and folk-inspired"},
            {"id": "blues", "name": "Blues", "description": "Emotional and soulful"}
        ]
        
        response_data = {
            "success": True,
            "genres": genres
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
        logging.error(f"Genres error: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False, 
                "error": f"Failed to get genres: {str(e)}"
            }),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )
