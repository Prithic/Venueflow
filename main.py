from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
import firebase_admin
from firebase_admin import credentials, db
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="VenueFlow Autonomous Intelligence", version="3.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    thought_process: str
    timestamp: str

class ReasoningEngine:

    @staticmethod
    def think(user_query: str, state: Dict[str, Any]):
        gates = {k: v for k, v in state.items() if k.startswith('gate_')}
        sorted_gates = sorted(gates.items(), key=lambda x: x[1])

        best_gate_id, best_wait = sorted_gates[0]
        worst_gate_id, worst_wait = sorted_gates[-1]

        best_gate_name = best_gate_id.replace('_', ' ').title()
        worst_gate_name = worst_gate_id.replace('_', ' ').title()

        query = user_query.lower()

        thought = f"Analyzed {len(state)} zones. Best={best_gate_name} ({best_wait}m), Worst={worst_gate_name} ({worst_wait}m)"

        if any(x in query for x in ["gate", "entry", "fast", "wait"]):
            reply = f"Best route: {best_gate_name} ({best_wait} mins). Avoid {worst_gate_name} ({worst_wait} mins)."
        elif any(x in query for x in ["food", "eat"]):
            food_wait = state.get("food_court", 0)
            reply = f"Food Court wait: {food_wait} mins."
        else:
            reply = f"Smart suggestion: Use {best_gate_name} ({best_wait} mins)."

        return reply, thought

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat_handler(request: ChatRequest):
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
