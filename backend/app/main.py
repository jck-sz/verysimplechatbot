import os
import boto3
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

# --- Load secret from Secrets Manager ---
def get_openai_api_key():
    secret_name = os.getenv("OPENAI_SECRET_NAME", "OpenAI_API_Key")
    region_name = os.getenv("AWS_REGION", "eu-north-1")

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    secret = json.loads(get_secret_value_response["SecretString"])
    return secret["OPENAI_API_KEY"]

# Get the API key from Secrets Manager
openai_api_key = get_openai_api_key()
client = OpenAI(api_key=openai_api_key)

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

from mangum import Mangum

handler = Mangum(app)
