import time
import asyncio
import logging
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger("CircuitBreaker")

class CircuitState(Enum):
    CLOSED = "CLOSED"      # Normal operational state
    OPEN = "OPEN"          # Failing state; block calls and use fallback
    HALF_OPEN = "HALF_OPEN"# Testing recovery state

class CircuitBreakerOpenException(Exception):
    """Exception raised when calling a service protected by an open circuit breaker."""
    pass

class CircuitBreaker:
    """State machine circuit breaker for GCP service tools to prevent cascading failures."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout_sec: float = 30.0,
        half_open_max_trials: int = 2
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.half_open_max_trials = half_open_max_trials
        
        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.success_count: int = 0
        self.last_failure_time: float = 0.0
        self._half_open_in_flight: int = 0
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., Any], *args: Any, fallback: Optional[Callable[..., Any]] = None, **kwargs: Any) -> Any:
        """Executes a call wrapped in circuit breaker protection."""
        async with self._lock:
            now = time.time()

            if self.state == CircuitState.OPEN:
                if now - self.last_failure_time > self.recovery_timeout_sec:
                    logger.info(f"Circuit Breaker [{self.name}] transitioning from OPEN -> HALF_OPEN for trial execution.")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    self._half_open_in_flight = 0
                else:
                    logger.warning(f"Circuit Breaker [{self.name}] is OPEN. Blocking execution.")
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(f"Service [{self.name}] circuit breaker is OPEN")

            # In HALF_OPEN, limit concurrent trial calls
            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_in_flight >= self.half_open_max_trials:
                    logger.warning(f"Circuit Breaker [{self.name}] HALF_OPEN trial limit reached. Blocking additional calls.")
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(f"Service [{self.name}] circuit breaker HALF_OPEN trial limit reached")
                self._half_open_in_flight += 1

        # Execute outside lock to allow concurrency
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as exc:
            await self._on_failure(exc)
            if fallback:
                return await fallback(*args, **kwargs)
            raise exc

    async def _on_success(self):
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self._half_open_in_flight = max(0, self._half_open_in_flight - 1)
                self.success_count += 1
                if self.success_count >= self.half_open_max_trials:
                    logger.info(f"Circuit Breaker [{self.name}] recovered! HALF_OPEN -> CLOSED")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self._half_open_in_flight = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    async def _on_failure(self, exc: Exception):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            logger.error(f"Circuit Breaker [{self.name}] recorded failure #{self.failure_count}: {exc}")
            
            if self.state == CircuitState.HALF_OPEN:
                # Any failure in HALF_OPEN immediately trips back to OPEN
                self._half_open_in_flight = max(0, self._half_open_in_flight - 1)
                logger.error(f"Circuit Breaker [{self.name}] HALF_OPEN trial failed. HALF_OPEN -> OPEN")
                self.state = CircuitState.OPEN
                self.failure_count = 0  # Reset for next recovery cycle
            elif self.failure_count >= self.failure_threshold:
                logger.error(f"Circuit Breaker [{self.name}] threshold reached. CLOSED -> OPEN")
                self.state = CircuitState.OPEN
