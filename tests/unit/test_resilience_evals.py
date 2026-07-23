import pytest
import asyncio
from src.resilience.rate_limiter import TokenBucketRateLimiter
from src.resilience.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpenException
from src.resilience.retry_policy import async_retry_with_backoff
from src.evaluations.tool_evaluator import ToolEvaluator

@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = TokenBucketRateLimiter(max_tokens=2, refill_period_sec=60.0)
    assert await limiter.acquire("test_session", 1) is True
    assert await limiter.acquire("test_session", 1) is True
    assert await limiter.acquire("test_session", 1) is False

@pytest.mark.asyncio
async def test_circuit_breaker():
    cb = CircuitBreaker(name="test_cb", failure_threshold=2, recovery_timeout_sec=0.1)
    
    async def failing_call():
        raise ValueError("Service down")

    async def fallback_call():
        return "fallback_result"

    with pytest.raises(ValueError):
        await cb.call(failing_call)
    
    # Second failure triggers OPEN
    result = await cb.call(failing_call, fallback=fallback_call)
    assert result == "fallback_result"
    assert cb.state == CircuitState.OPEN

@pytest.mark.asyncio
async def test_async_retry_policy():
    attempts = 0

    @async_retry_with_backoff(max_retries=3, initial_delay_sec=0.01)
    async def flaky_function():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise RuntimeError("Transient network issue")
        return "success"

    res = await flaky_function()
    assert res == "success"
    assert attempts == 2

def test_tool_evaluator_rag_citations():
    evaluator = ToolEvaluator()
    sample_payload = {
        "status": "SUCCESS",
        "results": [
            {
                "corpus_id": "corpus-fin-001",
                "document_uri": "gs://bucket/annual_report.pdf",
                "id": "doc-999",
                "score": 0.98,
                "snippet": "Q3 Revenue increased by 14%."
            }
        ]
    }
    
    eval_res = evaluator.evaluate_tool_execution(
        tool_name="query_knowledge_base",
        execution_time_ms=120.5,
        result_payload=sample_payload,
        expected_schema_keys=["results"]
    )
    
    assert eval_res.is_schema_valid is True
    assert len(eval_res.source_citations) == 1
    assert eval_res.source_citations[0].corpus_id == "corpus-fin-001"
    assert eval_res.source_citations[0].document_uri == "gs://bucket/annual_report.pdf"
