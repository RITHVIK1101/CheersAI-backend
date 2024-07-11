from flask import Flask, request, jsonify
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request
from app.database import messages_collection
from bson import ObjectId

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
    if request.method == 'GET':
        return await get_vapi_context(request)
    elif request.method == 'POST':
        return await handle_vapi_report(request)


def get_vapi_context(request: Request):
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 400

    # Get the last conversation for the user
    history = get_last_conversation(user_id)

    # Format the conversation history as Vapi expects
    formatted_history = [
        {
            "role": "user" if msg["role"] == "user" else "assistant",
            "content": msg["content"]
        }
        for msg in history
    ]

    return jsonify({
        "messages": formatted_history
    })

async def get_last_conversation(user_id: str, limit: int = 5):
    # Retrieve the last conversation for the user
    history = (
        messages_collection.find({"user_id": user_id}).sort([("_id", -1)]).limit(limit)
    )
    return list(history)


def handle_vapi_report(request: Request):
    data = request.json
    
    if data['message']['type'] == 'end-of-call-report':
        call_data = data['message']['call']
        
        # Extract user_id from metadata
        user_id = call_data.get('metadata', {}).get('userId')
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found in call metadata")
        
        # Search for the user_id in MongoDB
        user = messages_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User ID not found in the database")
        
        # Prepare the document to be stored
        report = {
            'user_id': user_id,
            'call_id': call_data['id'],
            'timestamp': datetime.now(datetime.timezone.utc),
            'summary': data['message'].get('summary'),
            'transcript': data['message'].get('transcript'),
            'recording_url': data['message'].get('recordingUrl'),
            'full_report': data  # Store the full report for reference
        }
        
        # Insert the document into MongoDB
        result = messages_collection.insert_one(report)
        
        return jsonify({
            'message': 'Call report stored successfully',
            'document_id': str(result.inserted_id)
        }), 201
    else:
        return jsonify({'message': 'Received non-end-of-call report message'}), 200

