import firebase_admin
from firebase_admin import credentials, firestore

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase_credentials.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    doc_ref = db.collection('cbt_exam_pro').document('database')
    doc = doc_ref.get()
    print("SUCCESS: Database is active!")
except Exception as e:
    print("ERROR:", e)
