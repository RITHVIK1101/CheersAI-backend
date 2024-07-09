from pymongo import MongoClient

import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB')]
messages_collection = db["chatmessages"]
goals_collection = db["goals_collection"]
