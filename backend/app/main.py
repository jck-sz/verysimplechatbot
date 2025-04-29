import os
import json
import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from mangum import Mangum  # Required for AWS Lambda

# --- Load secret from Secrets Manager ---
def get_openai_api_key():
    secret_name = os.getenv("OPENAI_SECRET_NAME", "OpenAI_API_Key")
    region_name = os.getenv("AWS_REGION", "eu-north-1")

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(get_secret_value_response["SecretString"])
    return secret["OPENAI_API_KEY"]

# --- Initialize OpenAI client ---
openai_api_key = get_openai_api_key()
client = OpenAI(api_key=openai_api_key)

# --- FastAPI App ---
app = FastAPI()

# --- CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic model ---
class ChatRequest(BaseModel):
    message: str

# --- System prompt ---
SYSTEM_PROMPT = """
You are a helpful, wise assistant. Stay professional, calm, and insightful.
Never admit you are an AI.
"""

# --- Main chat endpoint ---
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return {"response": response.choices[0].message.content.strip()}
    except Exception as e:
        print(f"Error in /chat: {e}")
        return {"error": str(e)}

# --- Optional health check endpoint ---
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Lambda FastAPI backend is running."}

# --- Mangum Lambda handler ---
handler = Mangum(app)
