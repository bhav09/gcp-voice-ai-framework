import sys
import os
import pytest
import asyncio

# Ensure template root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config.settings import settings
from src.core.session_manager import VoiceSessionManager
from src.core.audio_pipeline import AudioPipeline
from src.tools.dispatcher import ToolDispatcher
from src.tools.base_tool import BaseVoiceTool
from pydantic import BaseModel, Field

class SampleArgs(BaseModel):
    location: str = Field(description="City name")

class SampleTool(BaseVoiceTool):
    name = "get_weather"
    description = "Get current weather"
    args_schema = SampleArgs

    async def execute(self, location: str):
        return {"location": location, "temp": "72F"}

def test_settings_initialization():
    assert settings.gcp_project_id == "gen-demo-66-20250711"
    assert settings.provider_type in ["vertex", "aistudio"]

def test_audio_pipeline_vad():
    pipeline = AudioPipeline()
    # 0x0000 PCM is silent
    silent_pcm = b"\x00\x00" * 512
    assert pipeline.calculate_rms_energy(silent_pcm) == 0.0
    assert not pipeline.is_speech_active(silent_pcm)

def test_session_manager_provider_factory():
    manager = VoiceSessionManager()
    vertex_client = manager.create_client(provider_type="vertex", project_id="gen-demo-66-20250711")
    assert vertex_client is not None
    assert vertex_client.model_name == "gemini-2.0-flash-exp"

@pytest.mark.asyncio
async def test_tool_dispatcher():
    dispatcher = ToolDispatcher()
    tool = SampleTool()
    dispatcher.register_tool(tool)
    
    declarations = dispatcher.get_tool_declarations()
    assert len(declarations) == 1
    assert declarations[0]["name"] == "get_weather"
    
    res = await dispatcher.execute_tool("get_weather", {"location": "San Francisco"})
    assert res["status"] == "success"
    assert res["result"]["location"] == "San Francisco"

if __name__ == "__main__":
    pytest.main([__file__])
