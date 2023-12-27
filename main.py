from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel
import time
import os

load_dotenv()

API_KEY=os.getenv('OPEN_AI_API_KEY')
ORGANIZATION_ID=os.getenv('OPEN_AI_ORGANIZATION_ID')
ASSISTANT_ID=os.getenv('OPEN_AI_ASSISTANT_ID')

app = FastAPI()
client = OpenAI(api_key=API_KEY, organization=ORGANIZATION_ID)

@app.get("/")
def read_root():
    return {"status": "ok"}

class Chat(BaseModel):
    message: str

@app.post("/chat")
async def chat(data: Chat):
    thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=data.message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
    )
    
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    run_status = None 
    while run_status != "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        run_status = run.status
        time.sleep(2)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
        
    return {"response": messages.data[0].content[0].text.value  }
