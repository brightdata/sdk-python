"""
Data models for Scraper Studio API responses.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, TYPE_CHECKING

from ..exceptions import DataNotReadyError

if TYPE_CHECKING:
    from .client import ScraperStudioAPIClient


@dataclass
class JobStatus:
    """
    Job status returned by GET /dca/log/{job_id}.

    Attributes:
        id: Job identifier (e.g., "j_abc123")
        status: Job status ("queued", "running", "done", "failed", "cancelled")
        collector: Collector ID that ran this job
        inputs: Number of input records
        lines: Number of records collected
        fails: Number of failed records
        success_rate: Success rate (0.0 to 1.0)
        created: ISO timestamp when job was created
        started: ISO timestamp when job started processing
        finished: ISO timestamp when job finished
        job_time: Total job time in milliseconds
        queue_time: Time spent in queue in milliseconds
    """

    id: str
    status: str
    collector: str
    inputs: int = 0
    lines: int = 0
    fails: int = 0
    success_rate: float = 0.0
    created: str = ""
    started: Optional[str] = None
    finished: Optional[str] = None
    job_time: Optional[int] = None
    queue_time: Optional[int] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "JobStatus":
        """
        Create from API response.

        Handles mixed-case field names from the API (e.g., "Id", "Status", "Collector").
        """

        def _get(key: str) -> Any:
            """Try lowercase, then Title_case, then original key."""
            return data.get(key.lower(), data.get(key.title(), data.get(key)))

        return cls(
            id=_get("id") or "",
            status=_get("status") or "unknown",
            collector=_get("collector") or "",
            inputs=_get("inputs") or 0,
            lines=_get("lines") or 0,
            fails=_get("fails") or 0,
            success_rate=_get("success_rate") or data.get("Success_rate", 0.0),
            created=_get("created") or "",
            started=_get("started"),
            finished=_get("finished"),
            job_time=_get("job_time") or data.get("Job_time"),
            queue_time=_get("queue_time") or data.get("Queue_time"),
        )


class ScraperStudioJob:
    """
    A triggered Scraper Studio job.

    Returned by ScraperStudioService.trigger(). Holds the response_id
    and provides convenience methods to poll and fetch results.

    Same shape as ScrapeJob but wired to Scraper Studio endpoints.

    Example:
        >>> job = await client.scraper_studio.trigger(
        ...     collector="c_abc123",
        ...     input={"url": "https://example.com/1"},
        ... )
        >>> data = await job.wait_and_fetch(timeout=120)
    """

    def __init__(
        self,
        response_id: str,
        api_client: "ScraperStudioAPIClient",
    ):
        self.response_id = response_id
        self._api_client = api_client
        self._cached_data: Optional[List[Dict[str, Any]]] = None

    def __repr__(self) -> str:
        return f"<ScraperStudioJob response_id={self.response_id}>"

    async def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch results via GET /dca/get_result.

        Returns:
            List of scraped records.

        Raises:
            DataNotReadyError: If data is not ready yet (HTTP 202).
        """
        self._cached_data = await self._api_client.fetch_immediate_result(self.response_id)
        return self._cached_data

    async def wait_and_fetch(
        self,
        timeout: int = 300,
        poll_interval: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Poll fetch() until data arrives or timeout.

        Args:
            timeout: Maximum seconds to wait.
            poll_interval: Seconds between poll attempts.

        Returns:
            List of scraped records.

        Raises:
            TimeoutError: If timeout is reached before data is ready.
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                raise TimeoutError(f"Job {self.response_id} timed out after {timeout}s")

            try:
                return await self.fetch()
            except DataNotReadyError:
                await asyncio.sleep(poll_interval)
