import sys
import os
import pytest
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.evaluations.llm_judge import LLMJudgeEvaluator
from src.evaluations.acoustic_metrics import AcousticEvaluator

@pytest.mark.asyncio
async def test_llm_judge_groundedness():
    judge = LLMJudgeEvaluator()
    doc_context = ["GCP Vertex AI provides Gemini Live WebSockets support in us-central1."]
    res = await judge.evaluate_groundedness(
        agent_response="Gemini Live is available via Vertex AI WebSockets in us-central1.",
        context_documents=doc_context
    )
    assert res["passed"] is True
    assert res["score"] >= 0.80

def test_word_error_rate_calculation():
    evaluator = AcousticEvaluator()
    ref = "Welcome to Google Cloud Vertex AI"
    hyp = "Welcome to Google Cloud Vertex AI"
    wer = evaluator.calculate_wer(ref, hyp)
    assert wer == 0.0
    
    hyp_err = "Welcome to Google Cloud Vertex"
    wer_err = evaluator.calculate_wer(ref, hyp_err)
    assert wer_err > 0.0

def test_latency_sla_percentiles():
    evaluator = AcousticEvaluator(latency_target_ms=800.0)
    compliant_latencies = [450.0, 520.0, 610.0, 780.0, 510.0, 640.0, 590.0, 700.0, 750.0, 680.0]
    metrics = evaluator.evaluate_latency_sla(compliant_latencies)
    assert metrics["sla_compliant"] is True
    assert metrics["p95_latency_ms"] <= 800.0

    non_compliant_latencies = [450.0, 520.0, 610.0, 780.0, 890.0, 640.0, 590.0, 700.0, 750.0, 680.0]
    metrics_fail = evaluator.evaluate_latency_sla(non_compliant_latencies)
    assert metrics_fail["sla_compliant"] is False

if __name__ == "__main__":
    pytest.main([__file__])
