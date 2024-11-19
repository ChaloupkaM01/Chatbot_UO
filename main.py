from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OPENAI_API_KEY = os.getenv("API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
#OPENAI_API_URL = f"https://api.openai.com/v1/assistants/{ASSISTANT_ID}/messages"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

@app.post("/send-message")
async def send_message_to_assistant(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "input": {"text": prompt}
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENAI_API_URL, json=payload, headers=headers) as response:
            if response.status != 200:
                detail = await response.text()
                raise HTTPException(status_code=response.status, detail=detail)
            data = await response.json()

    return {"response": data}
