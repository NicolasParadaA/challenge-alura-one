# 🤖 BimBam Buy — Asistente Virtual Inteligente

Un chatbot corporativo potenciado por Inteligencia Artificial que responde automáticamente las preguntas más frecuentes de los colaboradores de **BimBam Buy**, una tienda online de confianza.

El agente utiliza **RAG (Retrieval-Augmented Generation)** para buscar información en documentos oficiales de la empresa y generar respuestas precisas y actualizadas.

---

## 🏗️ Arquitectura de la Solución

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│                  │      │                  │      │                  │
│    Streamlit     │─────►│     FastAPI      │─────►│  LangChain RAG   │
│    (Frontend)    │ HTTP │    (Backend)     │      │   (Pipeline)     │
│                  │      │                  │      │                  │
└──────────────────┘      └──────────────────┘      └────────┬─────────┘
                                                             │
                                              ┌──────────────┴──────────────┐
                                              │                             │
                                     ┌────────▼────────┐          ┌────────▼────────┐
                                     │                 │          │                 │
                                     │    ChromaDB     │          │  Groq + GPT-OSS │
                                     │  (Vectores)     │          │    (120B)       │
                                     │                 │          │                 │
                                     └─────────────────┘          └─────────────────┘
```

**Flujo de trabajo:**
1. El colaborador escribe una pregunta en el chat
2. El sistema busca los fragmentos más relevantes en los documentos
3. La IA genera una respuesta clara basada en la información encontrada
4. Se muestra la respuesta junto con las fuentes consultadas

---

## 💻 Tecnologías y Herramientas

| Componente | Tecnología | ¿Para qué sirve? |
|------------|-----------|-------------------|
| **Lenguaje** | Python 3.12 | Base del proyecto |
| **Frontend** | Streamlit | Interfaz de chat intuitiva |
| **Backend** | FastAPI | API REST de alta velocidad |
| **Motor RAG** | LangChain | Conecta búsqueda con generación |
| **Base de datos** | ChromaDB | Almacena documentos como vectores |
| **Embeddings** | HuggingFace | Convierte texto en números para buscar |
| **IA generativa** | Groq (GPT-OSS-120B) | Genera respuestas inteligentes |
| **Deploy** | Docker + Oracle Cloud | Ejecución en la nube |

---

## 🚀 Instrucciones para Ejecutar

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/NicolasParadaA/challenge-alura-one.git
cd challenge-alura-one

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GROQ_API_KEY (gratis en groq.com)

# 3. Ejecutar
docker-compose up -d --build
```

Abrir **http://localhost:8501** en el navegador.

### Opción 2: Sin Docker

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Indexar documentos
python ingest.py

# 3. Ejecutar Backend (Terminal 1)
uvicorn api:app --reload --port 8000

# 4. Ejecutar Frontend (Terminal 2)
streamlit run app.py
```

---

## 💬 Ejemplos de Preguntas que el Agente Puede Responder

El agente está entrenado con 5 documentos oficiales de BimBam Buy:

| Documento | Tema |
|-----------|------|
| 📋 Política de reembolsos | Devoluciones y reembolsos |
| 💳 Métodos de pago | Preguntas frecuentes sobre pagos |
| 🚚 Guía de envíos | Tiempos y costos por zona |
| 🛡️ Manual de garantía | Períodos y cobertura |
| 🤝 Programa de afiliados | Comisiones y reglas |

**Preguntas de ejemplo:**
- ¿Cuál es la política de devoluciones?
- ¿Qué métodos de pago aceptan?
- ¿Cuánto cuesta el envío?
- ¿Cómo funciona el programa de afiliados?
- ¿Cuál es la garantía de los productos?

---

## 📝 Ejemplos de Respuestas Generadas

### Pregunta: "¿Cuánto cuesta el envío?"

> El costo del envío no es un valor fijo, sino que se determina en función de varios factores:
>
> - Destino del pedido (país, región y ciudad).
> - Peso volumétrico y tamaño del paquete.
> - Servicio de entrega seleccionado (estándar, exprés, etc.).
> - Promociones vigentes y umbral de envío gratis que pueda aplicar en el país o campaña.
>
> El importe final del envío se muestra antes de confirmar la compra, de modo que el cliente siempre sabe cuánto pagará.
>
> En resumen, el precio del envío varía según destino, peso/tamaño, tipo de servicio y posibles promociones; se visualiza en el checkout antes de finalizar la compra.
>
> 📄 **Fuente:** guia-de-tiempos-y-costos-de-envio-de-bimbambuy.pdf

---

### Pregunta: "¿Cuál es la política de devoluciones?"

> La política de devoluciones de BimBam Buy permite devolver productos dentro de los primeros 30 días después de la compra. El producto debe estar en perfectas condiciones, con etiquetas originales y sin uso. Para iniciar una devolución, contactá a nuestro equipo de soporte con el número de orden.
>
> 📄 **Fuente:** politica-de-reembolsos-y-devoluciones-de-bimbambuy.pdf

---

### Pregunta: "¿Qué métodos de pago aceptan?"

> Aceptamos varios métodos de pago que pueden variar según el país y la categoría: tarjeta de crédito, tarjeta de débito, transferencia bancaria, pago en efectivo en puntos habilitados, y billeteras digitales disponibles por país. También ofrecemos cuotas o financiamiento cuando aplique.
>
> 📄 **Fuente:** preguntas-frecuentes-sobre-metodos-de-pago-de-bimbambuy.pdf

---

### Pregunta: "¿Cómo funciona el programa de afiliados?"

> El programa de afiliados funciona de la siguiente manera: recibís un enlace o código rastreable. Cuando una compra válida se origina desde ese canal, la venta puede generar una comisión. Las comisiones varían según la categoría del producto y el volumen de ventas.
>
> 📄 **Fuente:** programa-de-afiliados-de-bimbambuy.pdf

---

## ☁️ Deploy en Oracle Cloud

**Enlace público:** [http://144.22.62.189:8501](http://144.22.62.189:8501)

**Configuración de la VM:**
- Proveedor: Oracle Cloud Infrastructure (OCI)
- Tipo: VM.Standard.A1.Flex (ARM64)
- Recursos: 1 OCPU, 6GB RAM
- Sistema: Ubuntu 24.04

**Capturas de pantalla:**

![Modo Claro](docs/screenshot-1.png)

![Modo Oscuro](docs/screenshot-2.png)
