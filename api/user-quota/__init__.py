import azure.functions as func
import json
import logging
from datetime import datetime, timedelta

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('User quota endpoint triggered.')
    
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
        # Placeholder quota information
        reset_date = datetime.utcnow() + timedelta(days=1)
        reset_date = reset_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        response_data = {
            "success": True,
            "quota": {
                "plan": "free",
                "daily_limit": 10,
                "remaining_today": 7,
                "used_today": 3,
                "reset_date": reset_date.isoformat() + "Z"
            }
        }
        
        logging.info(f"Quota response: {response_data}")
        
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
        logging.error(f"User quota error: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False, 
                "error": f"Failed to get quota: {str(e)}"
            }),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )
