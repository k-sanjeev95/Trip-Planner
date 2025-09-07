import googlemaps
import requests
import os
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# Initialize API clients from .env


def get_weather_data(destination: str):
    """
    Fetches weather data for an Indian city using the indianapi.in service.
    This API requires an x-api-key in the header.
    """
    api_key = os.getenv('INDIAN_API_KEY')
    api_endpoint = 'https://weather.indianapi.in/india/weather'
    
    headers = {
        'x-api-key': api_key,
    }
    params = {
        'city': destination
    }
    
    try:
        response = requests.get(api_endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Simplified data extraction. The actual response will have more fields.
        weather_info = f"{data.get('description', 'N/A')}, Temperature: {data.get('temp', 'N/A')}°C"
        return f"Current weather in {destination}: {weather_info}"
    
    except Exception as e:
        print(f"Error fetching weather data from Indian API: {e}")
        return "Weather data from Indian API unavailable."

def get_local_events(destination: str, start_date: date):
    """
    Fetches local events from Eventbrite using a personal OAuth token.
    The token is sent in the Authorization header.
    """
    api_key = os.getenv('EVENTBRITE_API_KEY')
    api_endpoint = "https://www.eventbriteapi.com/v3/events/search/"
    
    # Eventbrite API uses ISO 8601 for time.
    start_datetime = start_date.isoformat() + 'T00:00:00Z'
    
    params = {
        'q': 'events',
        'location.address': destination,
        'start_date.range_start': start_datetime
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(api_endpoint, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        events = [
            f"{event['name']['text']} on {event['start']['local'].split('T')[0]}"
            for event in data.get('events', [])[:3]
        ]
        
        return "Upcoming events: " + ", ".join(events) if events else "No major events found."
    except Exception as e:
        print(f"Error fetching events data from Eventbrite: {e}")
        return "Events data unavailable."

weather_data= get_weather_data("pune")
print(weather_data)