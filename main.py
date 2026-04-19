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

# Agent Engine
class Agent:

    @staticmethod
    async def call_llm(query: str, state: Dict[str, Any]) -> Optional[str]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        prompt = f"""
You are VenueFlow AI.

STATE:
{json.dumps(state)}

USER:
{query}

TASK:
- Compare all zones
- Choose best option
- Explain tradeoffs

Return JSON:
{{"decision":"...","reason":"...","alternatives":[{{"zone":"...","note":"..."}}]}}
"""

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(url, json={"contents":[{"parts":[{"text":prompt}]}]})
                text = res.json()['candidates'][0]['content']['parts'][0]['text']
                return Agent.format(text)
        except Exception:
            return None

    @staticmethod
    def format(raw):
        try:
            data = json.loads(raw)
            alt = "\n".join([f"- {a['zone']}: {a['note']}" for a in data.get("alternatives",[])])
            return f"🎯 {data['decision']}\n💡 {data['reason']}\n{alt}"
        except:
            return raw

    @classmethod
    async def think(cls, query, state):
        if not state:
            return ("No data available","fallback")

        zones = [{"id":k,"wait":v} for k,v in state.items() if isinstance(v,(int,float))]

        llm = await cls.call_llm(query,{"zones":zones})
        if llm:
            return (llm,"LLM")

        best = min(zones,key=lambda x:x['wait'])
        return (f"Go to {best['id']} ({best['wait']} mins)","fallback")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    thought_process: str
    timestamp: str

@app.get("/")
def serve_ui():
    return FileResponse("index.html")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    state = db_ref.get() if db_ref else {}
    reply,thought = await Agent.think(request.message,state or {})
    return ChatResponse(reply=reply, thought_process=thought, timestamp=datetime.now().isoformat())
