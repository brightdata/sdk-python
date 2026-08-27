"""Retry logic with exponential backoff."""

import asyncio
from typing import Callable, Awaitable, TypeVar, Optional, List, Type
from ..exceptions import BrightDataError, NetworkError

T = TypeVar("T")


def is_retryable(exc: Exception) -> bool:
    """
    Decide whether repeating an operation is safe and worthwhile.

    Retryability is NOT inferred from the exception type or from a missing
    status code. Several SDK errors are raised *after* the server accepted the
    work (e.g. "Failed to trigger scrape - no snapshot_id returned"), and
    repeating those creates a duplicate billed job. So anything raised without
    an explicit opinion defaults to not-retryable; only a raiser with enough
    knowledge -- currently the engine, for 5xx -- opts in.

    Rate limits are never retryable: on this API a 429 response itself consumes
    quota, so retrying extends the lockout. Use `retry_after` to pause instead.
    """
    if isinstance(exc, (NetworkError, TimeoutError)):
        return True
    if isinstance(exc, BrightDataError):
        return exc.retryable
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
        retryable_exceptions: List of exception types to retry on

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
