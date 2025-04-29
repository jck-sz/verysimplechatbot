from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# FastAPI app
app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a Pydantic model for input validation
class ChatRequest(BaseModel):
    message: str

SYSTEM_PROMPT = """
You are a helpful, wise assistant. Stay professional, calm, and insightful.
Never admit you are an AI.
"""

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # request.message is automatically validated and parsed
        user_message = request.message

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500,
        )

        bot_reply = response.choices[0].message.content.strip()
        return {"response": bot_reply}

    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return {"error": str(e)}
