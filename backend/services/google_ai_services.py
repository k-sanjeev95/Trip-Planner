import os
import json
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("gemini key ",os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-pro-latest"

def create_gemini_prompt(request_data: Dict[str, Any]) -> str:
    """Generates a detailed prompt for the Gemini model."""
    interests_str = ", ".join(request_data.get("interests", []))
    # prompt = (
    #     f"You are a helpful travel planning assistant. Based on the user's preferences, "
    #     f"create a detailed and personalized {request_data['duration_days']}-day trip "
    #     f"itinerary for {request_data['destination']}. "
    #     f"The traveler has a {request_data['budget']} budget and is interested in {interests_str}. "
    #     f"Please provide the itinerary in a natural language, human-readable format. "
    #     f"Include suggestions for accommodation, transport, and experiences."
    # )
    
    prompt = (
    f"You are a creative and friendly travel planning assistant. "
    f"Design a {request_data['duration_days']}-day personalized itinerary for {request_data['destination']}. "
    f"The traveler has a budget of {request_data['budget']} and is especially interested in {interests_str}. "
    f"Make the itinerary engaging and exciting, written in a natural, story-like style that feels inspiring yet practical. "
    f"Include recommendations for cozy or unique accommodations, convenient transport options, must-try local foods, and memorable experiences. "
    f"Highlight a mix of famous attractions and hidden gems, and make sure each day feels balanced, enjoyable, and easy to follow. "
    f"Present it as if you’re a local friend guiding them on an unforgettable journey."
   )



    return prompt

async def stream_itinerary_with_ai(request_data: Dict[str, Any]):
    """
    Generates a trip itinerary using the Gemini API and streams the response.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = create_gemini_prompt(request_data)
        print("request data--------------", request_data)
        print("prompt ------------",prompt)
        
        print("Sending streaming request to Gemini API...")
        response_stream = await model.generate_content_async(
            prompt,
            stream=True
        )
        print(response_stream)
        
        async for chunk in response_stream:
            # Yield each text chunk as it arrives
            yield chunk.text

    except Exception as e:
        print(f"An unexpected error occurred during streaming: {e}")
        # Re-raise or handle as needed
        raise