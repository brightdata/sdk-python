"""
Scrape Job - Represents a triggered scraping operation.

Provides convenient methods for checking status and fetching results
after triggering a scrape operation.

All methods are async-only. For sync usage, use SyncBrightDataClient.
"""

import asyncio
import time
from typing import Optional, Any
from datetime import datetime, timezone

from ..models import ScrapeResult
from ..exceptions import APIError
from ..constants import DEFAULT_POLL_INTERVAL
from .api_client import DatasetAPIClient


class ScrapeJob:
    """
    Represents a triggered scraping job.

    Provides methods to check status, wait for completion, and fetch results.
    Created by trigger methods and allows manual control over the scrape lifecycle.

    Example:
        >>> # Trigger and get job
        >>> job = await client.scrape.amazon.products_trigger(url)
        >>>
        >>> # Check status
        >>> status = await job.status()
        >>>
        >>> # Wait for completion
        >>> await job.wait(timeout=120)
        >>>
        >>> # Fetch results
        >>> data = await job.fetch()
        >>>
        >>> # Or get as ScrapeResult
        >>> result = await job.to_result()
    """

    def __init__(
        self,
        snapshot_id: str,
        api_client: DatasetAPIClient,
        platform_name: Optional[str] = None,
        cost_per_record: float = 0.001,
        triggered_at: Optional[datetime] = None,
    ):
        """
        Initialize scrape job.

        Args:
            snapshot_id: Bright Data snapshot identifier
            api_client: API client for status/fetch operations
            platform_name: Platform name (e.g., "amazon", "linkedin")
            cost_per_record: Cost per record for cost estimation
            triggered_at: When the job was triggered
        """
        self.snapshot_id = snapshot_id
        self._api_client = api_client
        self.platform_name = platform_name
        self.cost_per_record = cost_per_record
        self.triggered_at = triggered_at or datetime.now(timezone.utc)
        self._cached_status: Optional[str] = None
        self._cached_data: Optional[Any] = None

    def __repr__(self) -> str:
        """String representation."""
        platform = f"{self.platform_name} " if self.platform_name else ""
        return f"<ScrapeJob {platform}snapshot_id={self.snapshot_id[:12]}...>"

    # ============================================================================
    # ASYNC METHODS
    # ============================================================================

    async def status(self, refresh: bool = True) -> str:
        """
        Check job status.

        Args:
            refresh: If False, returns cached status if available

        Returns:
            Status string: "ready", "in_progress", "error", etc.

        Example:
            >>> status = await job.status()
            >>> print(f"Job status: {status}")
        """
        if not refresh and self._cached_status:
            return self._cached_status

        self._cached_status = await self._api_client.get_status(self.snapshot_id)
        return self._cached_status


    async def wait(
        self,
        timeout: int = 300,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        verbose: bool = False,
    ) -> str:
        """
        Wait for job to complete.

        Args:
            timeout: Maximum seconds to wait
            poll_interval: Seconds between status checks
            verbose: Print status updates

        Returns:
            Final status ("ready" or "error")

        Raises:
            TimeoutError: If timeout is reached
            APIError: If job fails

        Example:
            >>> await job.wait(timeout=120, verbose=True)
            >>> print("Job completed!")
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                raise TimeoutError(f"Job {self.snapshot_id} timed out after {timeout}s")

            status = await self.status(refresh=True)

            if verbose:
                print(f"   [{elapsed:.1f}s] Job status: {status}")

            if status == "ready":
                return status
            elif status == "error" or status == "failed":
                raise APIError(f"Job {self.snapshot_id} failed with status: {status}")

            # Still in progress (can be "running", "in_progress", "pending", etc.)
            await asyncio.sleep(poll_interval)


    async def fetch(self, format: str = "json") -> Any:
        """
        Fetch job results.

        Note: Does not check if job is ready. Use wait() first
        or check status() to ensure job is complete.

        Args:
            format: Result format ("json" or "raw")

        Returns:
            Job results

        Example:
            >>> await job.wait()
            >>> data = await job.fetch()
        """
        self._cached_data = await self._api_client.fetch_result(self.snapshot_id, format=format)
        return self._cached_data


    async def to_result(
        self,
        timeout: int = 300,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
    ) -> ScrapeResult:
        """
        Wait for completion and return as ScrapeResult.

        Convenience method that combines wait + fetch + result creation.

        Args:
            timeout: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            ScrapeResult object

        Example:
            >>> result = await job.to_result()
            >>> if result.success:
            ...     print(result.data)
        """
        start_time = datetime.now(timezone.utc)

        try:
            # Wait for completion
            await self.wait(timeout=timeout, poll_interval=poll_interval)

            # Fetch results
            data = await self.fetch()

            # Calculate timing
            end_time = datetime.now(timezone.utc)

            # Estimate cost (rough)
            record_count = len(data) if isinstance(data, list) else 1
            estimated_cost = record_count * self.cost_per_record

            return ScrapeResult(
                success=True,
                data=data,
                platform=self.platform_name,
                cost=estimated_cost,
                timing_start=start_time,
                timing_end=end_time,
                metadata={"snapshot_id": self.snapshot_id},
            )

        except Exception as e:
            return ScrapeResult(
                success=False,
                error=str(e),
                platform=self.platform_name,
                timing_start=start_time,
                timing_end=datetime.now(timezone.utc),
                metadata={"snapshot_id": self.snapshot_id},
            )

