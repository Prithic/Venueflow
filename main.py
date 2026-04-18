from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

# Load environment variables for security
load_dotenv()

app = FastAPI(
    title="VenueFlow API",
    description="Intelligent backend for stadium crowd coordination."
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Firebase Initialization (Security Focused) ---
DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
except Exception as e:
    print(f"Firebase Init Error: {e}")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def health_check():
    """
    Standard health check endpoint to verify system uptime.
    
    Returns:
        dict: Status and service name.
    """
    return {"status": "online", "service": "VenueFlow AI"}

@app.post("/chat")
async def handle_chat_query(request: ChatRequest):
    """
    Asynchronous endpoint to process attendee queries with live stadium context.
    Uses Firebase Realtime Database to fetch sub-second wait time metrics.
    
    Args:
        request (ChatRequest): The incoming message model.
        
    Returns:
        dict: A proactive, data-driven response for crowd coordination.
    """
    try:
        user_msg = request.message.lower()
        queues = db.reference('queues').get() or {}

        # Logic for proactive coordination
        if "gate" in user_msg:
            ga = queues.get("gate_a", 0)
            gb = queues.get("gate_b", 0)
            winner = "Gate A" if ga < gb else "Gate B"
            return {"reply": f"Coordination Alert: {winner} is currently the fastest entry point with a {min(ga, gb)} min wait."}

        return {"reply": "I'm your VenueFlow concierge. How can I help you navigate the stadium today?"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
