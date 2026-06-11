"""Retry utilities with exponential backoff."""

import asyncio
import logging
from typing import TypeVar, Callable, Any
from functools import wraps

logger = logging.getLogger("localresearcher.retry")

T = TypeVar("T")


class RetryError(Exception):
    """Raised when all retry attempts fail."""
    pass


async def retry_async(
    func: Callable[..., Any],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Any:
    """Retry an async function with exponential backoff."""
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            
            if attempt < max_attempts - 1:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_attempts} attempts failed")
    
    raise RetryError(f"Failed after {max_attempts} attempts") from last_exception


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """Decorator for async functions to add retry logic."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_async(
                lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                backoff_factor=backoff_factor,
                exceptions=exceptions,
            )
        return wrapper
    return decorator