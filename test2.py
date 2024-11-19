from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OPENAI_API_KEY = os.getenv("API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

async def create_thread():
    url = f"https://api.openai.com/v1/assistants/{ASSISTANT_ID}/threads"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'title': 'New Thread'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as response:
                response.raise_for_status()
                json_response = await response.json()
                return json_response.get('id')
        except aiohttp.ClientError:
            return None

async def get_assistant_response(thread_id, user_message):
    url = f"https://api.openai.com/v1/assistants/{ASSISTANT_ID}/threads/{thread_id}/messages"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'messages': [
            {'role': 'user', 'content': user_message}
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as response:
                response.raise_for_status()
                json_response = await response.json()
                return json_response['choices'][0]['message']['content']
        except aiohttp.ClientError:
            return "An error occurred while getting a response from the assistant."

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get('message')
    if not user_message:
        raise HTTPException(status_code=400, detail="User message not provided.")

    thread_id = await create_thread()
    if not thread_id:
        raise HTTPException(status_code=500, detail="Failed to create thread.")

    assistant_response = await get_assistant_response(thread_id, user_message)
    return JSONResponse({"response": assistant_response})
