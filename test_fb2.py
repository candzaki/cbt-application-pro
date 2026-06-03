import firebase_admin
from firebase_admin import credentials, firestore

try:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    doc_ref = db.collection('cbt_exam_pro').document('database')
    
    # Try getting
    print("Reading from Firestore...")
    doc = doc_ref.get()
    print(f"Exists: {doc.exists}")
    if doc.exists:
        print(f"Data: {doc.to_dict().keys()}")
        
    # Try setting
    print("Writing to Firestore...")
    doc_ref.set({"test": "ok", "users": {}}, merge=True)
    print("Write successful!")
    
except Exception as e:
    import traceback
    traceback.print_exc()
