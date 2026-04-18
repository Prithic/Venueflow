from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import firebase_admin
from firebase_admin import credentials, db
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="VenueFlow Autonomous Intelligence", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

# Production-safe Firebase initialization
if not os.path.exists(SERVICE_ACCOUNT):
    raise RuntimeError("Firebase service account file missing")

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
except Exception as e:
    raise RuntimeError(f"Firebase init failed: {str(e)}")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    thought_process: str
    timestamp: str


class ReasoningEngine:
    """
    Autonomous reasoning engine performing full-state comparative analysis.
    """

    @staticmethod
    def think(user_query: str, state: Dict[str, Any]):
        """
        Performs full-state reasoning without keyword dependency.

        Args:
            user_query (str): User input query
            state (Dict[str, Any]): Firebase queue data

        Returns:
            tuple: reply, reasoning trace
        """

        if not state:
            return "No live data available.", "Empty state detected"

        zones = {k: v for k, v in state.items() if isinstance(v, (int, float))}

        sorted_zones = sorted(zones.items(), key=lambda x: x[1])

        best_zone, best_time = sorted_zones[0]
        worst_zone, worst_time = sorted_zones[-1]

        avg_wait = sum(zones.values()) / len(zones)

        def fmt(z):
            return z.replace("_", " ").title()

        thought = (
            f"Analyzed {len(zones)} zones | "
            f"Best={fmt(best_zone)}({best_time}) | "
            f"Worst={fmt(worst_zone)}({worst_time}) | "
            f"Avg={round(avg_wait,1)}"
        )

        if best_time < avg_wait * 0.7:
            strategy = f"Optimal flow at {fmt(best_zone)}."
        elif worst_time > avg_wait * 1.5:
            strategy = f"Heavy congestion at {fmt(worst_zone)}."
        else:
            strategy = "Balanced load across zones."

        reply = (
            f"AI Routing Decision:\n"
            f"Best: {fmt(best_zone)} ({best_time} mins)\n"
            f"Worst: {fmt(worst_zone)} ({worst_time} mins)\n"
            f"{strategy}"
        )

        return reply, thought


@app.get("/health")
def health():
    """
    Health check endpoint.

    Returns:
        dict: system status
    """
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat_handler(request: ChatRequest):
    """
    Main chat endpoint executing reasoning engine.

    Args:
        request (ChatRequest): user request

    Returns:
        ChatResponse: AI output
    """
    try:
        queues = db.reference('queues').get() or {}
        reply, thought = ReasoningEngine.think(request.message, queues)

        return ChatResponse(
            reply=reply,
            thought_process=thought,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
