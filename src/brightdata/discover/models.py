"""Models for Discover API results and jobs."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, TYPE_CHECKING

from ..models import BaseResult

if TYPE_CHECKING:
    from .service import DiscoverService


@dataclass
class DiscoverResult(BaseResult):
    """
    Result from a Discover API search.

    Contains AI-ranked web search results with relevance scores
    and optional full-page content.

    Attributes:
        query: Original search query.
        intent: Intent description used for relevance ranking.
        data: List of result dicts with link, title, description, relevance_score, content.
        duration_seconds: Server-side processing duration.
        total_results: Number of results returned.
        task_id: Discover API task identifier.
    """

    query: str = ""
    intent: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    duration_seconds: Optional[float] = None
    total_results: Optional[int] = None
    task_id: Optional[str] = None

    def __repr__(self) -> str:
        """String representation with query info."""
        base_repr = super().__repr__()
        query_str = self.query[:50] + "..." if len(self.query) > 50 else self.query
        total_str = f" results={self.total_results}" if self.total_results else ""
        return f"<DiscoverResult {base_repr} query={query_str!r}{total_str}>"


@dataclass
class DiscoverJob:
    """
    Handle for a pending Discover API search.

    Created by discover_trigger(), allows manual polling and fetching.

    Example:
        >>> job = await client.discover_trigger(
        ...     query="market research SaaS pricing",
        ...     intent="competitor pricing strategies",
        ... )
        >>> print(f"Task ID: {job.task_id}")
        >>> await job.wait(timeout=60)
        >>> data = await job.fetch()
    """

    task_id: str
    _service: "DiscoverService" = field(repr=False)
    query: str = ""
    intent: Optional[str] = None

    def __repr__(self) -> str:
        return f"<DiscoverJob task_id={self.task_id[:16]}...>"

    async def status(self) -> str:
        """
        Check task status.

        Returns:
            'processing' or 'done'
        """
        response_data = await self._service._poll_once(self.task_id)
        return response_data.get("status", "processing")

    async def wait(self, timeout: int = 60, poll_interval: int = 2) -> str:
        """
        Poll until done or timeout.

        Args:
            timeout: Maximum seconds to wait.
            poll_interval: Seconds between status checks.

        Returns:
            Final status string.

        Raises:
            TimeoutError: If timeout is reached.
            APIError: If task fails.
        """
        from ..exceptions import APIError

        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(f"Discover task {self.task_id} timed out after {timeout}s")

            response_data = await self._service._poll_once(self.task_id)
            status = response_data.get("status", "processing")

            if status == "done":
                self._last_response = response_data
                return status
            elif status in ("error", "failed"):
                raise APIError(f"Discover task {self.task_id} failed with status: {status}")

            await asyncio.sleep(poll_interval)

    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch results. Call after wait() returns 'done'.

        Returns:
            List of result dicts.
        """
        if hasattr(self, "_last_response") and self._last_response.get("status") == "done":
            return self._last_response.get("results", [])

        response_data = await self._service._poll_once(self.task_id)
        return response_data.get("results", [])

    async def to_result(self, timeout: int = 60, poll_interval: int = 2) -> DiscoverResult:
        """
        Wait + fetch + wrap in DiscoverResult.

        Args:
            timeout: Maximum seconds to wait.
            poll_interval: Seconds between status checks.

        Returns:
            DiscoverResult with full data.
        """
        from datetime import datetime, timezone

        start_time = datetime.now(timezone.utc)

        try:
            await self.wait(timeout=timeout, poll_interval=poll_interval)
            results = await self.fetch()
            end_time = datetime.now(timezone.utc)

            return DiscoverResult(
                success=True,
                query=self.query,
                intent=self.intent,
                data=results,
                total_results=len(results),
                task_id=self.task_id,
                trigger_sent_at=start_time,
                data_fetched_at=end_time,
            )
        except Exception as e:
            return DiscoverResult(
                success=False,
                query=self.query,
                intent=self.intent,
                error=str(e),
                task_id=self.task_id,
                trigger_sent_at=start_time,
                data_fetched_at=datetime.now(timezone.utc),
            )
