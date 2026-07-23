import sys
import os
import pytest
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.session_manager import VoiceSessionManager
from src.core.audio_pipeline import AudioPipeline
from src.observability.metrics import VoiceMetricsCollector

@pytest.mark.asyncio
async def test_synthetic_voice_session_flow():
    manager = VoiceSessionManager(session_id="synth-e2e-001")
    client = manager.create_client(provider_type="vertex")
    
    await client.connect()
    assert client.is_connected
    
    pipeline = AudioPipeline()
    metrics = VoiceMetricsCollector(target_sla_ms=800.0)
    
    # Simulate turn start
    turn_id = 1
    metrics.record_turn_start(turn_id)
    
    # Feed synthetic audio frame (PCM 16kHz)
    synthetic_pcm_frame = b"\x10\x00\x20\x00" * 256
    pipeline.append_input_pcm(synthetic_pcm_frame)
    
    await client.send_audio_chunk(synthetic_pcm_frame)
    
    # Simulate receipt of first audio token from Gemini Live
    ttft_ms = metrics.record_first_audio_token(turn_id)
    assert ttft_ms >= 0.0
    
    # Test barge-in interruption handling
    barge_in_res = manager.handle_barge_in()
    assert barge_in_res["interrupted"] is True
    pipeline.clear_buffer()
    
    await client.disconnect()
    assert not client.is_connected

if __name__ == "__main__":
    pytest.main([__file__])
