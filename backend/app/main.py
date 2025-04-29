from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (so frontend can talk to backend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WARNING: "*" is OK for dev but tighten in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define system prompt for the chatbot
SYSTEM_PROMPT = """
You are a helpful, wise assistant. Stay professional, calm, and insightful.
Never admit you are an AI.
"""

@app.post("/chat")
async def chat(request: Request):
    """
    Chat endpoint: accepts {"message": "user text"} and returns AI response.
    """
    try:
        data = await request.json()
        user_message = data.get("message")

        if not user_message:
            return {"error": "No message provided."}

        # Call OpenAI API
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
