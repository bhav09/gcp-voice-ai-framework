# Universal GCP Multimodal Voice AI Framework

Production-grade Voice AI Framework for Google Cloud Platform. The architecture connects client applications to Google Gemini Live (Multimodal Live WebSockets API) via the google-genai SDK for low-latency, full-duplex voice interactions.

## Architecture Flow

```mermaid
flowchart TD
    User["User (Voice Input / Output)"]
    
    subgraph CoreEngine["Voice AI Core Engine"]
        Orchestrator["Session Orchestrator"]
        MemoryState["State & Memory Engine"]
        GuardrailsEngine["Guardrail & Resilience Layer"]
    end

    subgraph GeminiLive["Gemini Live Multimodal Engine"]
        GenAIClient["google-genai Live Client"]
        GeminiModel["Gemini 2.5 Flash"]
    end

    subgraph GCPConnectors["GCP Service Connectors"]
        RAGCorpus["Vertex AI Search (RAG Corpus & Document Provenance)"]
        SpannerDB["Cloud Spanner & Graph DB"]
        RelationalSQL["Cloud SQL (pgvector)"]
        DataWarehouse["BigQuery Analytics"]
        NoSQLDoc["Firestore Memory Store"]
        EventPubSub["Cloud Pub/Sub Messaging"]
    end

    subgraph ObservabilityEvals["Observability & Evals"]
        ToolEvals["Tool-Level & Provenance Evaluator"]
        AgentEvals["Agent Task Completion & STT Verifier"]
        CloudMetrics["Cloud Monitoring & Metrics Exporter"]
    end

    User <-->|Full-Duplex Audio PCM| Orchestrator
    Orchestrator <--> MemoryState
    Orchestrator <--> GuardrailsEngine

    Orchestrator <-->|Bidirectional Audio Stream| GenAIClient
    GenAIClient <--> GeminiModel

    GenAIClient -->|Function Call Execution| GCPConnectors
    GCPConnectors --> RAGCorpus
    GCPConnectors --> SpannerDB
    GCPConnectors --> RelationalSQL
    GCPConnectors --> DataWarehouse
    GCPConnectors --> NoSQLDoc
    GCPConnectors --> EventPubSub

    Orchestrator --> ObservabilityEvals
    ObservabilityEvals --> ToolEvals
    ObservabilityEvals --> AgentEvals
    ObservabilityEvals --> CloudMetrics
```

## System Capabilities

Gemini Live Integration
Uses the google-genai SDK for bidirectional streaming over WebSockets. Supports authentication via Vertex AI (Application Default Credentials) and Google AI Studio (API Key). Configurable models default to gemini-2.5-flash with native context window compression.

Resilience Engineering
Includes token-bucket rate limiting for session turns, exponential backoff retries with full jitter for GCP operations, and circuit breakers (CLOSED, OPEN, HALF_OPEN) across all GCP service connectors to handle backend outages cleanly.

GCP Service Integration and Multi-Service Extraction
Connectors for Cloud Spanner, Spanner Graph DB (ISO GQL), Cloud SQL (pgvector), Firestore, BigQuery, Cloud Pub/Sub, and Vertex AI Search (RAG). Allows the voice agent to extract real-time data across multiple GCP services in a single voice conversation and report structured insights back to the user.

State and Memory Management
Short-term working memory ring buffer with automatic context compaction, paired with persistent episodic memory stored in Cloud Firestore.

Tool-Level and Agent-Level Evaluations
Evaluates performance at both granular tool execution levels (latency, schema validity, RAG Corpus ID and Document URI provenance metadata, row-level provenance) and end-to-end agent levels (task success, turn latency percentiles, groundedness, and Speech-to-Text audio transcript WER verification).

Security Guardrails
Three-tier guardrail system covering input prompt injection checks, tool execution boundary filters (blocking DDL/DML mutations), and output safety evaluation.

## Quick Start

1. Install Dependencies

```bash
git clone https://github.com/bhav09/gcp-voice-ai-framework.git
cd gcp-voice-ai-framework

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Environment Configuration

Copy the sample configuration file and update parameters:

```bash
cp .env.example .env
```

Set environment variables in .env:

```bash
GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID
GCP_REGION=us-central1
VOICE_PROVIDER_TYPE=vertex
GEMINI_MODEL_NAME=gemini-2.5-flash
GEMINI_VOICE_NAME=Puck
```

3. Run the Service

```bash
python -m uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000
```

Access API documentation at http://localhost:8000/docs or establish WebSocket connections at ws://localhost:8000/ws/voice.

4. Testing

Run the test suite:

```bash
python run_tests.py
```

## License

Universal framework template for Google Cloud Platform.
