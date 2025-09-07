from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional
from datetime import date

class TripRequest(BaseModel):
    destination: str
    duration_days: int
    budget: str
    start_date: date = Field(..., description="The start date of the trip (YYYY-MM-DD).")
    theme: List[str]
    people: Optional[int] = 1  # New field
    accommodation: Optional[str] = "mid-range hotel" # New field
    activities: Optional[List[str]] = ["sightseeing", "local food"] # New field

class ItineraryItem(BaseModel):
    title: str
    description: str
    location: str
    duration_hours: int
    cost_usd: float
    type: str

class Itinerary(BaseModel):
    trip_id: str
    destination: str
    duration_days: int
    total_cost: float
    items: List[ItineraryItem]

class UpdateItineraryRequest(BaseModel):
    trip_id: str
    updates: Dict[str, Union[str, float]]

class BookingRequest(BaseModel):
    trip_id: str
    payment_token: str
    total_amount: float