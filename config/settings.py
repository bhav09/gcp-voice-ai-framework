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
