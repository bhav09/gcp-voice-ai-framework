import time
import asyncio
import logging
from typing import Dict, Tuple

logger = logging.getLogger("RateLimiter")

class TokenBucketRateLimiter:
    """Sliding-window token bucket rate limiter for voice session turns and tool execution API calls."""

    def __init__(self, max_tokens: int = 60, refill_period_sec: float = 60.0):
        self.max_tokens = max_tokens
        self.refill_period_sec = refill_period_sec
        self.buckets: Dict[str, Tuple[float, float]] = {}  # key -> (tokens, last_update)
        self._lock = asyncio.Lock()

    async def acquire(self, key: str, tokens: int = 1) -> bool:
        """Acquires tokens for a given key (session or client ID). Returns True if allowed, False if rate limited."""
        async with self._lock:
            now = time.time()
            if key not in self.buckets:
                self.buckets[key] = (float(self.max_tokens - tokens), now)
                return True

            current_tokens, last_update = self.buckets[key]
            # Calculate refilled tokens based on elapsed time
            elapsed = now - last_update
            refill_rate = self.max_tokens / self.refill_period_sec
            new_tokens = min(float(self.max_tokens), current_tokens + (elapsed * refill_rate))

            if new_tokens >= tokens:
                self.buckets[key] = (new_tokens - tokens, now)
                return True
            else:
                logger.warning(f"Rate limit exceeded for key [{key}]. Available: {new_tokens:.2f}, Required: {tokens}")
                return False
