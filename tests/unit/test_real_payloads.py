import sys
import os
import pytest
import json
import base64

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.aistudio_client import AIStudioLiveClient
from src.core.vertex_client import VertexAILiveClient
from src.core.audio_pipeline import AudioPipeline
from src.tools.base_tool import BaseVoiceTool
from pydantic import BaseModel, Field

class ComplexSchemaArgs(BaseModel):
    query: str = Field(description="Search string")
    max_results: int = Field(default=10, description="Max return count")
    filters: list[str] = Field(default=[], description="Filter category tags")

class ComplexTool(BaseVoiceTool):
    name = "complex_search_tool"
    description = "Executes search with nested parameters"
    args_schema = ComplexSchemaArgs

    async def execute(self, query: str, max_results: int = 10, filters: list = None):
        return {"query": query, "count": max_results}

def test_base64_audio_payload_generation():
    client = AIStudioLiveClient(api_key="TEST_KEY")
    live_config = client.build_live_config()
    
    assert live_config is not None
    assert live_config.response_modalities == ["AUDIO"]

def test_vertex_setup_payload_generation():
    client = VertexAILiveClient(project_id="gen-demo-66-20250711", region="us-central1")
    live_config = client.build_live_config()
    
    assert live_config is not None
    assert live_config.speech_config.voice_config.prebuilt_voice_config.voice_name == "Puck"

def test_recursive_pydantic_schema_converter():
    tool = ComplexTool()
    decl = tool.to_gemini_function_declaration()
    
    assert decl["name"] == "complex_search_tool"
    params = decl["parameters"]["properties"]
    assert params["query"]["type"] == "STRING"
    assert params["max_results"]["type"] == "INTEGER"
    assert params["filters"]["type"] == "ARRAY"

def test_pcm_linear_resampler():
    pipeline = AudioPipeline()
    pcm_16k = b"\x00\x10\x00\x20" * 100 # 200 samples at 16kHz
    pcm_24k = pipeline.resample_pcm_linear(pcm_16k, source_rate=16000, target_rate=24000)
    
    # Ratio 24000/16000 = 1.5 -> 200 samples * 1.5 = 300 samples (600 bytes)
    assert len(pcm_24k) == 600

if __name__ == "__main__":
    pytest.main([__file__])
