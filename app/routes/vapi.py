import json
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse as jsonify
from app.database import messages_collection
import pytz

router = APIRouter()

class VapiReport(BaseModel):
    user_id: str
    call_id: str
    timestamp: datetime
    summary: str
    transcript: str
    recording_url: str
    full_report: dict

@router.api_route('/', methods=['GET', 'POST'])
async def handle_vapi_requests(request: Request):
    print("Received request", request.method, request.url, json.dumps(await request.json()))
    if request.method == 'GET':
        return await get_vapi_context(request)
    elif request.method == 'POST':
        return await handle_vapi_report(request)

async def get_vapi_context(request: Request):
    print("Handling GET request")
    data = await request.json()

    user_id = data.get('metadata', {}).get('userId')
    if not user_id:
        return jsonify({"error": "User ID not provided"}, status_code=400),

    # Fetch context based on user ID
    context = await get_last_user_messages(user_id)

    return jsonify({
        "assistant": {
            "model": {
                "messages": [
                    {
                        "role": "system",
                        "content": context
                    }
                ]
            }
        }
    })

async def get_last_user_messages(user_id: str, limit: int = 5):
    print("Fetching last user messages for", user_id)
    # Retrieve the last conversation messages for the user
    history = (
        messages_collection.find({"user_id": user_id}).sort([("_id", -1)]).limit(limit)
    )
    # Convert ObjectId to string and datetime to ISO format for JSON serialization
    return [{**msg, "_id": str(msg["_id"]), "timestamp": msg.get("timestamp", "").isoformat() if "timestamp" in msg else None} for msg in history]

async def handle_vapi_report(request: Request):
    print("Handling POST request", json.dumps(await request.json()))
    data = await request.json()
    
    if data['message']['type'] == 'end-of-call-report':
        print("Handling end-of-call report")
        call_data = data['message']['call']
        
        # Extract user_id from metadata
        user_id = call_data.get('metadata', {}).get('userId')

        # Debug print to check the extracted user_id
        print("Extracted user_id:", user_id)
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found in call metadata")
        
        # Search for the user_id in MongoDB
        user = messages_collection.find({"user_id": user_id}).sort([("_id", -1)]).limit(50)
        
        if not user:
            raise HTTPException(status_code=404, detail="User ID not found in the database")
        
        # Prepare the document to be stored
        report = {
            'user_id': user_id,
            'call_id': call_data['id'],
            'timestamp': datetime.now(pytz.utc),
            'summary': data['message'].get('summary'),
            'transcript': data['message'].get('transcript'),
            'recording_url': data['message'].get('recordingUrl'),
            'full_report': data  # Store the full report for reference
        }
        
        # Insert the document into MongoDB
        result = messages_collection.insert_one(report)
        
        print("Stored report with id", result.inserted_id)
        return jsonify({
            'message': 'Call report stored successfully',
            'document_id': str(result.inserted_id)
        }), 201
    else:
        print("Ignoring non-end-of-call report message")
        return jsonify({'message': 'Received non-end-of-call report message'}), 200

