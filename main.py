from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

# Load environment variables for secure credential management
load_dotenv()

app = FastAPI(
    title="VenueFlow API",
    description="Secure backend for stadium crowd coordination."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Firebase Initialization ---
DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
except Exception as e:
    print(f"Firebase initialization failed: {e}")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def health_check():
    """
    Standard health check endpoint to verify system uptime.
    
    Returns:
        dict: Uptime status and service identifier.
    """
    return {"status": "online", "service": "VenueFlow AI Concierge"}

@app.post("/chat")
async def chat_handler(request: ChatRequest):
    """
    Processes attendee queries by integrating real-time stadium congestion data.
    Implements proactive routing logic based on current wait times.
    
    Args:
        request (ChatRequest): Incoming user message model.
        
    Returns:
        dict: Context-aware AI recommendation.
    """
    try:
        user_msg = request.message.lower()
        queues = db.reference('queues').get() or {}

        # Core logic: If user asks about a location, provide live context and alternatives
        if "gate a" in user_msg:
            wait = queues.get("gate_a", 0)
            reply = f"Gate A currently has a {wait} min wait."
            if wait > 25:
                alt_wait = queues.get("gate_b", 0)
                reply += f" It's congested! Use Gate B instead for a {alt_wait} min entry."
            return {"reply": reply}

        if "gate b" in user_msg:
            wait = queues.get("gate_b", 0)
            reply = f"Gate B currently has a {wait} min wait."
            if wait > 25:
                alt_wait = queues.get("gate_a", 0)
                reply += f" It's busy! Gate A is faster at {alt_wait} mins."
            return {"reply": reply}

        return {"reply": "I am monitoring stadium flow. Ask me about gates or food wait times!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
