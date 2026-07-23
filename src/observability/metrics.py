import time
import logging
from typing import Dict, Any

logger = logging.getLogger("VoiceMetricsCollector")

class VoiceMetricsCollector:
    """Latency, SLA, and Token throughput metrics aggregator."""

    def __init__(self, target_sla_ms: float = 800.0):
        self.target_sla_ms = target_sla_ms
        self._turn_start_times: Dict[int, float] = {}
        self.ttft_records_ms: list[float] = []
        self.total_input_audio_seconds: float = 0.0
        self.total_output_audio_seconds: float = 0.0

    def record_turn_start(self, turn_id: int) -> None:
        """Mark user speech completion / turn start timestamp."""
        self._turn_start_times[turn_id] = time.perf_counter()

    def record_first_audio_token(self, turn_id: int) -> float:
        """Calculate Time to First Audio Token (TTFT) in milliseconds."""
        if turn_id in self._turn_start_times:
            elapsed_ms = (time.perf_counter() - self._turn_start_times[turn_id]) * 1000.0
            self.ttft_records_ms.append(elapsed_ms)
            is_sla_met = elapsed_ms <= self.target_sla_ms
            logger.info(f"Turn [{turn_id}] TTFT: {elapsed_ms:.2f} ms (SLA <= {self.target_sla_ms}ms Met: {is_sla_met})")
            return elapsed_ms
        return 0.0

    def record_audio_duration(self, input_sec: float = 0.0, output_sec: float = 0.0) -> None:
        self.total_input_audio_seconds += input_sec
        self.total_output_audio_seconds += output_sec

    def get_summary(self) -> Dict[str, Any]:
        avg_ttft = sum(self.ttft_records_ms) / len(self.ttft_records_ms) if self.ttft_records_ms else 0.0
        return {
            "total_turns": len(self.ttft_records_ms),
            "average_ttft_ms": round(avg_ttft, 2),
            "total_input_audio_sec": round(self.total_input_audio_seconds, 2),
            "total_output_audio_sec": round(self.total_output_audio_seconds, 2),
            "target_sla_ms": self.target_sla_ms
        }
