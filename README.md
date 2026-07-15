# BimBam Buy - Asistente Virtual con RAG

Agente de inteligencia artificial corporativo que responde preguntas de colaboradores de BimBam Buy basándose en documentos internos de la empresa.

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Container                      │
│                                                         │
│  ┌─────────────┐    HTTP    ┌─────────────────────┐    │
│  │  Streamlit   │ ─────────►│     FastAPI          │    │
│  │  (Frontend)  │           │     (Backend)        │    │
│  │  Puerto 8501 │           │     Puerto 8000      │    │
│  └─────────────┘           └──────────┬──────────┘    │
│                                       │                 │
│                              ┌────────▼────────┐       │
│                              │   RAG Pipeline   │       │
│                              │   (LangChain)    │       │
│                              └────────┬────────┘       │
│                                       │                 │
│                    ┌──────────────────┼──────────┐     │
│                    │                  │          │     │
│              ┌─────▼─────┐    ┌──────▼──────┐  │     │
│              │  ChromaDB   │    │  Groq LLM   │  │     │
│              │  (Vectores) │    │  (Llama 3.1) │  │     │
│              └───────────┘    └─────────────┘  │     │
│                                                 │     │
│                    ┌────────────────────────────┘     │
│                    │                                   │
│              ┌─────▼─────┐                            │
│              │  5 PDFs    │                            │
│              │  BimBam Buy│                            │
│              └───────────┘                            │
└─────────────────────────────────────────────────────────┘
```

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Lenguaje | Python 3.14 |
| Framework RAG | LangChain |
| Vector Store | ChromaDB |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 |
| LLM | Groq Llama 3.1 8B Instant |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Deploy | Docker + OCI |

## Requisitos

- Python 3.14+
- Docker y Docker Compose (para deploy)
- API Key de Groq (gratis en [groq.com](https://groq.com))
- Token de HuggingFace (opcional, para evitar rate limits)

## Configuración Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/NicolasParadaA/challenge-alura-one.git
cd challenge-alura-one/bimbam-agent-final
```

### 2. Crear archivo .env

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```
GROQ_API_KEY=tu_api_key_de_groq
HF_API_TOKEN=tu_token_de_huggingface
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Indexar documentos

```bash
python ingest.py
```

Esto crea la base de datos vectorial en `chroma_db/` con 193 vectores de los 5 PDFs.

### 5. Ejecutar el sistema

En **terminal 1** (Backend):
```bash
uvicorn api:app --reload --port 8000
```

En **terminal 2** (Frontend):
```bash
streamlit run app.py
```

Abrir http://localhost:8501 en el navegador.

## Ejecutar con Docker

```bash
docker compose up --build
```

Los servicios estarán disponibles en:
- API: http://localhost:8000
- Frontend: http://localhost:8501

## Uso

### Ejemplos de preguntas

- ¿Cuál es la política de devoluciones?
- ¿Cómo funciona el programa de afiliados?
- ¿Qué métodos de pago aceptan?
- ¿Cuánto cuesta el envío?
- ¿Cuál es la garantía de los productos?

### API

**POST /chat**
```json
{
  "message": "¿Cuál es la política de devoluciones?",
  "session_id": "mi-sesion-123"
}
```

Respuesta:
```json
{
  "answer": "Según la política de devoluciones...",
  "sources": ["politica-de-reembolsos-y-devoluciones-de-bimbambuy.pdf"],
  "session_id": "mi-sesion-123"
}
```

**GET /health**
```json
{
  "status": "ok",
  "documents_loaded": true
}
```

## Documentos de BimBam Buy

| Documento | Descripción |
|-----------|-------------|
| Guía de envíos | Tiempos y costos de envío por zona |
| Manual de garantía | Períodos y cobertura de garantía |
| Política de reembolsos | Reglas de devolución y reembolso |
| FAQ métodos de pago | Preguntas frecuentes sobre pagos |
| Programa de afiliados | Comisiones y reglas de afiliados |

## Decisiones Técnicas

- **Embeddings multilingües**: Usamos `paraphrase-multilingual-MiniLM-L12-v2` para soporte español/inglés
- **ChromaDB local**: Sin servidor externo, persiste en disco
- **Threshold de similitud**: 18.0 (distancia L2) — textos con distancia menor son relevantes
- **Memoria de sesiones**: Últimos 10 mensajes en memoria, limpieza después de 30 min de inactividad
- **Stack mínimo**: Sin frameworks innecesarios, focus en el pipeline RAG

## License

Proyecto educativo - Challenge Alura ONE IA for Tech
