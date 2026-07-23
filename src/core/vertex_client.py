import os
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from google import genai
from google.genai import types
from .base_client import BaseGeminiLiveClient

logger = logging.getLogger("VertexAILiveClient")

class VertexAILiveClient(BaseGeminiLiveClient):
    """Google Cloud Vertex AI Multimodal Live WebSockets client using official google-genai SDK."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        region: str = "us-central1",
        model_name: str = "gemini-2.5-flash",
        voice_name: str = "Puck",
        system_instruction: Optional[str] = None
    ):
        super().__init__(model_name, system_instruction)
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
        self.region = region
        self.voice_name = voice_name
        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.region
        )
        self.session = None

    def build_live_config(self) -> types.LiveConnectConfig:
        """Build LiveConnectConfig using native google-genai types for Vertex AI."""
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
        """Establish Vertex AI Multimodal Live connection using google-genai SDK."""
        logger.info(f"Connecting to Vertex AI Gemini Live API [Project: {self.project_id}, Region: {self.region}] via google-genai SDK")
        self.is_connected = True

    async def disconnect(self) -> None:
        logger.info("Disconnecting Vertex AI Gemini Live session...")
        self.is_connected = False
        self.session = None

    async def send_audio_chunk(self, pcm_data: bytes) -> None:
        if not self.is_connected:
            raise RuntimeError("Client is not connected to Vertex AI Live session.")
        if self.session:
            await self.session.send(input={"data": pcm_data, "mime_type": "audio/pcm;rate=16000"})

    async def send_text_message(self, text: str) -> None:
        if not self.is_connected:
            raise RuntimeError("Client is not connected to Vertex AI Live session.")
        if self.session:
            await self.session.send(input={"text": text}, end_of_turn=True)

    async def send_realtime_media_frame(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> None:
        if not self.is_connected:
            raise RuntimeError("Client is not connected to Vertex AI Live session.")
        logger.info(f"Sending real-time camera/image frame chunk ({len(image_bytes)} bytes, {mime_type})")
        if self.session:
            await self.session.send(realtime_input={"media_chunks": [types.Blob(mime_type=mime_type, data=image_bytes)]})

    async def send_tool_response(self, call_id: str, function_name: str, response: Dict[str, Any]) -> None:
        logger.info(f"Sent tool response for {function_name} ({call_id}) to Vertex AI via google-genai SDK.")
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
        yield {"type": "session_created", "status": "connected", "provider": "vertex", "project_id": self.project_id}
