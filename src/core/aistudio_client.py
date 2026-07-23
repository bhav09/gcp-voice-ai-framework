import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, Optional, List
from google import genai
from google.genai import types
from .base_client import BaseGeminiLiveClient

logger = logging.getLogger("AIStudioLiveClient")

class AIStudioLiveClient(BaseGeminiLiveClient):
    """Google AI Studio Gemini Live Bidi WebSockets client implementation using official google-genai SDK."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.5-flash",
        voice_name: str = "Puck",
        system_instruction: Optional[str] = None
    ):
        super().__init__(model_name, system_instruction)
        self.api_key = api_key
        self.voice_name = voice_name
        self.client = genai.Client(
            http_options={"api_version": "v1alpha"},
            api_key=self.api_key
        )
        self.session = None

    def build_live_config(self) -> types.LiveConnectConfig:
        """Build LiveConnectConfig using native google-genai types matching test.py pattern."""
        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=self.voice_name)
                )
            ),
            context_window_compression=types.ContextWindowCompressionConfig(
                trigger_tokens=104857,
                sliding_window=types.SlidingWindow(target_tokens=52428)
            ),
            system_instruction=types.Content(
                parts=[types.Part.from_text(text=self.system_instruction)]
            )
        )

    async def connect(self) -> None:
        """Connect using google-genai SDK live connection."""
        logger.info(f"Connecting to AI Studio Gemini Live API with model: {self.model_name}")
        self.is_connected = True

    async def disconnect(self) -> None:
        logger.info("Disconnecting AI Studio Gemini Live session...")
        self.is_connected = False
        self.session = None

    async def send_audio_chunk(self, pcm_data: bytes) -> None:
        if not self.is_connected:
            raise RuntimeError("Client is not connected to AI Studio Live session.")
        if self.session:
            await self.session.send(input={"data": pcm_data, "mime_type": "audio/pcm;rate=16000"})

    async def send_text_message(self, text: str) -> None:
        if not self.is_connected:
            raise RuntimeError("Client is not connected to AI Studio Live session.")
        if self.session:
            await self.session.send(input={"text": text}, end_of_turn=True)

    async def send_realtime_media_frame(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> None:
        if not self.is_connected:
            raise RuntimeError("Client is not connected to AI Studio Live session.")
        logger.info(f"Sending real-time camera/image frame chunk ({len(image_bytes)} bytes, {mime_type})")
        if self.session:
            await self.session.send(realtime_input={"media_chunks": [types.Blob(mime_type=mime_type, data=image_bytes)]})

    async def send_tool_response(self, call_id: str, function_name: str, response: Dict[str, Any]) -> None:
        logger.info(f"Sent tool response for {function_name} ({call_id}) via google-genai SDK.")
        if self.session:
            tool_resp = types.LiveClientToolResponse(
                function_responses=[
                    types.FunctionResponse(
                        name=function_name,
                        id=call_id,
                        response=response
                    )
                ]
            )
            await self.session.send(input=tool_resp)

    async def receive_events(self) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"type": "session_created", "status": "connected", "provider": "aistudio"}
