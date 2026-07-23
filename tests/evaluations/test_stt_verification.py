import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.evaluations.stt_verifier import STTVoiceVerifier

@pytest.mark.asyncio
async def test_stt_voice_output_verification():
    verifier = STTVoiceVerifier(project_id="gen-demo-66-20250711")
    
    # 24kHz PCM sample bytes
    sample_pcm = b"\x00\x00\x10\x00" * 240
    
    res = await verifier.verify_voice_output_accuracy(
        pcm_output_bytes=sample_pcm,
        expected_phrase="Gemini Live voice assistant response transcript.",
        sample_rate=24000
    )
    
    assert "word_error_rate" in res
    assert res["status"] == "PASSED"
    assert res["is_matched"] is True

if __name__ == "__main__":
    pytest.main([__file__])
