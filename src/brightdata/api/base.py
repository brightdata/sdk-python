"""Base API class for all API implementations."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any
from ..core.engine import AsyncEngine


class BaseAPI(ABC):
    """
    Base class for all API implementations.

    Provides common structure and async/sync wrapper pattern
    for all API service classes.
    """

    def __init__(self, engine: AsyncEngine):
        """
        Initialize base API.

        Args:
            engine: AsyncEngine instance for HTTP operations.
        """
        self.engine = engine

    @abstractmethod
    async def _execute_async(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute API operation asynchronously.

        This method should be implemented by subclasses to perform
        the actual async API operation.
        """
        pass

    def _execute_sync(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute API operation synchronously.

        Wraps async method using asyncio.run() for sync compatibility.
        Properly manages engine context.
        """
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot call sync method from async context. Use async method instead."
            )
        except RuntimeError:

            async def _run():
                async with self.engine:
                    return await self._execute_async(*args, **kwargs)

            return asyncio.run(_run())
