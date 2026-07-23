import logging
from typing import Dict, Any, List

logger = logging.getLogger("AcousticEvaluator")

class AcousticEvaluator:
    """Acoustic Quality, NISQA speech quality, Word Error Rate (WER), and Latency SLA Evaluator."""

    def __init__(self, latency_target_ms: float = 800.0):
        self.latency_target_ms = latency_target_ms

    def calculate_wer(self, reference_text: str, hypothesis_text: str) -> float:
        """Calculate Word Error Rate (WER) between reference transcript and generated speech transcript."""
        ref_words = reference_text.lower().split()
        hyp_words = hypothesis_text.lower().split()
        
        if not ref_words:
            return 0.0 if not hyp_words else 1.0

        # Simple Levenshtein distance on words
        d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
        for i in range(len(ref_words) + 1):
            d[i][0] = i
        for j in range(len(hyp_words) + 1):
            d[0][j] = j
            
        for i in range(1, len(ref_words) + 1):
            for j in range(1, len(hyp_words) + 1):
                cost = 0 if ref_words[i-1] == hyp_words[j-1] else 1
                d[i][j] = min(
                    d[i-1][j] + 1,      # deletion
                    d[i][j-1] + 1,      # insertion
                    d[i-1][j-1] + cost  # substitution
                )
                
        wer = d[len(ref_words)][len(hyp_words)] / len(ref_words)
        return round(wer, 4)

    def evaluate_latency_sla(self, latency_records_ms: List[float]) -> Dict[str, Any]:
        """Compute p50, p95, and p99 latency percentiles against target SLA."""
        if not latency_records_ms:
            return {"status": "no_data"}

        sorted_recs = sorted(latency_records_ms)
        n = len(sorted_recs)
        p50 = sorted_recs[int(n * 0.50)]
        p95 = sorted_recs[min(int(n * 0.95), n - 1)]
        p99 = sorted_recs[min(int(n * 0.99), n - 1)]

        return {
            "sample_count": n,
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "p99_latency_ms": round(p99, 2),
            "sla_target_ms": self.latency_target_ms,
            "sla_compliant": p95 <= self.latency_target_ms
        }
