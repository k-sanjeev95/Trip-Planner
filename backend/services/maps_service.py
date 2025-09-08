# import googlemaps
# import requests
# import os
# from datetime import date, timedelta
# from dotenv import load_dotenv
# from tavily import TavilyClient

# load_dotenv()

# # Initialize API clients from .env
# gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))

# def get_location_coordinates(destination: str):
#     """Geocodes a destination to get its latitude and longitude."""
#     try:
#         geocode_result = gmaps.geocode(destination)
#         if geocode_result:
#             location_coords = geocode_result[0]['geometry']['location']
#             return location_coords['lat'], location_coords['lng']
#     except Exception as e:
#         print(f"Error geocoding location: {e}")
#     return None, None

# def get_weather_data(destination: str):
#     """
#     Fetches weather data using the WeatherAPI.com service, including the aqi=no parameter.
#     """
#     api_key = os.getenv('WEATHER_API_KEY')
#     api_endpoint = "https://api.weatherapi.com/v1/current.json"
    
#     params = {
#         "key": api_key,
#         "q": destination,
#         "aqi": "no" # Exclude air quality data
#     }
    
#     try:
#         response = requests.get(api_endpoint, params=params)
#         response.raise_for_status()
#         data = response.json()
        
#         # Extract relevant weather information
#         temp_c = data["current"]["temp_c"]
#         condition_text = data["current"]["condition"]["text"]
        
#         weather_info = f"{condition_text}, Temperature: {temp_c}°C"
#         return f"Current weather in {destination}: {weather_info}"
    
#     except requests.exceptions.HTTPError as err:
#         print(f"HTTP error occurred: {err}")
#         return "Weather data unavailable."
#     except Exception as e:
#         print(f"Error fetching weather data from WeatherAPI.com: {e}")
#         return "Weather data from WeatherAPI.com unavailable."


# def get_events_with_tavily(destination: str, start_date: date):
#     """
#     Fetches events by performing a live search using the Tavily API.
#     """
#     api_key = os.getenv('TAVILY_API_KEY')
#     client = TavilyClient(api_key=api_key)
    
#     # Construct a dynamic search query
#     query = f"Upcoming events and festivals in {destination} in {start_date.strftime('%B %Y')}"
    
#     try:
#         response = client.search(
#             query=query,
#             search_depth='basic',
#             max_results=5
#         )
        
#         event_snippets = [
#             f"Title: {result.get('title', 'No Title')}\nURL: {result.get('url', 'No URL')}\nSnippet: {result.get('content', 'No content')}"
#             for result in response.get('results', [])
#         ]
        
#         return "\n\n".join(event_snippets) if event_snippets else "No relevant events found via Tavily search."
    
#     except Exception as e:
#         print(f"Error fetching events from Tavily: {e}")
#         return "Events data from Tavily unavailable."

# def get_realtime_data(destination: str, start_date: date):
#     """Aggregates data from multiple sources."""
#     # We don't need coordinates for these APIs, but it's good practice to keep the
#     # geocoding function for other uses.
    
#     # Fetch data from each source
#     weather_info = get_weather_data(destination)
#     events_info = get_events_with_tavily(destination, start_date)
    
#     # Return a structured dictionary
#     print(weather_info)
#     print(events_info)
#     return {
#         "destination": destination,
#         "weather_info": weather_info,
#         "events_info": events_info
#     }

import os
import asyncio
import googlemaps
import aiohttp
from datetime import date
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables from .env file
load_dotenv()

# Initialize API clients
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
gmaps_client = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))

async def get_location_coordinates(destination: str):
    """Geocodes a destination to get its latitude and longitude asynchronously."""
    try:
        geocode_result = await asyncio.to_thread(gmaps_client.geocode, destination)
        if geocode_result:
            location_coords = geocode_result[0]['geometry']['location']
            return location_coords['lat'], location_coords['lng']
    except Exception as e:
        print(f"Error geocoding location: {e}")
    return None, None

async def get_weather_data(session: aiohttp.ClientSession, destination: str):
    """
    Fetches weather data using aiohttp for asynchronous requests.
    """
    api_key = os.getenv('WEATHER_API_KEY')
    api_endpoint = "https://api.weatherapi.com/v1/current.json"
    
    params = {
        "key": api_key,
        "q": destination,
        "aqi": "no"
    }
    
    try:
        async with session.get(api_endpoint, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            
            temp_c = data["current"]["temp_c"]
            condition_text = data["current"]["condition"]["text"]
            
            weather_info = f"{condition_text}, Temperature: {temp_c}°C"
            return f"Current weather in {destination}: {weather_info}"
    
    except aiohttp.ClientError as err:
        print(f"HTTP error occurred while fetching weather data: {err}")
        return "Weather data unavailable."
    except Exception as e:
        print(f"Error fetching weather data from WeatherAPI.com: {e}")
        return "Weather data from WeatherAPI.com unavailable."


async def validate_event_with_gmaps(event_title: str, destination: str):
    """
    Validates an event by searching for it on Google Maps.
    """
    try:
        places_result = await asyncio.to_thread(
            gmaps_client.places,
            query=f"event {event_title} in {destination}",
            type="event"
        )
        if places_result and places_result.get('results'):
            print(f"Event '{event_title}' validated via Google Maps.")
            return True
    except Exception as e:
        print(f"Google Maps validation for '{event_title}' failed: {e}")
    return False

async def get_events_with_tavily(destination: str, start_date: date):
    """
    Fetches and validates events by performing a live search using the Tavily API.
    """
    query = f"Upcoming events, festivals, and concerts in {destination} from {start_date.strftime('%Y-%m-%d')} for official sources."
    
    try:
        response = await asyncio.to_thread(
            tavily_client.search,
            query=query,
            search_depth='basic',
            max_results=5
        )
        
        event_snippets = [
            result.get('content', 'No content')
            for result in response.get('results', [])
        ]
        
        validated_events = []
        for snippet in event_snippets:
            title = snippet.split('\n')[0].strip() if '\n' in snippet else snippet[:50]
            
            is_valid = await validate_event_with_gmaps(title, destination)
            
            if is_valid:
                validated_events.append({
                    "title": title,
                    "snippet": snippet,
                    "validated": True
                })
        
        if not validated_events:
            return "No verified, upcoming events found. The AI can still create an itinerary based on other interests."
        
        formatted_events = "\n\n".join([
            f"Title: {event['title']}\nSnippet: {event['snippet']}"
            for event in validated_events
        ])
        
        return f"Verified Upcoming Events:\n{formatted_events}"
    
    except Exception as e:
        print(f"Error fetching/validating events from Tavily: {e}")
        return "Events data from Tavily is unavailable or could not be verified."

async def get_realtime_data(destination: str, start_date: date):
    """
    Aggregates and concurrently fetches data from multiple sources.
    """
    async with aiohttp.ClientSession() as session:
        # Run API calls in parallel to improve performance
        weather_task = get_weather_data(session, destination)
        events_task = get_events_with_tavily(destination, start_date)
        
        weather_info, events_info = await asyncio.gather(weather_task, events_task)
        
    return {
        "destination": destination,
        "weather_info": weather_info,
        "events_info": events_info
    }


