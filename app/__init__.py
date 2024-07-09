from fastapi import FastAPI

app = FastAPI()

from app.routes import chat, goals

app.include_router(chat.router, prefix="/chat")
app.include_router(goals.router, prefix="/goals")
