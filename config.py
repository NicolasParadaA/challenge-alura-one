"""Shared configuration module for BimBam Buy RAG Agent."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")

# Paths
CHROMA_DIR: str = "chroma_db"
DOCS_DIR: str = "docs"

# Model settings
EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL: str = "llama-3.1-8b-instant"

# Chunking
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 100

# Retrieval
TOP_K: int = 4
SIMILARITY_THRESHOLD: float = 0.3

# Generation
TEMPERATURE: float = 0.2
MAX_TOKENS: int = 1000
