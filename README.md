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
│              │  (Vectores) │    │  (Llama 3.3) │  │     │
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

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Lenguaje | Python | 3.12 |
| Framework RAG | LangChain | 0.3.x |
| Vector Store | ChromaDB | 0.5.x |
| Embeddings | HuggingFace | paraphrase-multilingual-MiniLM-L12-v2 |
| LLM | Groq | Llama 3.3 70B Versatile |
| Backend API | FastAPI | 0.115.x |
| Frontend | Streamlit | 1.40.x |
| Deploy | Docker + Oracle Cloud | OCI ARM64 |

## Requisitos

### Para desarrollo local

- Python 3.12+
- pip
- API Key de Groq (gratis en [groq.com](https://groq.com))
- Token de HuggingFace (opcional, para evitar rate limits)

### Para deploy en Oracle Cloud

- Cuenta OCI con VM ARM64 (Ubuntu 24.04)
- Docker y Docker Compose instalados
- SSH key para acceso
- Puerto 8501 abierto en Security List

## Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/NicolasParadaA/challenge-alura-one.git
cd challenge-alura-one
```

### 2. Crear archivo .env

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
GROQ_API_KEY=tu_api_key_de_groq
HF_API_TOKEN=tu_token_de_huggingface
CORS_ORIGINS=http://localhost:8501
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

## Ejecutar

### Opción 1: Desarrollo (hot reload)

```bash
docker-compose -f docker-compose.dev.yml up --build
```

Los cambios en el código se reflejan automáticamente sin rebuild.

### Opción 2: Producción

```bash
docker-compose up -d --build
```

### Opción 3: Sin Docker

Terminal 1 (Backend):
```bash
uvicorn api:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
streamlit run app.py
```

## Deploy en Oracle Cloud

### Evidencia de Deploy

**Enlace público:** [http://144.22.62.189:8501](http://144.22.62.189:8501)

**Captura de pantalla - Modo Claro:**

![BimBam Buy - Modo Claro](docs/screenshot-1.png)

**Captura de pantalla - Modo Oscuro:**

![BimBam Buy - Modo Oscuro](docs/screenshot-2.png)

### Configuración de la VM

- **Proveedor:** Oracle Cloud Infrastructure (OCI)
- **Tipo:** VM.Standard.A1.Flex (ARM64)
- **Recursos:** 2 OCPUs, 12GB RAM
- **Sistema Operativo:** Ubuntu 24.04
- **Puertos abiertos:** 22 (SSH), 8501 (Streamlit)

### 1. Crear VM ARM64

- Image: Ubuntu 24.04
- Shape: VM.Standard.A1.Flex (2 OCPUs, 12GB RAM)
- Puertos abiertos: 22 (SSH), 8501 (Streamlit)

### 2. Conectar por SSH

```bash
ssh -i tu-key.pem ubuntu@tu-ip-oci
```

### 3. Instalar Docker

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
newgrp docker
```

### 4. Clonar y ejecutar

```bash
git clone https://github.com/NicolasParadaA/challenge-alura-one.git
cd challenge-alura-one

# Crear .env
cp .env.example .env
nano .env  # Agregar GROQ_API_KEY

# Ejecutar
docker-compose up -d --build
```

### 5. Acceder

Abrir en el navegador:
```
http://tu-ip-oci:8501
```

## API

### POST /chat

```json
{
  "message": "¿Cuál es la política de devoluciones?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Respuesta:
```json
{
  "answer": "Según la política de devoluciones...",
  "sources": ["politica-de-reembolsos-y-devoluciones-de-bimbambuy.pdf"],
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### POST /chat/stream (SSE)

Respuesta en tiempo real (streaming):
```
data: {"token": "El"}
data: {"token": " envío"}
data: {"token": " cuesta"}
data: {"sources": ["guia-de-envios.pdf"], "done": true}
```

### GET /health

```json
{
  "status": "ok",
  "documents_loaded": true
}
```

## Ejemplos de Preguntas y Respuestas

### Ejemplos de preguntas que el agente puede responder

- ¿Cuál es la política de devoluciones?
- ¿Cómo funciona el programa de afiliados?
- ¿Qué métodos de pago aceptan?
- ¿Cuánto cuesta el envío?
- ¿Cuál es la garantía de los productos?

### Ejemplos de respuestas generadas

**Pregunta:** ¿Cuánto cuesta el envío?

**Respuesta:**
> Los costos de envío varían según la zona y el peso del paquete. Para Buenos Aires y alrededores, el envío estándar tiene un costo de $5.000. Para el interior del país, los tiempos pueden ser de 3 a 7 días hábiles dependingiendo de la ubicación. Consultá la guía completa de envíos para más detalles sobre tu zona.

**Fuentes:** guia-de-tiempos-y-costos-de-envio-de-bimbambuy.pdf

---

**Pregunta:** ¿Cuál es la política de devoluciones?

**Respuesta:**
> La política de devoluciones de BimBam Buy permite devolver productos dentro de los primeros 30 días después de la compra. El producto debe estar en perfectas condiciones, con etiquetas originales y sin uso. Para iniciar una devolución, contactá a nuestro equipo de soporte con el número de orden y el motivo de la devolución.

**Fuentes:** politica-de-reembolsos-y-devoluciones-de-bimbambuy.pdf

---

**Pregunta:** ¿Cómo funciona el programa de afiliados?

**Respuesta:**
> El programa de afiliados de BimBam Buy funciona de la siguiente manera: recibís un enlace o código rastreable. Cuando una compra válida se origina desde ese canal, la venta puede generar una comisión. Las comisiones varían según la categoría del producto y el volumen de ventas. Registrándote como afiliado, accedés a herramientas de seguimiento y reportes de tus ganancias.

**Fuentes:** programa-de-afiliados-de-bimbambuy.pdf

---

**Pregunta:** ¿Qué métodos de pago aceptan?

**Respuesta:**
> Aceptamos varios métodos de pago que pueden variar según el país y la categoría. Entre ellos: tarjeta de crédito, tarjeta de débito, transferencia bancaria, pago en efectivo en puntos habilitados, y billeteras digitales disponibles por país. También ofrecemos cuotas o financiamiento cuando aplique.

**Fuentes:** preguntas-frecuentes-sobre-metodos-de-pago-de-bimbambuy.pdf

## Documentos de BimBam Buy

| Documento | Descripción |
|-----------|-------------|
| Guía de envíos | Tiempos y costos de envío por zona |
| Manual de garantía | Períodos y cobertura de garantía |
| Política de reembolsos | Reglas de devolución y reembolso |
| FAQ métodos de pago | Preguntas frecuentes sobre pagos |
| Programa de afiliados | Comisiones y reglas de afiliados |

## Seguridad

- CORS restringido a orígenes configurados
- Session IDs validados (UUID v4)
- Límite de 2000 caracteres por mensaje
- Variables sensibles en `.env` (no en código)
- `.env` excluido de Git y Docker

## Decisiones Técnicas

- **Embeddings multilingües**: `paraphrase-multilingual-MiniLM-L12-v2` para soporte español/inglés
- **ChromaDB local**: Sin servidor externo, persiste en disco
- **Threshold de similitud**: 17.3 (distancia L2, basado en profiling empírico)
- **MMR**: λ=0.7 para diversidad en resultados
- **Streaming**: SSE para respuestas en tiempo real
- **Hot reload**: Volumes en docker-compose.dev.yml para desarrollo

## License

Proyecto educativo - Challenge Alura ONE IA for Tech
