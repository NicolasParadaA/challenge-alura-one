"""RAG pipeline for BimBam Buy Agent.

Builds the retrieval-augmented generation chain using LCEL,
handles similarity-based retrieval with score thresholding,
and provides source extraction helpers.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_chroma import Chroma

from config import (
    GROQ_API_KEY,
    LLM_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    TOP_K,
    SIMILARITY_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

RAG_PROMPT_TEMPLATE = (
    "Basado en el siguiente contexto, responde la pregunta. "
    "Si no sabes, di que no tienes información.\n\n"
    "Contexto: {context}\n\n"
    "Pregunta: {question}"
)

rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_docs(docs: list) -> str:
    """Join documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def extract_sources(docs: list) -> list[str]:
    """Extract unique source filenames from document metadata."""
    sources = []
    seen = set()
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        if source not in seen:
            sources.append(source)
            seen.add(source)
    return sources


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def get_relevant_docs(query: str, vectorstore: Chroma) -> tuple[list, list[str]]:
    """Retrieve documents filtered by similarity threshold.

    Returns:
        (docs, sources): matched documents and their source filenames.
    """
    results = vectorstore.similarity_search_with_score(query, k=TOP_K)
    # Chroma returns (doc, distance) — lower distance = more similar.
    # Filter by threshold.
    filtered = [doc for doc, score in results if score <= SIMILARITY_THRESHOLD]
    sources = extract_sources(filtered)
    return filtered, sources


# ---------------------------------------------------------------------------
# Chain builder
# ---------------------------------------------------------------------------

def build_rag_chain(vectorstore: Chroma):
    """Build and return an LCEL RAG chain.

    The chain: prompt → Groq LLM → string output.
    Accepts {"context": str, "question": str} as input.
    """
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=LLM_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    chain = rag_prompt | llm | StrOutputParser()
    return chain


def run_rag(question: str, vectorstore: Chroma) -> dict:
    """End-to-end RAG call: retrieve → format → generate → return answer + sources."""
    docs, sources = get_relevant_docs(question, vectorstore)
    context = format_docs(docs)

    chain = build_rag_chain(vectorstore)
    answer = chain.invoke({"context": context, "question": question})

    return {
        "answer": answer,
        "sources": sources,
    }
