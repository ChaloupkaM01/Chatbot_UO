import openai
import time
from dotenv import load_dotenv
import os

# Assummes you have a .env file containing OPENAI_API_KEY=<your key> in the same directory
load_dotenv()
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Initialize OpenAI Client
client = openai.Client()
my_assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

print(my_assistant)