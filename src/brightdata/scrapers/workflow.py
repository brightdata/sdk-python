"""
Workflow Executor - Trigger/Poll/Fetch workflow implementation.

Handles the complete async workflow for dataset operations:
1. Trigger collection and get snapshot_id
2. Poll until status is "ready"
3. Fetch results when ready
"""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timezone

from ..models import ScrapeResult
from ..exceptions import APIError
from ..constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT, DEFAULT_COST_PER_RECORD
from ..utils.polling import poll_until_ready
from .api_client import DatasetAPIClient


class WorkflowExecutor:
    """
    Executes the standard trigger/poll/fetch workflow for dataset operations.

    This class encapsulates the complete workflow logic, making it reusable
    across different scraper implementations.
    """

    def __init__(
        self,
        api_client: DatasetAPIClient,
        platform_name: Optional[str] = None,
        cost_per_record: float = DEFAULT_COST_PER_RECORD,
    ):
        """
        Initialize workflow executor.

        Args:
            api_client: DatasetAPIClient for API operations
            platform_name: Platform name for result metadata
            cost_per_record: Cost per record for cost calculation
        """
        self.api_client = api_client
        self.platform_name = platform_name
        self.cost_per_record = cost_per_record

    async def execute(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: int = DEFAULT_POLL_TIMEOUT,
        include_errors: bool = True,
        normalize_func: Optional[Callable[[Any], Any]] = None,
        sdk_function: Optional[str] = None,
    ) -> ScrapeResult:
        """
        Execute complete trigger/poll/fetch workflow.

        Args:
            payload: Request payload for dataset API
            dataset_id: Dataset identifier
            poll_interval: Seconds between status checks
            poll_timeout: Maximum seconds to wait
            include_errors: Include error records
            normalize_func: Optional function to normalize result data
            sdk_function: SDK function name for monitoring

        Returns:
            ScrapeResult with data or error
        """
        trigger_sent_at = datetime.now(timezone.utc)

        try:
            snapshot_id = await self.api_client.trigger(
                payload=payload,
                dataset_id=dataset_id,
                include_errors=include_errors,
                sdk_function=sdk_function,
            )
        except APIError as e:
            return ScrapeResult(
                success=False,
                url="",
                status="error",
                error=f"Trigger failed: {str(e)}",
                platform=self.platform_name,
                method="web_scraper",
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=datetime.now(timezone.utc),
            )

        if not snapshot_id:
            return ScrapeResult(
                success=False,
                url="",
                status="error",
                error="Failed to trigger scrape - no snapshot_id returned",
                platform=self.platform_name,
                method="web_scraper",
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=datetime.now(timezone.utc),
            )

        snapshot_id_received_at = datetime.now(timezone.utc)

        result = await self._poll_and_fetch(
            snapshot_id=snapshot_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            trigger_sent_at=trigger_sent_at,
            snapshot_id_received_at=snapshot_id_received_at,
            normalize_func=normalize_func,
        )

        return result

    async def _poll_and_fetch(
        self,
        snapshot_id: str,
        poll_interval: int,
        poll_timeout: int,
        trigger_sent_at: datetime,
        snapshot_id_received_at: datetime,
        normalize_func: Optional[Callable[[Any], Any]] = None,
    ) -> ScrapeResult:
        """
        Poll snapshot until ready, then fetch results.

        Uses shared polling utility for consistent behavior.

        Args:
            snapshot_id: Snapshot identifier
            poll_interval: Seconds between polls
            poll_timeout: Maximum wait time
            trigger_sent_at: Timestamp when trigger request was sent
            snapshot_id_received_at: When snapshot_id was received
            normalize_func: Optional function to normalize result data

        Returns:
            ScrapeResult with data or error/timeout status
        """
        result = await poll_until_ready(
            get_status_func=self.api_client.get_status,
            fetch_result_func=self.api_client.fetch_result,
            snapshot_id=snapshot_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            trigger_sent_at=trigger_sent_at,
            snapshot_id_received_at=snapshot_id_received_at,
            platform=self.platform_name,
            method="web_scraper",
            cost_per_record=self.cost_per_record,
        )

        if result.success and result.data and normalize_func:
            result.data = normalize_func(result.data)

        return result
