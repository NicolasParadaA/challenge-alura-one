"""Streamlit frontend for BimBam Buy RAG Agent.

Provides a branded, streaming chat interface that communicates with the FastAPI
backend via SSE (Server-Sent Events).
"""

import os

import streamlit as st
import httpx
import json
import uuid
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL = os.getenv("API_URL", "http://localhost:8000")
CHAT_STREAM_ENDPOINT = f"{API_URL}/chat/stream"
HEALTH_ENDPOINT = f"{API_URL}/health"

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="BimBam Buy - Asistente Virtual",
    page_icon="🤖",
    layout="centered",
)

# ---------------------------------------------------------------------------
# CSS injection — brand colors, bubble styling, typography
# ---------------------------------------------------------------------------

BRAND_CSS = """
<style>
/* ---- Brand colors ---- */
:root {
    --bimbam-primary: #FF6B35;
    --bimbam-secondary: #004E89;
    --bimbam-bg: #F8F9FA;
}

/* ---- Header ---- */
.stApp header {
    border-bottom: 3px solid var(--bimbam-primary);
}

/* ---- Chat bubble overrides ---- */
.stChatMessage {
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    border-left: 4px solid transparent;
}
[data-testid="stChatMessage"][aria-label="user"] {
    border-left-color: var(--bimbam-secondary);
    background: #eef3f9;
}
[data-testid="stChatMessage"][aria-label="assistant"] {
    border-left-color: var(--bimbam-primary);
    background: #fff7f3;
}

/* ---- Avatar badges ---- */
.avatar-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    font-size: 18px;
    margin-right: 6px;
    vertical-align: middle;
    flex-shrink: 0;
}
.avatar-user {
    background: var(--bimbam-secondary);
    color: white;
}
.avatar-assistant {
    background: var(--bimbam-primary);
    color: white;
}

/* ---- Timestamp caption ---- */
.msg-timestamp {
    font-size: 0.75em;
    color: #888;
    margin-top: 4px;
    text-align: right;
}

/* ---- Typography ---- */
.stMarkdown p { line-height: 1.6; }
.stMarkdown h2 { color: var(--bimbam-secondary); }

/* ---- Welcome section ---- */
.welcome-container {
    background: linear-gradient(135deg, #fff7f3 0%, #eef3f9 100%);
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}
.welcome-container h2 { margin-top: 0; color: var(--bimbam-secondary); }
.welcome-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin: 16px 0;
}
.welcome-cards .card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px;
    text-align: center;
    transition: transform 0.15s, box-shadow 0.15s;
    font-size: 0.95em;
}
.welcome-cards .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* ---- Skeleton shimmer ---- */
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
.skeleton-line {
    height: 16px;
    border-radius: 4px;
    background: linear-gradient(90deg, #e0e0e0 25%, #f0f0f0 50%, #e0e0e0 75%);
    background-size: 800px 100%;
    animation: shimmer 1.5s infinite linear;
    margin-bottom: 10px;
}
.skeleton-line-short  { width: 40%; }
.skeleton-line-long   { width: 90%; }
.skeleton-line-medium { width: 65%; }
</style>
"""

st.markdown(BRAND_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = True

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🤖 BimBam Buy - Asistente Virtual")
st.caption("Pregúntale sobre devoluciones, afiliados, métodos de pago y más")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STREAM_URL = f"{API_URL}/chat/stream"


def _detect_language(text: str) -> str:
    """Simple heuristic to detect if response is Spanish or English."""
    spanish_indicators = [
        r'\b(el|la|los|las|un|una|de|del|en|con|por|para|que|se|no|sí|pero|como|este|esta|más|también|puede|tiene|debe|todo|bien)\b',
        r'[áéíóúñ¿¡]',
    ]
    score = 0
    for pattern in spanish_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            score += 1
    return "Español" if score >= 2 else "English"


def _now_timestamp() -> str:
    """Return current time as HH:MM."""
    return datetime.now().strftime("%H:%M")


def render_skeleton() -> None:
    """Show animated shimmer placeholders while waiting for the stream."""
    skeleton_html = """
    <div class="skeleton-container">
      <div class="skeleton-line skeleton-line-short"></div>
      <div class="skeleton-line skeleton-line-long"></div>
      <div class="skeleton-line skeleton-line-medium"></div>
    </div>
    """
    st.markdown(skeleton_html, unsafe_allow_html=True)


def render_welcome() -> None:
    """Render the branded welcome section with topic cards."""
    welcome_html = """
    <div class="welcome-container">
      <h2>👋 ¡Bienvenido a BimBam Buy!</h2>
      <p><strong>BimBam Buy</strong> es tu tienda online de confianza.</p>
      <p>Este chat puede ayudarte con:</p>
      <div class="welcome-cards">
        <div class="card">📋 Política de devoluciones</div>
        <div class="card">💰 Métodos de pago</div>
        <div class="card">🚚 Costos y tiempos de envío</div>
        <div class="card">🤝 Programa de afiliados</div>
        <div class="card">🛡️ Garantías de productos</div>
      </div>
      <p><em>Ejemplo: "¿Cuántos días tengo para devolver un producto?"</em></p>
    </div>
    """
    st.markdown(welcome_html, unsafe_allow_html=True)


def handle_chat(prompt: str) -> None:
    """Send a message to the streaming endpoint and render the response progressively."""
    # Append user message
    user_msg = {
        "role": "user",
        "content": prompt,
        "timestamp": _now_timestamp(),
    }
    st.session_state.messages.append(user_msg)

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
        st.caption(f"🕐 {user_msg['timestamp']}")

    # Create placeholder for assistant response
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        render_skeleton()

        try:
            answer = ""
            sources = []

            with httpx.stream(
                "POST",
                STREAM_URL,
                json={
                    "message": prompt,
                    "session_id": st.session_state.session_id,
                },
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = json.loads(line[6:])
                    if "token" in payload:
                        answer += payload["token"]
                        placeholder.markdown(answer)
                    if payload.get("done"):
                        sources = payload.get("sources", [])

            # Clear skeleton, show final answer
            placeholder.markdown(answer)

            # Timestamp
            st.caption(f"🕐 {_now_timestamp()}")

            # Language badge
            lang = _detect_language(answer)
            st.caption(f"🌐 Idioma detectado: {lang}")

            # Sources expander
            if sources:
                with st.expander("📄 Fuentes consultadas"):
                    for source in sources:
                        st.write(f"- {source}")

            # Store in history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "timestamp": _now_timestamp(),
                "error": False,
            })

        except (httpx.ConnectError, httpx.HTTPStatusError, Exception) as e:
            error_msg = f"⚠️ Error: {str(e)}"
            placeholder.empty()
            st.error(error_msg)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "sources": [],
                "timestamp": _now_timestamp(),
                "error": True,
            })
            st.session_state.last_failed_prompt = prompt


# ---------------------------------------------------------------------------
# Welcome section (dismissible after first message)
# ---------------------------------------------------------------------------

if st.session_state.welcome_shown and len(st.session_state.messages) == 0:
    render_welcome()

if len(st.session_state.messages) > 0:
    st.session_state.welcome_shown = False

# ---------------------------------------------------------------------------
# Display chat history
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        # Timestamp
        if msg.get("timestamp"):
            st.caption(f"🕐 {msg['timestamp']}")
        # Sources (assistant only)
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📄 Fuentes consultadas"):
                for source in msg["sources"]:
                    st.write(f"- {source}")
        # Language badge
        if msg["role"] == "assistant":
            lang = _detect_language(msg["content"])
            st.caption(f"🌐 Idioma detectado: {lang}")


# ---------------------------------------------------------------------------
# Retry button (on last error)
# ---------------------------------------------------------------------------

if st.session_state.get("last_failed_prompt"):
    if st.button("🔄 Reintentar"):
        failed = st.session_state.last_failed_prompt
        del st.session_state.last_failed_prompt
        handle_chat(failed)
        st.rerun()

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    handle_chat(prompt)

# ---------------------------------------------------------------------------
# Sidebar: session info
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("ℹ️ Información")
    st.write(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
    st.write(f"**Mensajes:** {len(st.session_state.messages)}")

    if st.button("🗑️ Nueva conversación"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.welcome_shown = True
        st.rerun()

    st.divider()
    st.markdown("""
    **Ejemplos de preguntas:**
    - ¿Cuál es la política de devoluciones?
    - ¿Cómo funciona el programa de afiliados?
    - ¿Qué métodos de pago aceptan?
    - ¿Cuánto cuesta el envío?
    - ¿Cuál es la garantía de los productos?
    """)
