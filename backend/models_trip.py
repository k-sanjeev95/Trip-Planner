from pydantic import BaseModel
from typing import List, Dict, Union

class TripRequest(BaseModel):
    destination: str
    duration_days: int
    budget: str
    interests: List[str]

class ItineraryItem(BaseModel):
    title: str
    description: str
    location: str
    duration_hours: int
    cost_usd: float
    type: str # e.g., "activity", "food", "transport", "accommodation"

class Itinerary(BaseModel):
    trip_id: str
    destination: str
    duration_days: int
    total_cost: float
    items: List[ItineraryItem]

class UpdateItineraryRequest(BaseModel):
    trip_id: str
    updates: Dict[str, Union[str, float]] # A flexible dictionary for various updates

class BookingRequest(BaseModel):
    trip_id: str
    payment_token: str # A mock payment token
    total_amount: float