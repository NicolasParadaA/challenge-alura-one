"""FastAPI backend for BimBam Buy RAG Agent.

Provides POST /chat and GET /health endpoints with session memory,
CORS, and error handling.
"""

import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config import CHROMA_DIR, EMBEDDING_MODEL
from rag import run_rag

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="BimBam Buy RAG Agent", version="0.2.0")

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------

SESSION_TTL_SECONDS = 30 * 60  # 30 minutes
MAX_SESSION_MESSAGES = 10      # 5 user + 5 assistant

sessions: dict[str, list[dict]] = {}
session_timestamps: dict[str, float] = {}


def _cleanup_expired_sessions() -> None:
    """Remove sessions inactive for more than 30 minutes."""
    now = time.time()
    expired = [
        sid for sid, ts in session_timestamps.items()
        if now - ts > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        sessions.pop(sid, None)
        session_timestamps.pop(sid, None)


def _get_session_history(session_id: str) -> list[dict]:
    """Get or create session history, cleaning up expired sessions first."""
    _cleanup_expired_sessions()
    if session_id not in sessions:
        sessions[session_id] = []
    session_timestamps[session_id] = time.time()
    return sessions[session_id]


def _add_message(session_id: str, role: str, content: str) -> None:
    """Append a message, keeping only the last MAX_SESSION_MESSAGES."""
    history = sessions[session_id]
    history.append({"role": role, "content": content})
    # Keep only last N messages
    if len(history) > MAX_SESSION_MESSAGES:
        sessions[session_id] = history[-MAX_SESSION_MESSAGES:]


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str


class HealthResponse(BaseModel):
    status: str
    documents_loaded: bool


# ---------------------------------------------------------------------------
# Startup: load vectorstore once
# ---------------------------------------------------------------------------

vectorstore: Optional[Chroma] = None


@app.on_event("startup")
async def load_vectorstore() -> None:
    """Load the persisted ChromaDB vector store at startup."""
    global vectorstore
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )
    print(f"Vector store loaded: {vectorstore._collection.count()} vectors")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Process a chat message using RAG."""
    global vectorstore

    if vectorstore is None:
        raise HTTPException(status_code=503, detail="Vector store not ready")

    if not req.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty")

    if not req.session_id.strip():
        raise HTTPException(status_code=422, detail="Session ID cannot be empty")

    try:
        # Build context with conversation history
        history = _get_session_history(req.session_id)
        history_text = ""
        if history:
            history_text = "\n".join(
                f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
                for m in history[-6:]  # Last 3 exchanges
            )
            history_text = f"\n\nHistorial reciente:\n{history_text}"

        # Run RAG pipeline (includes retrieval, fallback check, generation)
        result = run_rag(req.message, vectorstore, history_text=history_text)

        # Store messages in session
        _add_message(req.session_id, "user", req.message)
        _add_message(req.session_id, "assistant", result["answer"])

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=req.session_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    docs_loaded = vectorstore is not None and vectorstore._collection.count() > 0
    return HealthResponse(status="ok", documents_loaded=docs_loaded)
