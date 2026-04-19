from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, db
import os
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="VenueFlow | Agentic AI", version="7.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://venueflow-945cc.web.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase
def get_db_ref():
    db_url = os.getenv("FIREBASE_DATABASE_URL")
    cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(cred_json)) if cred_json else None
            firebase_admin.initialize_app(cred, {'databaseURL': db_url})
        return db.reference('queues')
    except Exception:
        return None

db_ref = get_db_ref()

# --- Hybrid Reasoning Engine ---
class HybridReasoningEngine:
    """
    2-Layer Hybrid Intelligence Engine.
    Layer 1: Deterministic Utility Matrix (difflib + telemetry).
    Layer 2: Generative Context Synthesis (Gemini 1.5 Flash).
    """

    @staticmethod
    async def _call_llm(query: str, state: str) -> Optional[str]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = f"System State: {state}\nUser Query: {query}\nTask: Act as a stadium navigation expert. Compare zones and suggest the best one with trade-offs. Return a concise, premium response."

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json={"contents":[{"parts":[{"text":prompt}]}]})
                return res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return None

    @classmethod
    async def think(cls, query: str, state: Dict[str, Any]) -> tuple:
        if not state:
            return ("⚠️ Telemetry link offline. Proceed to Main Atrium for manual guidance.", "Null State Failover")

        import difflib
        ranked = []
        for zone_id, wait in state.items():
            if not isinstance(wait, (int, float)): continue
            
            # Semantic Similarity (0.0 to 1.0)
            similarity = difflib.SequenceMatcher(None, query.lower(), zone_id.replace('_', ' ')).ratio()
            # Throughput Utility (Higher wait = Lower utility)
            throughput = 1.0 / (wait + 1.0)
            
            ranked.append({
                "id": zone_id,
                "wait": wait,
                "utility": (similarity * 0.7) + (throughput * 0.3),
                "similarity": similarity
            })

        ranked.sort(key=lambda x: x['utility'], reverse=True)
        top = ranked[0]
        thought_trace = f"L1 Utility: {[ {r['id']: round(r['utility'], 2)} for r in ranked[:3] ]} | Confidence: {round(top['similarity'], 2)}"

        # Layer 2 Trigger (Low Confidence)
        if top['similarity'] < 0.65:
            llm_reply = await cls._call_llm(query, json.dumps(state))
            if llm_reply:
                return (llm_reply, f"{thought_trace} | L2 Booster Active")

        # Fallback to Deterministic Decision
        reply = f"Autonomous Decision: Directing to {top['id'].replace('_', ' ').title()}.\n\nReasoning: Optimal utility match ({top['wait']}m wait). "
        
        faster = [z for z in ranked[1:] if z['wait'] < top['wait']]
        if faster:
            reply += f"Note: While {faster[0]['id'].replace('_', ' ').title()} is faster ({faster[0]['wait']}m), {top['id'].replace('_', ' ').title()} is more relevant to your request."
            
        return (reply, thought_trace)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    thought_process: str
    timestamp: str

@app.get("/")
async def serve_ui():
    return FileResponse("index.html")

@app.get("/health")
async def health():
    """Health check for Render monitoring."""
    return {"status": "ok", "mode": "hybrid_v6"}

@app.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest) -> ChatResponse:
    """
    Handles autonomous reasoning queries by interfacing with the Hybrid Reasoning Engine.

    Args:
        request (ChatRequest): The incoming user message wrapped in a Pydantic model.

    Returns:
        ChatResponse: A structured response containing the agent's reply, 
                     the thought process trace, and a ISO-formatted timestamp.
    """
    state = db_ref.get() if db_ref else {}
    reply, thought = await HybridReasoningEngine.think(request.message, state or {})
    return ChatResponse(
        reply=reply, 
        thought_process=thought, 
        timestamp=datetime.now().isoformat()
    )
