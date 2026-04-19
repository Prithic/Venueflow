from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, Tuple
import firebase_admin
from firebase_admin import credentials, db
import os
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="VenueFlow | Agentic AI", version="7.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://venueflow-945cc.web.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_ref() -> Optional[Any]:
    """
    Initialize Firebase connection and return database reference.

    Returns:
        Optional[Any]: Firebase database reference or None if initialization fails.
    """
    db_url: Optional[str] = os.getenv("FIREBASE_DATABASE_URL")
    cred_json: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(cred_json)) if cred_json else None
            firebase_admin.initialize_app(cred, {'databaseURL': db_url})
        return db.reference('queues')
    except Exception:
        return None


db_ref: Optional[Any] = get_db_ref()


class HybridReasoningEngine:
    """
    Hybrid AI Engine combining deterministic utility scoring and LLM reasoning.
    """

    @staticmethod
    async def _call_llm(query: str, state: str) -> Optional[str]:
        """
        Calls Gemini LLM with system state and user query.

        Args:
            query (str): User input query.
            state (str): Serialized system state.

        Returns:
            Optional[str]: Generated response from LLM or None on failure.
        """
        api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        url: str = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt: str = f"System State: {state}\nUser Query: {query}\nTask: Compare all zones and give optimal recommendation with tradeoffs."

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json={"contents":[{"parts":[{"text":prompt}]}]})
                return res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return None

    @classmethod
    async def think(cls, query: str, state: Dict[str, Any]) -> Tuple[str, str]:
        """
        Core reasoning function combining deterministic and LLM logic.

        Args:
            query (str): User query.
            state (Dict[str, Any]): Live telemetry data.

        Returns:
            Tuple[str, str]: AI response and reasoning trace.
        """
        if not state:
            return ("⚠️ Telemetry offline. Proceed to Main Atrium.", "Null State")

        import difflib
        ranked = []
        for zone_id, wait in state.items():
            if not isinstance(wait, (int, float)):
                continue

            similarity: float = difflib.SequenceMatcher(None, query.lower(), zone_id.replace('_', ' ')).ratio()
            throughput: float = 1.0 / (wait + 1.0)

            ranked.append({
                "id": zone_id,
                "wait": wait,
                "utility": (similarity * 0.7) + (throughput * 0.3),
                "similarity": similarity
            })

        ranked.sort(key=lambda x: x['utility'], reverse=True)
        top = ranked[0]

        if top['similarity'] < 0.65:
            llm_reply: Optional[str] = await cls._call_llm(query, json.dumps(state))
            if llm_reply:
                return (llm_reply, "LLM Boost")

        return (f"Go to {top['id']} ({top['wait']} mins)", "Deterministic")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    thought_process: str
    timestamp: str


@app.get("/")
async def serve_ui() -> FileResponse:
    return FileResponse("index.html")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest) -> ChatResponse:
    state: Dict[str, Any] = db_ref.get() if db_ref else {}
    reply, thought = await HybridReasoningEngine.think(request.message, state or {})
    return ChatResponse(reply=reply, thought_process=thought, timestamp=datetime.now().isoformat())
