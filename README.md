# 🤖 BimBam Buy — Asistente Virtual

Chatbot inteligente que responde preguntas de colaboradores de BimBam Buy utilizando documentos internos de la empresa (políticas, envíos, pagos, garantías y afiliados).

## Cómo funciona

1. El usuario escribe una pregunta
2. El sistema busca la información relevante en 5 PDFs de la empresa
3. La IA genera una respuesta precisa con las fuentes consultadas

## Arquitectura

```
Streamlit (Frontend) → FastAPI (Backend) → LangChain (RAG) → ChromaDB + Groq LLM
```

## Tecnologías

- **Frontend:** Streamlit
- **Backend:** FastAPI, Python 3.12
- **IA:** LangChain, Groq (Llama 3.3), HuggingFace Embeddings
- **Base de datos vectorial:** ChromaDB
- **Deploy:** Docker en Oracle Cloud (OCI)

## Ejecutar el proyecto

```bash
# Clonar
git clone https://github.com/NicolasParadaA/challenge-alura-one.git
cd challenge-alura-one

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GROQ_API_KEY

# Ejecutar con Docker
docker-compose up -d --build
```

Abrir http://localhost:8501

## Ejemplo de preguntas y respuestas

**¿Cuánto cuesta el envío?**

> Los costos de envío varían según la zona. Para Buenos Aires, el envío estándar tiene un costo de $5.000. Para el interior, los tiempos son de 3 a 7 días hábiles.

**¿Cuál es la política de devoluciones?**

> Se pueden devolver productos dentro de los primeros 30 días. El producto debe estar en perfectas condiciones, con etiquetas originales y sin uso.

**¿Qué métodos de pago aceptan?**

> Tarjeta de crédito, débito, transferencia bancaria, pago en efectivo en puntos habilitados, y billeteras digitales. También ofrecemos cuotas o financiamiento.

## Deploy en Oracle Cloud

**Enlace:** [http://144.22.62.189:8501](http://144.22.62.189:8501)

![Modo Claro](docs/screenshot-1.png)

![Modo Oscuro](docs/screenshot-2.png)
