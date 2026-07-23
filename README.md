# Universal GCP Multimodal Voice AI Framework

Production-grade Voice AI Framework for Google Cloud Platform. The architecture connects client applications to Google Gemini Live (Multimodal Live WebSockets API) via the google-genai SDK for low-latency, full-duplex voice interactions.

## Architecture Flow

```mermaid
flowchart TD
    User["User (Full-Duplex PCM Audio Stream)"]
    
    subgraph ServiceLayer["FastAPI Application & Transport Layer"]
        WSBridge["WebSockets Voice Stream Bridge"]
        RESTService["REST Tools & Sessions API"]
    end

    subgraph AgentOrchestration["Agent & Tool Orchestration Engine"]
        SessionOrchestrator["Voice Session Orchestrator"]
        ToolDispatcher["Async Tool Dispatcher & Schema Converter"]
        MemoryState["Unified State & Memory Orchestrator"]
        GuardrailsEngine["3-Tier Guardrails & Resilience Layer"]
    end

    subgraph GeminiLiveEngine["Gemini Live Engine (google-genai)"]
        LiveClient["google-genai Live Connect Engine"]
        GeminiModel["Gemini 2.5 Flash"]
    end

    subgraph GCPFabric["Universal GCP Tool & Data Fabric"]
        RAGCorpus["Vertex AI Search (RAG Corpus & Document Provenance)"]
        SpannerDB["Cloud Spanner & Graph DB (ISO GQL)"]
        RelationalSQL["Cloud SQL (pgvector)"]
        DataWarehouse["BigQuery Analytics Engine"]
        NoSQLStore["Firestore Episodic Memory Store"]
        EventPubSub["Cloud Pub/Sub Event Mesh"]
        MCPAdapter["Model Context Protocol (MCP) Adapter"]
    end

    subgraph ObservabilityFramework["Observability & Evaluation Framework"]
        ToolEvaluator["Tool-Level Provenance & Schema Evaluator"]
        AgentEvaluator["Agent Task Completion & STT Audio Verifier"]
        TelemetryExporter["Cloud Monitoring & OpenTelemetry Exporter"]
    end

    User <-->|Bidirectional Audio Stream| WSBridge
    User <-->|HTTP REST Requests| RESTService

    WSBridge <--> SessionOrchestrator
    RESTService <--> ToolDispatcher

    SessionOrchestrator <--> MemoryState
    SessionOrchestrator <--> GuardrailsEngine
    SessionOrchestrator <--> ToolDispatcher

    SessionOrchestrator <-->|Audio PCM Chunks & Tool Responses| LiveClient
    LiveClient <--> GeminiModel

    LiveClient -->|Function Call Events| ToolDispatcher
    ToolDispatcher -->|Async Concurrent Tool Invocations| GCPFabric
    
    GCPFabric --> RAGCorpus
    GCPFabric --> SpannerDB
    GCPFabric --> RelationalSQL
    GCPFabric --> DataWarehouse
    GCPFabric --> NoSQLStore
    GCPFabric --> EventPubSub
    GCPFabric --> MCPAdapter

    AgentOrchestration --> ObservabilityFramework
    ObservabilityFramework --> ToolEvaluator
    ObservabilityFramework --> AgentEvaluator
    ObservabilityFramework --> TelemetryExporter
```

## System Capabilities

Gemini Live Integration
Uses the google-genai SDK for bidirectional streaming over WebSockets. Supports authentication via Vertex AI (Application Default Credentials) and Google AI Studio (API Key). Configurable models default to gemini-2.5-flash with native context window compression.

Agent and Tool Orchestration
The Agent Orchestrator manages session lifecycles, user identity, working memory sliding buffers, and barge-in audio interruptions. The Async Tool Orchestrator converts Pydantic tool models into Gemini Function Declarations, intercepts function call events over WebSockets, executes concurrent tool calls across GCP services, and returns formatted responses back to the Live model stream.

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
