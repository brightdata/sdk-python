"""
Scraper Studio Service - High-level interface for Scraper Studio operations.

Provides run/trigger/status/fetch methods following the same pattern as
ScrapeService and SearchService.

All methods are async-only. For sync usage, use SyncBrightDataClient.
"""

from typing import Dict, List, Any, Union, TYPE_CHECKING

from .client import ScraperStudioAPIClient
from .models import ScraperStudioJob, JobStatus
from ..constants import SCRAPER_STUDIO_DEFAULT_TIMEOUT, SCRAPER_STUDIO_POLL_INTERVAL

if TYPE_CHECKING:
    from ..client import BrightDataClient


class ScraperStudioService:
    """
    High-level service for Scraper Studio operations.

    Access via client.scraper_studio:

        >>> async with BrightDataClient() as client:
        ...     # High-level: trigger + poll + return data
        ...     data = await client.scraper_studio.run(
        ...         collector="c_abc123",
        ...         input={"url": "https://example.com/1"},
        ...     )
        ...
        ...     # Manual control: trigger, then fetch later
        ...     job = await client.scraper_studio.trigger(
        ...         collector="c_abc123",
        ...         input={"url": "https://example.com/1"},
        ...     )
        ...     data = await job.wait_and_fetch(timeout=120)
    """

    def __init__(self, client: "BrightDataClient"):
        self._client = client
        self._api = ScraperStudioAPIClient(client.engine)

    async def run(
        self,
        collector: str,
        input: Union[Dict[str, Any], List[Dict[str, Any]]],
        timeout: int = SCRAPER_STUDIO_DEFAULT_TIMEOUT,
        poll_interval: int = SCRAPER_STUDIO_POLL_INTERVAL,
    ) -> List[Dict[str, Any]]:
        """
        Trigger a scrape and wait for results.

        High-level method that handles trigger + poll + return.
        Uses trigger_immediate internally.

        Args:
            collector: Scraper collector ID (e.g., "c_abc123").
            input: Single input dict or list of input dicts.
                   Each dict contains scraper-specific fields (e.g., {"url": "..."}).
            timeout: Maximum seconds to wait for results.
            poll_interval: Seconds between poll attempts.

        Returns:
            List of scraped records.

        Raises:
            TimeoutError: If timeout is reached before data is ready.
            APIError: If the API request fails.
        """
        # Normalize list input to individual triggers
        if isinstance(input, list):
            # Trigger each input separately and collect results
            all_data: List[Dict[str, Any]] = []
            for single_input in input:
                response_id = await self._api.trigger_immediate(collector, single_input)
                job = ScraperStudioJob(response_id=response_id, api_client=self._api)
                data = await job.wait_and_fetch(timeout=timeout, poll_interval=poll_interval)
                all_data.extend(data)
            return all_data
        else:
            response_id = await self._api.trigger_immediate(collector, input)
            job = ScraperStudioJob(response_id=response_id, api_client=self._api)
            return await job.wait_and_fetch(timeout=timeout, poll_interval=poll_interval)

    async def trigger(
        self,
        collector: str,
        input: Dict[str, Any],
    ) -> ScraperStudioJob:
        """
        Trigger a scrape and return a job object for manual control.

        Does not wait for results. Use job.wait_and_fetch() or job.fetch()
        to retrieve data later.

        Args:
            collector: Scraper collector ID.
            input: Single input dict with scraper-specific fields.

        Returns:
            ScraperStudioJob with response_id for polling.

        Raises:
            APIError: If the trigger request fails.
        """
        response_id = await self._api.trigger_immediate(collector, input)
        return ScraperStudioJob(response_id=response_id, api_client=self._api)

    async def status(
        self,
        job_id: str,
    ) -> JobStatus:
        """
        Check the status of a job.

        Args:
            job_id: Job ID (e.g., "j_abc123").

        Returns:
            JobStatus with status, success_rate, lines, etc.

        Raises:
            APIError: If the status request fails.
        """
        raw = await self._api.get_status(job_id)
        return JobStatus.from_api_response(raw)

    async def fetch(
        self,
        response_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetch results of a completed scrape.

        Args:
            response_id: Response ID from trigger().

        Returns:
            List of scraped records.

        Raises:
            DataNotReadyError: If data is not ready yet.
            APIError: If the fetch request fails.
        """
        return await self._api.fetch_immediate_result(response_id)
