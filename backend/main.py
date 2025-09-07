import os
import uuid
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models_trip import  *
from services import booking_services,firestore_services,google_ai_services,maps_service
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

# async def itinerary_stream_generator(request_data):
#     """A generator that yields chunks from the Gemini API."""
#     try:
#         # Step 1: Fetch real-time data (simulated for now)
#         realtime_data = maps_service.get_realtime_data(request_data['destination'])
        
#         # Step 2: Stream itinerary using the Gemini AI service
#         async for chunk in google_ai_service.stream_itinerary_with_ai(request_data):
#             yield chunk

#     except Exception as e:
#         yield json.dumps({"error": f"An error occurred: {e}"})

@app.post("/plan_trip")
async def plan_trip(request: TripRequest):
    """Generates a personalized itinerary as a real-time stream."""
    return StreamingResponse(itinerary_stream_generator(request.dict()), media_type="text/event-stream")

# Keep the other endpoints (`/update_itinerary`, `/book_trip`) unchanged
# ... (rest of main.py code) ...

# @app.post("/plan_trip", response_model=Itinerary)
# async def plan_trip(request: TripRequest):
#     """Generates a personalized itinerary based on user preferences."""
#     print("Received request to plan a trip.")

#     try:
#         # Step 1: Fetch real-time data (simulated for now)
#         realtime_data = maps_service.get_realtime_data(request.destination)
#         print(f"Simulated real-time data: {realtime_data}")
        
#         # Step 2: Generate itinerary using the real Gemini API
#         itinerary_items_data = await google_ai_service.generate_itinerary_with_ai(request.dict())
        
#         # Step 3: Process AI response and calculate total cost
#         total_cost = sum(item.get("cost_usd", 0.0) for item in itinerary_items_data)
        
#         # Step 4: Create a unique trip ID and save the itinerary
#         trip_id = str(uuid.uuid4())
#         itinerary_to_save = {
#             "trip_id": trip_id,
#             "destination": request.destination,
#             "duration_days": request.duration_days,
#             "total_cost": total_cost,
#             "items": itinerary_items_data,
#         }
        
#         firestore_service.save_itinerary(itinerary_to_save)
        
#         return itinerary_to_save
        
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/update_itinerary")
def update_itinerary(request: UpdateItineraryRequest):
    """Allows the user to make real-time adjustments to an existing itinerary."""
    print(f"Received request to update itinerary ID: {request.trip_id}")
    itinerary = firestore_services.get_itinerary(request.trip_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
        
    if firestore_services.update_itinerary(request.trip_id, request.updates):
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
    