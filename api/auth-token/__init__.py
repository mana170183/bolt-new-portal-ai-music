import azure.functions as func
import json
import logging
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Auth token endpoint triggered.')
    
    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
    
    try:
        # Get request data
        data = req.get_json() or {}
        logging.info(f"Auth request data: {data}")
        
        user_id = data.get('user_id', 'demo_user')
        plan = data.get('plan', 'free')
        
        # Placeholder authentication - return a mock token
        response_data = {
            "success": True,
            "token": f"mock-jwt-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user": {
                "id": user_id,
                "email": "user@example.com",
                "plan": plan,
                "created_at": datetime.utcnow().isoformat()
            }
        }
        
        logging.info(f"Auth response: {response_data}")
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            }
        )
        
    except Exception as e:
        logging.error(f"Auth token error: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False, 
                "error": f"Authentication failed: {str(e)}"
            }),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )
