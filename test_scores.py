"""Debug similarity scores."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import CHROMA_DIR, EMBEDDING_MODEL

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

results = vectorstore.similarity_search_with_score("¿Qué es BimBam Buy?", k=4)
print("Raw similarity scores (lower = more similar):")
for doc, score in results:
    source = doc.metadata.get("source", "?")
    print(f"  score={score:.4f} source={source}")
    print(f"  content={doc.page_content[:120]}...")
    print()
