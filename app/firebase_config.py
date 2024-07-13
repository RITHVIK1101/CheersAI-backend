import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("/home/evan/Documents/firebase/startup-app-bb5a1-firebase-adminsdk-87b5c-14ca32614b.json")
firebase_admin.initialize_app(cred)
print("firebase initialized")