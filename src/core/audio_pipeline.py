import math
import struct
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger("AudioPipeline")

class AudioPipeline:
    """PCM Audio Resampler, Silence/VAD Detector, and Jitter Ring Buffer Manager."""

    def __init__(self, input_rate: int = 16000, output_rate: int = 24000, pcm_width: int = 2):
        self.input_rate = input_rate
        self.output_rate = output_rate
        self.pcm_width = pcm_width
        self._buffer = bytearray()
        self.silence_threshold_rms = 100.0  # RMS energy threshold for VAD

    def append_input_pcm(self, pcm_bytes: bytes) -> None:
        """Append raw PCM audio frame to the input stream buffer."""
        self._buffer.extend(pcm_bytes)

    def calculate_rms_energy(self, pcm_bytes: bytes) -> float:
        """Calculate Root Mean Square (RMS) energy level of PCM 16-bit audio chunk for Voice Activity Detection (VAD)."""
        if not pcm_bytes or len(pcm_bytes) % 2 != 0:
            return 0.0
        
        num_samples = len(pcm_bytes) // 2
        samples = struct.unpack(f"<{num_samples}h", pcm_bytes)
        sum_squares = sum(s ** 2 for s in samples)
        rms = math.sqrt(sum_squares / num_samples) if num_samples > 0 else 0.0
        return rms

    def is_speech_active(self, pcm_bytes: bytes) -> bool:
        """VAD check: Returns True if audio frame energy exceeds silence threshold."""
        return self.calculate_rms_energy(pcm_bytes) > self.silence_threshold_rms

    def resample_pcm_linear(self, pcm_bytes: bytes, source_rate: int = 16000, target_rate: int = 24000) -> bytes:
        """Linear interpolation resampler for PCM 16-bit mono audio streams."""
        if not pcm_bytes or source_rate == target_rate:
            return pcm_bytes
            
        num_source_samples = len(pcm_bytes) // 2
        source_samples = struct.unpack(f"<{num_source_samples}h", pcm_bytes)
        
        ratio = target_rate / source_rate
        num_target_samples = int(num_source_samples * ratio)
        target_samples = []

        for i in range(num_target_samples):
            src_index = i / ratio
            idx_low = int(src_index)
            idx_high = min(idx_low + 1, num_source_samples - 1)
            weight = src_index - idx_low
            
            sample_val = (1.0 - weight) * source_samples[idx_low] + weight * source_samples[idx_high]
            target_samples.append(int(max(-32768, min(32767, sample_val))))

        return struct.pack(f"<{len(target_samples)}h", *target_samples)

    def get_chunk(self, chunk_size_bytes: int = 1024) -> Optional[bytes]:
        """Extract a fixed-size chunk from the input audio buffer."""
        if len(self._buffer) >= chunk_size_bytes:
            chunk = bytes(self._buffer[:chunk_size_bytes])
            del self._buffer[:chunk_size_bytes]
            return chunk
        return None

    def clear_buffer(self) -> None:
        """Clear buffer immediately upon user barge-in / interruption event."""
        logger.info("Interruption triggered: Clearing audio pipeline buffer.")
        self._buffer.clear()
