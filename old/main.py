# main.py
from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
# from firebase_admin import auth as firebase_auth
from database import users_collection, chats_collection
from chatgpt_service import get_chatgpt_response
from vapi_service import initiate_call
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ChatMessage(BaseModel):
    message: str

class CallRequest(BaseModel):
    contact: str

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         decoded_token = firebase_auth.verify_id_token(token)
#         user = users_collection.find_one({"uid": decoded_token['uid']})
#         if not user:
#             user = {"uid": decoded_token['uid'], "email": decoded_token['email']}
#             users_collection.insert_one(user)
#         return user
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#         )

@app.post("/chat/")
async def chat(message: ChatMessage):
    response = get_chatgpt_response(message.message)
    chat_record = {
        "user_id": "guest",
        "message": message.message,
        "response": response
    }
    chats_collection.insert_one(chat_record)
    return {"response": response}

@app.post("/call/")
async def call(request: CallRequest):
    call_status = initiate_call(request.contact, request.contact)
    call_record = {
        "user_id": "guest",
        "contact": request.contact,
        "status": call_status
    }
    chats_collection.insert_one(call_record)
    return {"status": call_status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

