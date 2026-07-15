"""Streamlit frontend for BimBam Buy RAG Agent.

Provides a chat interface that communicates with the FastAPI backend.
"""

import streamlit as st
import httpx
import uuid
import re

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_URL}/chat"
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
# Session state initialization
# ---------------------------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🤖 BimBam Buy - Asistente Virtual")
st.caption("Pregúntale sobre devoluciones, afiliados, métodos de pago y más")

# ---------------------------------------------------------------------------
# Language detection helper
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Display chat history
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Show sources if present (assistant messages only)
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📄 Fuentes consultadas"):
                for source in msg["sources"]:
                    st.write(f"- {source}")
        # Show language badge
        if msg["role"] == "assistant":
            lang = _detect_language(msg["content"])
            st.caption(f"🌐 Idioma detectado: {lang}")


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send to API
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = httpx.post(
                    CHAT_ENDPOINT,
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                answer = data["answer"]
                sources = data.get("sources", [])

                st.markdown(answer)

                # Language badge
                lang = _detect_language(answer)
                st.caption(f"🌐 Idioma detectado: {lang}")

                # Sources expander
                if sources:
                    with st.expander("📄 Fuentes consultadas"):
                        for source in sources:
                            st.write(f"- {source}")

                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except httpx.ConnectError:
                error_msg = "⚠️ No se pudo conectar al API. Asegúrate de que el servidor esté corriendo en `localhost:8000`."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })
            except httpx.HTTPStatusError as e:
                error_msg = f"⚠️ Error del API: {e.response.status_code} - {e.response.text}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })
            except Exception as e:
                error_msg = f"⚠️ Error inesperado: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })

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