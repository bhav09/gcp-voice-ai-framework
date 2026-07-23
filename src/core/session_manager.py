import os
import uuid
import logging
from typing import Optional, Dict, Any
from .base_client import BaseGeminiLiveClient
from .aistudio_client import AIStudioLiveClient
from .vertex_client import VertexAILiveClient
from ..memory.state_memory_orchestrator import UnifiedStateAndMemoryOrchestrator

logger = logging.getLogger("VoiceSessionManager")

class VoiceSessionManager:
    """Manages Voice AI Agent session lifecycle, provider instantiation, interruption state, and common state/memory orchestration."""

    def __init__(self, session_id: Optional[str] = None, user_id: Optional[str] = None, project_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
        self.client: Optional[BaseGeminiLiveClient] = None
        self.active_turn_id: int = 0
        self.is_interrupted: bool = False
        
        # Common State & Memory Orchestrator
        self.memory_orchestrator = UnifiedStateAndMemoryOrchestrator(
            session_id=self.session_id,
            user_id=self.user_id,
            project_id=self.project_id
        )

    async def initialize(self) -> Dict[str, Any]:
        """Initialize session state and load persistent user memory."""
        return await self.memory_orchestrator.initialize_session()

    def create_client(
        self,
        provider_type: str = "vertex",
        project_id: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-exp",
        system_instruction: Optional[str] = None
    ) -> BaseGeminiLiveClient:
        """Factory method to instantiate Vertex AI or AI Studio Gemini Live client with memory prompt injection."""
        target_project = project_id or self.project_id
        
        # Inject memory context into system instruction
        base_instruction = system_instruction or "You are a helpful GCP Voice AI Assistant."
        memory_context = self.memory_orchestrator.get_full_context_prompt_injection()
        full_instruction = f"{base_instruction}\n{memory_context}"

        if provider_type == "aistudio":
            if not api_key:
                raise ValueError("GEMINI_API_KEY is required for Google AI Studio provider.")
            self.client = AIStudioLiveClient(api_key=api_key, model_name=model_name, system_instruction=full_instruction)
        elif provider_type == "vertex":
            self.client = VertexAILiveClient(project_id=target_project, model_name=model_name, system_instruction=full_instruction)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        logger.info(f"Initialized Voice Session [{self.session_id}] with Provider [{provider_type}] and Memory Injection")
        return self.client

    def handle_barge_in(self) -> Dict[str, Any]:
        """Triggered when user speaks over agent audio response."""
        self.is_interrupted = True
        self.active_turn_id += 1
        logger.info(f"Barge-in detected on Session [{self.session_id}]. Advancing turn ID to {self.active_turn_id}")
        return {"session_id": self.session_id, "interrupted": True, "new_turn_id": self.active_turn_id}

    async def close_session(self) -> bool:
        """Gracefully close session and persist state/memory."""
        if self.client:
            await self.client.disconnect()
        return await self.memory_orchestrator.finalize_session()
