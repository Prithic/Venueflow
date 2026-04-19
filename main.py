from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import firebase_admin
from firebase_admin import credentials, db
import os
import httpx
import json
import difflib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="VenueFlow | Hybrid Reasoning Engine",
    version="6.0.0",
    description="2-Layer Hybrid Intelligence: Deterministic Utility + LLM Synthesis."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://venueflow-945cc.web.app", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Persistence Layer ---
def get_db_ref() -> Optional[db.Reference]:
    """
    Initializes and returns a secure Firebase reference.
    
    Args:
        None
    Returns:
        Optional[db.Reference]: Database reference or None.
    Raises:
        None
    """
    db_url = os.getenv("FIREBASE_DATABASE_URL") or "https://venueflow-945cc-default-rtdb.asia-southeast1.firebasedatabase.app"
    cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    
    try:
        if not firebase_admin._apps:
            if cred_json:
                cred = credentials.Certificate(json.loads(cred_json))
                firebase_admin.initialize_app(cred, {'databaseURL': db_url})
            elif os.path.exists("serviceAccountKey.json"):
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred, {'databaseURL': db_url})
            else:
                # Fallback to default auth if possible
                firebase_admin.initialize_app(options={'databaseURL': db_url})
        return db.reference('queues')
    except Exception:
        return None

db_ref = get_db_ref()

# --- Hybrid Reasoning Engine ---
class HybridReasoningEngine:
    """
    Advanced 2-Layer Reasoning Engine combining semantic utility and LLM-backed synthesis.
    """

    CONFIDENCE_THRESHOLD = 0.65

    @staticmethod
    def _get_similarity(query: str, target: str) -> float:
        """
        Calculates normalized string similarity score.
        
        Args:
            query (str): User query.
            target (str): Zone identifier.
        Returns:
            float: Similarity score (0-1).
        """
        target_norm = target.replace("_", " ").lower()
        return difflib.SequenceMatcher(None, query.lower(), target_norm).ratio()

    @staticmethod
    async def _call_llm(query: str, state: Dict[str, Any]) -> Optional[str]:
        """
        Optional Layer 2: LLM Reasoning Booster.
        
        Args:
            query (str): User query.
            state (Dict[str, Any]): Full system state.
        Returns:
            Optional[str]: LLM generated response or None.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = f"""
        System State: {json.dumps(state)}
        User Query: "{query}"
        
        Role: VenueFlow Oracle.
        Task: Provide a context-aware routing decision based on the state.
        Requirement: Be concise, empathetic, and data-driven.
        """
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                return res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return None

    @classmethod
    async def think(cls, user_query: str, state: Dict[str, Any]) -> tuple:
        """
        Executes hybrid reasoning: Deterministic utility first, then optional LLM booster.
        
        Args:
            user_query (str): The raw user query.
            state (Dict[str, Any]): Real-time telemetry dictionary.
        Returns:
            tuple: (reply, thought_process)
        """
        if not state:
            return ("Telemetry link offline. Reverting to safe-state defaults.", "Deterministic Fallback: Null State")

        # Layer 1: Deterministic Utility Engine
        zones = {k: v for k, v in state.items() if isinstance(v, (int, float))}
        scores = []
        
        for zone, wait in zones.items():
            similarity = cls._get_similarity(user_query, zone)
            # Utility formula: Similarity + Normalized Inverse Wait Time
            utility = similarity + (1.0 / (wait + 1.0))
            scores.append({"id": zone, "utility": utility, "wait": wait})

        ranked = sorted(scores, key=lambda x: x["utility"], reverse=True)
        top = ranked[0]
        
        # Calculate Confidence Score (0-1)
        total_utility = sum(s["utility"] for s in scores) or 1.0
        confidence = top["utility"] / total_utility
        
        thought_trace = f"L1 Utility: {[{s['id']: round(s['utility'], 2)} for s in ranked]} | Confidence: {round(confidence, 2)}"

        # Layer 2: LLM Booster (Optional / Triggered by low confidence)
        if confidence < cls.CONFIDENCE_THRESHOLD:
            llm_reply = await cls._call_llm(user_query, state)
            if llm_reply:
                return (llm_reply, f"{thought_trace} | L2 Booster Active")

        # Fallback to Deterministic Decision (Comparative Reasoning)
        reply = (
            f"Autonomous Decision: Directing to {top['id'].replace('_', ' ').title()}.\n\n"
            f"Reasoning: Optimal utility match ({top['wait']}m wait). "
        )
        
        # Comparative Logic: Check if another zone is significantly faster
        faster_zones = [z for z in ranked[1:] if z['wait'] < top['wait']]
        if faster_zones:
            best_alt = faster_zones[0]
            reply += f"Note: While {best_alt['id'].replace('_', ' ').title()} is faster ({best_alt['wait']}m), {top['id'].replace('_', ' ').title()} offers higher semantic relevance to your query."
        else:
            reply += "Semantic anchors and throughput are currently balanced for this sector."
            
        return (reply, thought_trace)

# --- API Layer ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    thought_process: str
    timestamp: str

@app.get("/")
def serve_ui():
    """Serves the primary intelligence dashboard."""
    return FileResponse("index.html")

@app.get("/health")
def health():
    """
    Verifies the system operational status and engine version.
    
    Args:
        None
    Returns:
        dict: Status message and operational mode.
    Raises:
        None
    """
    return {"status": "ok", "mode": "hybrid_v6"}

@app.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    """
    Processes user queries through the 2-layer hybrid reasoning engine.
    
    Args:
        request (ChatRequest): The incoming user message payload.
    Returns:
        ChatResponse: Synthesized reply, internal thought process, and timestamp.
    Raises:
        None: Errors are handled gracefully with a resilience fallback.
    """
    try:
        current_state = {}
        if db_ref:
            try:
                current_state = db_ref.get() or {}
            except Exception: pass
            
        reply, thought = await HybridReasoningEngine.think(request.message, current_state)
        
        return ChatResponse(
            reply=reply,
            thought_process=thought,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return ChatResponse(
            reply="The reasoning layer is currently recalibrating.",
            thought_process=f"Resilience override: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

if __name__ == "__main__":
    import uvicorn
    # Render provides PORT via environment variable
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
