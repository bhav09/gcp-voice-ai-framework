from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Callable, Optional, List

class BaseGeminiLiveClient(ABC):
    """Abstract base class for Gemini Live (Multimodal Live WebSockets/Bidi) client implementations."""

    def __init__(self, model_name: str, system_instruction: Optional[str] = None):
        self.model_name = model_name
        self.system_instruction = system_instruction or "You are a helpful GCP Voice AI Assistant."
        self.is_connected = False
        self.tools: List[Dict[str, Any]] = []

    @abstractmethod
    async def connect(self) -> None:
        """Establish bidirectional WebSocket connection to Gemini Live endpoint."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close WebSocket connection gracefully."""
        pass

    @abstractmethod
    async def send_audio_chunk(self, pcm_data: bytes) -> None:
        """Send raw PCM 16kHz audio frame to the live stream."""
        pass

    @abstractmethod
    async def send_text_message(self, text: str) -> None:
        """Send text message frame to the live stream."""
        pass

    @abstractmethod
    async def send_tool_response(self, call_id: str, function_name: str, response: Dict[str, Any]) -> None:
        """Return function call execution result back to Gemini Live."""
        pass

    @abstractmethod
    async def receive_events(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream events (audio chunks, text transcript, function call requests) received from Gemini Live."""
        pass
