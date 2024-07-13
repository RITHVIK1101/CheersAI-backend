from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import chat, goals,vapi

app.include_router(chat.router, prefix="/chat")
app.include_router(goals.router, prefix="/goals")
app.include_router(vapi.router, prefix="/vapi")
