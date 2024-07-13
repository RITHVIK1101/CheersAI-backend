from fastapi import APIRouter, HTTPException, Form, UploadFile, Depends, Header
from pydantic import BaseModel
import openai
from app.database import messages_collection
from typing import Optional
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth, credentials
import base64


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")
chatgpt_prompt = os.getenv("CHATGPT_PROMPT")

cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
firebase_admin.initialize_app(cred)

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str


async def get_last_conversation(user_id: str, limit: int = 5):
    # Retrieve the last conversation for the user
    history = (
        messages_collection.find({"user_id": user_id}).sort([("_id", -1)]).limit(limit)
    )
    return list(history)


async def get_current_user(authorization: str = Header()):
    try:
        token = authorization.split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/")
async def chat(
    user_id: str = Form(...),
    message: str = Form(...),
    image: Optional[UploadFile] = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get the last conversation from the database
        conversation_history = await get_last_conversation(user_id)
        context = [{"role": "system", "content": chatgpt_prompt}]

        for conversation in reversed(conversation_history):
            context.append({"role": "user", "content": conversation["message"]})
            context.append({"role": "assistant", "content": conversation["response"]})

        context.append({"role": "user", "content":message})

        if image:
            image_data = await image.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            context.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            })

        response = openai.chat.completions.create(
            model=openai_model,
            messages=context,
            temperature=0.7,
            max_tokens=500,
        )
                # Debugging: print the response
        print("OpenAI API response:", response)

        reply = response.choices[0].message.content

        # Store the new conversation
        message_doc = {
            "user_id": user_id,
            "message": message,
            "response": reply,
        }
        messages_collection.insert_one(message_doc)

        return {"message": message, "response": reply}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
