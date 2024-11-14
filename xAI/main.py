from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
XAI_API_KEY = os.getenv("X_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Define a Pydantic model for the request body
class ChatRequest(BaseModel):
    prompt: str

# Function to interact with X.AI API using httpx
async def get_xai_response(prompt: str) -> str:
    """
    Sends a request to the X.AI API with the provided prompt and retrieves the response.

    Args:
        prompt (str): The user input prompt to send to the X.AI API.

    Returns:
        str: The response content from the X.AI API.
    """
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {XAI_API_KEY}"
    }
    data = {
        "messages": [
            {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."},
            {"role": "user", "content": prompt}
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for HTTP errors
            response_data = response.json()
            return response_data['choices'][0]['message']['content']

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error contacting X.AI API: {str(e)}")

# Endpoint to handle requests and return X.AI responses
@app.post("/ask_grok/")
async def ask_grok(request: ChatRequest):
    """
    Endpoint to handle requests and retrieve responses from the X.AI API.

    Args:
        request (ChatRequest): The incoming request with a user prompt.

    Returns:
        dict: A dictionary with the response from the X.AI API.
    """
    if not XAI_API_KEY:
        raise HTTPException(status_code=500, detail="X.AI API key not configured")

    try:
        # Call the function to get the response from X.AI API
        response_content = await get_xai_response(request.prompt)
        return {"response": response_content}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
