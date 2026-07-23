# Universal GCP Multimodal Voice AI Framework (`gcp-voice-ai-framework`)

[![Google Cloud Platform](https://img.shields.io/badge/GCP-Exclusive-blue.svg)](https://cloud.google.com/)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Model-Gemini%202.5%20Flash-orange.svg)](https://deepmind.google/technologies/gemini/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API--First-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-30%20Passed-brightgreen.svg)]()

Production-grade, highly scalable, domain-agnostic enterprise **Voice AI Agent Framework**. Built strictly for **Google Cloud Platform (GCP)**, the architecture leverages the **Google Gemini Live (Multimodal Live WebSockets / Bidi API)** via the official **`google-genai`** SDK to deliver low-latency (< 800ms end-to-end), full-duplex, bidirectional voice interactions.

---

## 🌟 Key Architecture & Highlights

* **Official `google-genai` SDK Core**: Exclusively utilizes `from google import genai` and `genai.Client` referencing Google Gemini Live patterns for bidirectional WebSockets streaming.
* **API-First FastAPI Service Layer**: Exposes full-duplex WebSockets voice bridge (`GET /ws/voice`), REST tool execution engine (`POST /api/v1/tools/execute`), and session lifecycle management.
* **Universal GCP Tool & Connectivity Fabric**:
  * **Databases & Vector Search**: Cloud Spanner, Spanner Graph DB (GQL), Cloud SQL (`pgvector`), and Firestore document store.
  * **Enterprise RAG & Data Warehouse**: Vertex AI Search & Vector Search RAG, and BigQuery analytical SQL engine.
  * **Asynchronous Action Engine**: Cloud Pub/Sub event publisher for background enterprise actions.
  * **Model Context Protocol (MCP)**: Native MCP Client adapter (Stdio, SSE, gRPC).
* **Unified State & Common Memory Orchestrator**: Maintains active workflow steps, multi-turn working memory, automatic context compaction, and Firestore episodic memory.
* **Voice Speech-to-Text (STT) Verification Harness**: Automated output speech transcript verifier using **Google Cloud Speech-To-Text API** (`google-cloud-speech`) to assert what Gemini Live actually said.
* **Solidified 3-Tier Security Guardrails**: Prompt injection detector, SQL mutation blocker, and Cloud DLP PII redaction loggers.

---

## 📁 Repository Structure

```
gcp-voice-ai-framework/
├── README.md                    # Framework Overview & Documentation
├── requirements.txt             # Python dependencies
├── .env                         # Environment & GCP configuration template
├── .gitignore                   # Git ignore patterns
├── run_tests.py                 # Master test execution runner
├── config/
│   └── settings.py              # Global settings manager (Pydantic / BaseSettings)
├── src/
│   ├── api/
│   │   ├── fastapi_app.py       # Main FastAPI application server
│   │   └── routes/
│   │       ├── voice_ws_router.py   # WebSockets voice streaming bridge (/ws/voice)
│   │       ├── tools_router.py      # REST tool execution API (/api/v1/tools)
│   │       └── sessions_router.py   # Session lifecycle API (/api/v1/sessions)
│   ├── core/
│   │   ├── base_client.py       # Base Gemini Live client class
│   │   ├── aistudio_client.py   # AI Studio live client (google-genai SDK)
│   │   ├── vertex_client.py     # Vertex AI live client (ADC / OAuth2)
│   │   ├── audio_pipeline.py    # PCM resampler (16k->24k), VAD & jitter buffer
│   │   └── session_manager.py   # Session lifecycle & barge-in handler
│   ├── tools/
│   │   ├── base_tool.py         # Universal Tool interface & OpenAPI schema generator
│   │   ├── dispatcher.py        # Non-blocking async tool execution engine
│   │   ├── mcp_client.py        # Model Context Protocol (MCP) adapter
│   │   └── gcp_connectors/      # Native GCP service connectors
│   │       ├── bigquery_tool.py # BigQuery SQL engine tool
│   │       ├── cloudsql_tool.py # Cloud SQL (pgvector) database tool
│   │       ├── spanner_tool.py  # Cloud Spanner transactional DB tool
│   │       ├── spanner_graph_tool.py # Spanner Graph GQL traversal tool
│   │       ├── firestore_tool.py# Firestore document database tool
│   │       ├── pubsub_tool.py   # Cloud Pub/Sub event trigger tool
│   │       └── rag_vertex.py    # Vertex AI Search RAG connector tool
│   ├── memory/
│   │   ├── working_memory.py    # In-memory sliding dialogue turn buffer
│   │   ├── episodic_memory.py   # Firestore persistent user profile memory
│   │   └── state_memory_orchestrator.py # Unified state & memory orchestrator
│   ├── observability/
│   │   ├── metrics.py           # Latency (TTFT, SLA) & token throughput counters
│   │   ├── tracer.py            # OpenTelemetry & Cloud Trace spans
│   │   └── logger.py            # Cloud Logging & Cloud DLP PII Redactor
│   ├── evaluations/
│   │   ├── llm_judge.py         # Vertex AI AutoSxS groundedness & safety evaluator
│   │   ├── acoustic_metrics.py  # NISQA, WER & latency SLA percentiles
│   │   └── stt_verifier.py      # Cloud Speech-To-Text output speech verifier
│   └── security/
│       └── guardrails.py        # 3-Tier guardrail & security engine
└── tests/
    ├── unit/                    # Unit tests for core, FastAPI, and payload modules
    ├── integration/             # Integration tests for GCP services & tools
    ├── synthetic_scenarios/     # Synthetic audio stream E2E tests
    └── evaluations/             # Evaluator & STT verification tests
```

---

## 🚀 Quick Start Guide

### 1. Installation & Environment Setup

```bash
# Clone the repository
git clone https://github.com/bhav09/gcp-voice-ai-framework.git
cd gcp-voice-ai-framework

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `.env` or set environment variables:

```bash
export GCP_PROJECT_ID="gen-demo-66-20250711"
export GCP_REGION="us-central1"
export VOICE_PROVIDER_TYPE="vertex"  # or 'aistudio'
export GEMINI_MODEL_NAME="gemini-2.5-flash"
export GEMINI_VOICE_NAME="Puck"
```

### 3. Run FastAPI Web & WebSockets Server

```bash
python -m uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

* **Swagger API Docs**: `http://localhost:8000/docs`
* **Health Endpoint**: `http://localhost:8000/health`
* **Voice WebSockets Stream**: `ws://localhost:8000/ws/voice`

### 4. Run Automated Test Suite

```bash
python run_tests.py
```

---

## 🧪 Comprehensive Verification & Test Suite

The framework includes **30 automated test cases** verifying all components:

```bash
pytest -v
```

* **Unit Tests**: Provider auth, audio VAD/pipeline, tool dispatcher, real payloads, FastAPI REST & WebSocket endpoints.
* **GCP Services Integration**: BigQuery, Cloud SQL (`pgvector`), Spanner, Spanner Graph (GQL), Firestore, PubSub, Vertex Search RAG.
* **Synthetic E2E Audio Flow**: Simulated PCM 16kHz audio input turns, Gemini Live connection, TTFT latency (< 800ms SLA), and barge-in interruption handling.
* **Evaluations & STT**: Speech-to-Text audio transcript verification via `google-cloud-speech`, WER calculator, and LLM-as-a-judge groundedness.

---

## 🛡️ License & Compliance

Developed as a universal enterprise framework template for Google Cloud Platform. Strict read-only/create-only execution guidelines prevent resource deletion during operational calls.
