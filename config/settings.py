import os
from typing import Literal, Optional
from pydantic import BaseModel, Field

class VoiceAgentSettings(BaseModel):
    """Global dynamic configuration settings for the Universal GCP Voice AI Agent."""
    
    # GCP Project & Identity Configuration
    gcp_project_id: str = Field(
        default_factory=lambda: os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
    )
    gcp_region: str = Field(
        default_factory=lambda: os.getenv("GCP_REGION", "us-central1")
    )
    
    # Dual Engine Provider Configuration ('vertex' or 'aistudio')
    provider_type: Literal["vertex", "aistudio"] = Field(
        default_factory=lambda: os.getenv("VOICE_PROVIDER_TYPE", "vertex")
    )
    
    # Gemini Model Specification (Defaulting to gemini-2.5-flash / gemini-2.0-flash-exp)
    model_name: str = Field(
        default_factory=lambda: os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    )
    
    # Prebuilt Voice Selection (e.g. "Puck", "Charon", "Kore", "Fenrir", "Aoede", "Zephyr")
    voice_name: str = Field(
        default_factory=lambda: os.getenv("GEMINI_VOICE_NAME", "Puck")
    )
    
    # System Persona & Guardrail Policy Instruction
    system_instruction: str = (
        "You are an enterprise GCP Voice AI Assistant specializing in GCP data analytics, automated dashboard generation, "
        "and cross-source data discovery across BigQuery, Cloud Spanner, Cloud SQL, Firestore, Cloud Pub/Sub, and Vertex RAG. "
        "STRICT POLICY: You must NOT entertain any NSFW, vulgar, explicit, profane language or off-topic non-business conversations. "
        "If a user uses NSFW language or engages in off-topic chatter, politely decline and steer the conversation back "
        "to GCP enterprise analytics, dashboard creation, and data extraction tools."
    )

    # API Keys & Credentials
    gemini_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY")
    )
    google_application_credentials: Optional[str] = Field(
        default_factory=lambda: os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    
    # Audio Specs
    input_sample_rate: int = 16000
    output_sample_rate: int = 24000
    audio_encoding: str = "AUDIO_PCM"
    
    # FastAPI Server Configuration
    fastapi_host: str = Field(default_factory=lambda: os.getenv("FASTAPI_HOST", "0.0.0.0"))
    fastapi_port: int = Field(default_factory=lambda: int(os.getenv("FASTAPI_PORT", "8000")))
    
    # Observability & Evaluation
    enable_cloud_tracing: bool = True
    enable_dlp_pii_redaction: bool = False
    target_latency_sla_ms: float = 800.0

settings = VoiceAgentSettings()
