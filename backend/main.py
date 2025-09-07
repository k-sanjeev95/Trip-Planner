import json
from fastapi import FastAPI, HTTPException,status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models_trip import  *
from services import booking_services, firesbase_services,google_ai_services,maps_service
from services.firesbase_services import get_current_user_uid
app = FastAPI(title="AI Trip Planner Backend", version="1.0.0")

# CORS middleware for communication with the React frontend
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Trip Planner API"}



async def itinerary_stream_generator(request_data):
    """A generator that yields chunks from the Gemini AI API."""
    try:
        # Step 1: Fetch real-time data from the aggregator service, now with start_date
        search_info_dict = maps_service.get_realtime_data(
            request_data['destination'],
            request_data['start_date']
        )
        
        # Format the dictionary into a string for the AI prompt
        search_info = ""
        for key, value in search_info_dict.items():
            search_info += f"- {key}: {value}\n"
        
        print(f"Aggregated real-time data for Gemini prompt:\n{search_info}")
        
        # Step 2: Stream itinerary using the Gemini AI service
        stream = google_ai_services.stream_itinerary_with_ai(request_data, search_info)
        
        print("Starting to stream chunks from Gemini...")
        async for chunk in stream:
            print(f"Received chunk: {chunk}")
            yield chunk

    except Exception as e:
        print(f"An error occurred in the streaming generator: {e}")
        yield json.dumps({"error": f"An error occurred: {e}"})

@app.post("/plan_trip")
async def plan_trip(request: TripRequest):
    """Generates a personalized itinerary as a real-time stream."""
    return StreamingResponse(itinerary_stream_generator(request.model_dump()), media_type="text/event-stream")


# @app.post("/plan_trip")
# async def plan_trip(request: TripRequest):
#     """Generates a personalized itinerary as a real-time stream."""
#     return StreamingResponse(itinerary_stream_generator(request.dict()), media_type="text/event-stream")


@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_user(user_data: UserCreate):
    """Creates a new user account."""
    return firesbase_services.create_firebase_user(user_data.full_name,user_data.email, user_data.password)
@app.post("/itinerary/save")
async def save_user_itinerary(
    itinerary_data: ItineraryData,
    uid: str = Depends(get_current_user_uid)
):
    """Saves a generated itinerary to the user's account."""
    return await firesbase_services.save_itinerary_to_firestore(uid, itinerary_data.plan)
    

@app.get("/itinerary/{trip_id}")
async def get_user_itinerary(
    trip_id: str,
    uid: str = Depends(get_current_user_uid)
):
    """
    Retrieves a specific saved itinerary by its ID for the authenticated user.
    """
    return await firesbase_services.get_itinerary_by_id(uid, trip_id)


@app.get("/users/me")
async def read_current_user(uid: str = Depends(get_current_user_uid)):
    """Retrieves the current authenticated user's ID."""
    return {"user_uid": uid, "message": "You are authenticated."}


@app.post("/update_itinerary")
def update_itinerary(request: UpdateItineraryRequest):
    """Allows the user to make real-time adjustments to an existing itinerary."""
    print(f"Received request to update itinerary ID: {request.trip_id}")
    itinerary = firesbase_services.get_itinerary(request.trip_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
        
    if firesbase_services.update_itinerary(request.trip_id, request.updates):
        return {"message": "Itinerary updated successfully."}
    
    raise HTTPException(status_code=500, detail="Failed to update itinerary.")


@app.post("/book_trip")
def book_trip(request: BookingRequest):
    """Handles payment and final booking of the trip."""
    print(f"Received booking request for trip ID: {request.trip_id}")
    
    if not booking_services.process_payment(request.payment_token, request.total_amount):
        raise HTTPException(status_code=400, detail="Payment failed. Please try again.")
    
    if not booking_services.book_trip(request.trip_id):
        raise HTTPException(status_code=500, detail="Booking failed.")
    
    return {"message": "Trip booked successfully!", "trip_id": request.trip_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
	