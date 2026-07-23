import asyncio
import random
import logging
from functools import wraps
from typing import Callable, Any, Type

logger = logging.getLogger("RetryPolicy")

def async_retry_with_backoff(
    max_retries: int = 3,
    initial_delay_sec: float = 0.5,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """Async decorator for exponential backoff retries with full jitter for GCP API calls and WebSockets reconnects."""
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay_sec
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as exc:
                    if attempt == max_retries:
                        logger.error(f"Function [{func.__name__}] failed after {max_retries} attempts: {exc}")
                        raise exc
                    
                    sleep_time = delay * (random.uniform(0.8, 1.2) if jitter else 1.0)
                    logger.warning(f"Attempt #{attempt} for [{func.__name__}] failed ({exc}). Retrying in {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
                    delay *= backoff_factor
        return wrapper
    return decorator
