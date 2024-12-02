from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import aiohttp
import os
from dotenv import load_dotenv

# Načtení .env souboru
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")




# FastAPI aplikace
app = FastAPI()


# Pydantic model pro požadavek
class UserMessage(BaseModel):
    content: str

# Base URL pro OpenAI API
BASE_URL = "https://api.openai.com/v1"

# Funkce pro volání API a načítání JSON odpovědi
async def fetch_json(session, method, url, headers=None, json=None):
    async with session.request(method, url, headers=headers, json=json) as response:
        if response.status == 200:
            return await response.json()
        else:
            try:
                error = await response.json()
            except Exception:
                error = await response.text()
            raise HTTPException(status_code=response.status, detail=error)

# Vytvoření vlákna
async def create_thread(session, headers):
    thread_url = f"{BASE_URL}/threads"
    thread_response = await fetch_json(session, "POST", thread_url, headers)
    return thread_response["id"]

# Přidání zprávy do vlákna
async def add_message_to_thread(session, headers, thread_id, user_message):
    message_url = f"{BASE_URL}/threads/{thread_id}/messages"
    message_payload = {
        "role": "user",
        "content": user_message,
    }
    await fetch_json(session, "POST", message_url, headers, json=message_payload)

# Spuštění asistenta
async def run_assistant(session, headers, thread_id):
    run_url = f"{BASE_URL}/threads/{thread_id}/runs"
    run_payload = {"assistant_id": ASSISTANT_ID}
    run_response = await fetch_json(session, "POST", run_url, headers, json=run_payload)
    return run_response["id"]

# Kontrola stavu běhu asistenta
async def get_run_status(session, headers, thread_id, run_id):
    run_status_url = f"{BASE_URL}/threads/{thread_id}/runs/{run_id}"
    return await fetch_json(session, "GET", run_status_url, headers)

# Endpoint FastAPI
@app.post("/ask")
async def ask_assistant(user_message: UserMessage):
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2" 
        }

        # 1. Vytvoření vlákna
        try:
            thread_id = await create_thread(session, headers)
        except HTTPException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create thread: {e.detail}"
            )

        # 2. Přidání zprávy do vlákna
        try:
            await add_message_to_thread(session, headers, thread_id, user_message.content)
        except HTTPException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to add message to thread: {e.detail}"
            )

        # 3. Spuštění asistenta
        try:
            run_id = await run_assistant(session, headers, thread_id)
        except HTTPException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to start assistant: {e.detail}"
            )

        # 4. Čekání na dokončení běhu
        while True:
            try:
                run_status = await get_run_status(session, headers, thread_id, run_id)
                if run_status["status"] == "completed":
                    break
                elif run_status["status"] == "failed":
                    raise HTTPException(
                        status_code=500, detail=run_status.get("last_error", "Unknown error")
                    )
            except HTTPException as e:
                raise HTTPException(
                    status_code=500, detail=f"Failed to get run status: {e.detail}"
                )

        # 5. Získání zpráv
        messages_url = f"{BASE_URL}/threads/{thread_id}/messages"
        try:
            messages = await fetch_json(session, "GET", messages_url, headers)
        except HTTPException as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch messages: {e.detail}"
            )

        # Zpracování odpovědi
        response = [
            content["text"]["value"]
            for message in reversed(messages["data"])
            if message["role"] == "assistant"
            for content in message["content"]
            if content["type"] == "text"
        ]

        return {"response": response}



# Read the HTML file once at startup
with open("index.html") as f:
    html = f.read()

@app.get("/ui", response_class=HTMLResponse)
async def web_app() -> HTMLResponse:
    """
    Web App
    """
    return HTMLResponse(html)