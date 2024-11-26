from fastapi import FastAPI, HTTPException
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
OPENAI_API_KEY = os.getenv("API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

@app.post("/ask_chatgpt/")
async def ask_chatgpt(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {
        #"model": "gpt-4o-mini",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 100
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            #"https://api.openai.com/v1/chat/completions", headers=headers, json=data
            f"https://api.openai.com/v1/assistants/{ASSISTANT_ID}", headers=headers, json=data
        ) as response:
            if response.status != 200:
                error_detail = await response.text()
                raise HTTPException(status_code=response.status, detail=error_detail)

            result = await response.json()
            return {
                "response": result['choices'][0]['message']['content']
            }
