import os
import json
import google.generativeai as genai
from typing import Dict, Any,List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
print("gemini key ",os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "gemini-1.5-pro-latest"

def create_gemini_prompt(travel_params: Dict[str, Any], search_info: str) -> str:
    """Generates a detailed, markdown-formatted prompt for the Gemini AI."""
    
    prompt = f"""
Create a detailed travel itinerary in proper markdown format with clear sections and bullet points. Use the following structure:

# {travel_params['destination']} Travel Plan

## Destination Overview
- Brief introduction to {travel_params['destination']}
- Best time to visit
- Local currency and basic phrases

## Real-Time Trip Context
- **Current Weather:** {travel_params.get('weather_info', 'Not available.')}
- **Upcoming Events:** {travel_params.get('events_info', 'No upcoming events found.')}
- **Trip Start Date:** {travel_params['start_date']}

## Before You Go
- Visa requirements
- Health and safety tips
- Packing recommendations
- Transportation to/from airport

## Accommodations
- Recommended places to stay based on {travel_params['accommodation']} preference
- Location advantages
- Approximate rates
- Booking tips

## Day-by-Day Itinerary

### Day 1
- Morning activities
  * Specific locations
  * Timing
  * Tips
- Afternoon activities
  * Detailed stops
  * Recommendations
- Evening activities
  * Dinner options
  * Entertainment

[Continue similar format for each day for a total of {travel_params['duration_days']} days]

## Local Transportation
- Getting around options
- Costs
- Tips and recommendations

## Dining Guide
- Must-try local dishes
- Restaurant recommendations
  * Budget options
  * Mid-range choices
  * Special experiences
- Food safety tips

## Budget Breakdown
- Daily estimates
  * Accommodation: {travel_params['accommodation']}
  * Meals
  * Activities
  * Transportation
- Money-saving tips
- Total budget range

## Local Tips
- Cultural etiquette
- Safety advice
- Common phrases
- Best photo spots

Use the following details:
- Duration: {travel_params['duration_days']} days
- Group size: {travel_params['people']} people
- Accommodation preference: {travel_params['accommodation']}
- Activities: {travel_params['activities']}
- theme: {travel_params['theme']}
- Budget level: {travel_params.get('budget', 'Not specified')}

Additional research information:
{search_info}

IMPORTANT FORMATTING RULES:
1. Use proper markdown headings (# for main title, ## for sections, ### for subsections)
2. Use bullet points (-) for all lists
3. Use nested bullet points (*) for sub-items
4. Add blank lines between sections
5. Keep content organized and easy to read
6. Use bold (**) for important information
7. Include specific details and recommendations
"""
    return prompt

async def stream_itinerary_with_ai(request_data: Dict[str, Any], search_info: str):
    """
    Generates a trip itinerary using the Gemini API and streams the response.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = create_gemini_prompt(request_data, search_info)
        
        print("Sending streaming request to Gemini API with detailed prompt...")
        response_stream = await model.generate_content_async(
            prompt,
            stream=True
        )
        
        async for chunk in response_stream:
            yield chunk.text

    except Exception as e:
        print(f"An unexpected error occurred during streaming: {e}")
        raise