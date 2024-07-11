import firebase_admin
from firebase_admin import credentials
import os
import json

firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
cred_dict = json.loads(firebase_credentials)

# cred = credentials.Certificate("/home/evan/Documents/firebase/startup-app-bb5a1-firebase-adminsdk-87b5c-14ca32614b.json")

cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
print("firebase initialized")