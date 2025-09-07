import firebase_admin
from firebase_admin import credentials, auth, firestore
from fastapi import Header, HTTPException, status, Depends
from dotenv import load_dotenv
import os

load_dotenv()

try:
    cred = credentials.Certificate(os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH'))
    firebase_admin.initialize_app(cred)
except ValueError as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    print("Please ensure FIREBASE_SERVICE_ACCOUNT_PATH is set correctly in your .env file.")

db = firestore.client()

def create_firebase_user(name: str, email: str, password: str):
    """
    Creates a new user in Firebase Authentication with a display name.
    """
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        return {"uid": user.uid, "message": "User created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def get_current_user_uid(id_token: str = Header(None)):
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is missing."
        )
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        return uid
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token."
        )
    


async def save_itinerary_to_firestore(uid: str, itinerary_data: dict):
    try:
        user_ref = db.collection("users").document(uid)
        itinerary_ref = user_ref.collection("itineraries").document()
        
        await itinerary_ref.set({
            "plan": itinerary_data,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        return {"message": "Itinerary saved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    

async def get_itinerary_by_id(uid: str, trip_id: str):
    """
    Retrieves a specific itinerary from Firestore by its unique trip ID.
    The uid ensures the user can only access their own data.
    """
    try:
        itinerary_ref = db.collection("users").document(uid).collection("itineraries").document(trip_id)
        itinerary_doc = await itinerary_ref.get()

        if not itinerary_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found or you do not have permission to view it."
            )
        
        return itinerary_doc.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )