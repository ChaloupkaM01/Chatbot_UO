from fastapi import FastAPI, HTTPException
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
OPENAI_API_KEY = os.getenv("API_KEY")

@app.get("/hello")
async def hello_endpoint(name: str = "World"):
    return {"message": f"Hello, {name}!"}

@app.post("/ask_chatgpt/")
async def ask_chatgpt(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 100
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=data
        ) as response:
            if response.status != 200:
                error_detail = await response.text()
                raise HTTPException(status_code=response.status, detail=error_detail)

            result = await response.json()
            return {
                "response": result['choices'][0]['message']['content']
            }