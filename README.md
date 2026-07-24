<div align="center">
  <img src="assets/logo.png" alt="Universal GCP Multimodal Voice AI Framework Logo" width="450" />

  # Universal GCP Multimodal Voice AI Framework

  Production-grade Voice AI Framework for Google Cloud Platform. The architecture connects client applications to Google Gemini Live (Multimodal Live WebSockets API) via the `google-genai` SDK for low-latency, full-duplex voice interactions.
</div>


## System Capabilities

### Gemini Live Integration
* Uses the official `google-genai` SDK for bidirectional streaming over WebSockets.
* Supports dual authentication via Vertex AI (Application Default Credentials) and Google AI Studio (API Key).
* Configured by default for `gemini-2.5-flash` with native context window compression.

### Agent and Tool Orchestration
* **Voice Session Orchestrator**: Manages multi-turn session lifecycles, user identities, barge-in audio interruptions, and context window compaction.
* **Async Tool Dispatcher**: Dynamically converts Pydantic tool models into Gemini OpenAPI Function Declarations, intercepts live WebSocket function calls, executes concurrent GCP tool invocations, and returns formatted responses back to the Live stream.

### Automated Dashboard Generation
* **Cross-Source Data Discovery**: Identifies where target business metrics reside across BigQuery datasets, Cloud Spanner relational tables, Cloud SQL vector indexes, and Firestore document collections.
* **Automated Visual Specs**: Generates dashboard specifications with line charts, bar graphs, KPI cards, and Looker Studio / GCP Monitoring links directly from voice instructions.

### Cross-Source Executive Insights Engine
* Discovers and correlates data across BigQuery analytical engines, Cloud Spanner graph schemas, Cloud SQL pgvector similarity indexes, and Vertex RAG document corpora in a single voice turn.
* Synthesizes statistical takeaways, growth trends, anomalies, and executive summaries.

### Resilience Engineering
* **Token-Bucket Rate Limiter**: Enforces configurable rate limits per user session to protect downstream GCP services.
* **Circuit Breakers**: Implements state-machine breakers (CLOSED, OPEN, HALF_OPEN) across all GCP connectors to isolate backend outages gracefully.
* **Exponential Backoff Retries**: Decorates API operations with backoff and full jitter to recover from transient network drops automatically.

### State and Memory Management
* **Working Memory**: In-memory ring buffer tracking recent conversation turns with automated background context compaction.
* **Episodic Memory**: Persistent cross-session user profile and conversation state stored in Cloud Firestore.

### Tool-Level and Agent-Level Evaluations
* **Tool Execution Evaluator**: Verifies schema compliance, execution latency (ms), RAG Corpus ID and Document URI provenance metadata, and database row provenance.
* **Agent Performance Evaluator**: Measures end-to-end task success rates, turn latency percentiles (p50, p95, p99), response groundedness, and Word Error Rate (WER) using `google-cloud-speech` STT audio transcript verification.

### Strict NSFW and Off-Topic Guardrails
* **NSFW & Vulgar Language Blocking**: Detects explicit or profane language and politely redirects the conversation back to GCP enterprise operations.
* **Off-Topic Redirection Policy**: Politely declines non-business or off-topic conversation requests, remaining strictly focused on GCP analytics, dashboard creation, and data management tools.
* **Security & Mutation Boundaries**: Enforces read-only operational boundaries to block unauthorized database DDL/DML deletion commands.

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
        GuardrailsEngine["3-Tier Guardrails & NSFW Filter Layer"]
    end

    subgraph GeminiLiveEngine["Gemini Live Engine (google-genai)"]
        LiveClient["google-genai Live Connect Engine"]
        GeminiModel["Gemini 2.5 Flash"]
    end

    subgraph GCPFabric["Universal GCP Tool & Data Fabric"]
        DashboardTool["Automated Dashboard Generator"]
        InsightsTool["Cross-Source Insights Synthesizer"]
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
    
    GCPFabric --> DashboardTool
    GCPFabric --> InsightsTool
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

Set environment variables in `.env`:

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

Access API documentation at `http://localhost:8000/docs` or establish WebSocket connections at `ws://localhost:8000/ws/voice`.

4. Testing

Run the test suite:

```bash
python run_tests.py
```

## License

Universal framework template for Google Cloud Platform.
