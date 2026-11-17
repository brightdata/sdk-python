"""Retry logic with exponential backoff."""

import asyncio
from typing import Callable, Awaitable, TypeVar, Optional, List, Type
from ..exceptions import BrightDataError

T = TypeVar("T")


def is_retryable(exc: Exception) -> bool:
    """
    Decide whether repeating an operation is safe and worthwhile.

    Honor SDK errors' retryable flag, including explicit service policies.
    NetworkError defaults to retryable and plain built-in timeouts keep their
    legacy retry behavior. Other errors need an explicit retryable decision.
    A failed response does not prove that the server did not execute the work.
    RateLimitError stays non-retryable; callers can inspect retry_after.
    """
    if isinstance(exc, BrightDataError):
        return exc.retryable
    if isinstance(exc, TimeoutError):
        return True
    return False


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: Optional[List[Type[Exception]]] = None,
) -> T:
    """
    Retry function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for exponential backoff
        retryable_exceptions: Explicit exception-type override of the default
            retry policy. Supplying this list opts into retries for those types.

    Returns:
        Result from successful function call

    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    delay = initial_delay

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e

            # Check if exception is retryable
            if retryable_exceptions is None:
                if not is_retryable(e):
                    raise
            elif not any(isinstance(e, exc_type) for exc_type in retryable_exceptions):
                raise

            # Don't retry on last attempt
            if attempt >= max_retries:
                break

            # Wait before retrying
            await asyncio.sleep(min(delay, max_delay))
            delay *= backoff_factor

    raise last_exception
