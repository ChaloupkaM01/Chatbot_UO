import aiohttp
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# API klíč a ID asistenta
OPENAI_API_KEY = os.getenv("API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
OPENAI_API_URL = f"https://api.openai.com/v1/assistants/{ASSISTANT_ID}/messages"

# Funkce pro komunikaci s OpenAI API
async def send_query_to_openai(thread_id: str, message: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "thread": thread_id,  # Správa vlákna pomocí thread_id
        "messages": [{"role": "user", "content": message}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENAI_API_URL, headers=headers, json=payload) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# Endpoint pro správu dotazů
@app.post("/query")
async def query_openai(request: Request):
    try:
        body = await request.json()
        thread_id = body.get("thread_id")
        message = body.get("message")
        if not thread_id or not message:
            raise HTTPException(status_code=400, detail="Missing 'thread_id' or 'message' in request body.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        response = await send_query_to_openai(thread_id, message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
