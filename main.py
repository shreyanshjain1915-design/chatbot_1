from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import time

from chatbot import chatbot_logic

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # allows Netlify + any frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session store ────────────────────────────────────────────────
sessions: dict = {}

def get_session(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {
            "chat_history": [],
            "mode": None,
            "business_type": None,
            "website_goal":  None,
            "pages_needed":  None,
            "tech_stack":    None,
            "design_style":  None,
            "seo_step": 0,
            "seo_data": {},
            "gen_step": 0,
            "gen_data": {},
        }
    return sessions[session_id]


class Message(BaseModel):
    session_id: str
    message: str = ""


@app.post("/chat")
@app.post("/chat/")
def chat(msg: Message):
    session_id   = msg.session_id
    user_message = msg.message.strip()
    if not user_message:
        return {"reply": "Please type a message."}
    session = get_session(session_id)
    reply   = chatbot_logic(session, user_message)
    return {"reply": reply}


@app.post("/stream")
def stream(msg: Message):
    def generate():
        result = chat(msg)
        reply  = result["reply"]
        for char in reply:
            yield char
            time.sleep(0.008)
    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/reset/{session_id}")
def reset_chat(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "Chat reset successfully"}


@app.get("/")
def home():
    return {"message": "SiteBot AI — 3-mode API running ✓"}