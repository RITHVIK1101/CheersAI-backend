from pymongo import MongoClient

import os
from dotenv import load_dotenv

load_dotenv()

# client = MongoClient(os.getenv('MONGODB_URI'))

client = MongoClient("mongodb+srv://Testin:dbsjr4XNX6jr4c@cluster0.delv054.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
goals_collection = db["goals_collection"]
users_collection = db["users"]
chats_collection = db["chatmessages"]