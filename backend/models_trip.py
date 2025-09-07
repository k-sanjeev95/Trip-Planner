from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Union, Optional,Any
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

class UserCreate(BaseModel):
    """
    Pydantic model for validating user creation data.

    This model ensures that the data for a new user, such as
    email, password, and an optional full name, meets the required
    data types and formats before being processed.
    
    The `EmailStr` type from pydantic automatically handles email
    format validation.
    """
    full_name: Optional[str] = None
    email: EmailStr
    password: str
    

class ItineraryData(BaseModel):
    plan: Dict[str, Any]

