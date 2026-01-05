"""Base API class for all API implementations."""

from abc import ABC, abstractmethod
from typing import Any
from ..core.engine import AsyncEngine


class BaseAPI(ABC):
    """
    Base class for all API implementations.

    Provides common structure for all API service classes.
    All methods are async-only. For sync usage, use SyncBrightDataClient.
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
