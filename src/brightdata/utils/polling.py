"""
Polling utilities for async dataset operations.

Provides shared polling logic for:
- Waiting for dataset snapshots to complete
- Checking status periodically
- Fetching results when ready
- Timeout handling
"""

from __future__ import annotations

import asyncio
from typing import Any, List, Callable, Awaitable
from datetime import datetime, timezone

from ..models import ScrapeResult
from ..constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT


async def poll_until_ready(
    get_status_func: Callable[[str], Awaitable[str]],
    fetch_result_func: Callable[[str], Awaitable[Any]],
    snapshot_id: str,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    poll_timeout: int = DEFAULT_POLL_TIMEOUT,
    trigger_sent_at: datetime | None = None,
    snapshot_id_received_at: datetime | None = None,
    platform: str | None = None,
    method: str | None = None,
    cost_per_record: float = 0.001,
) -> ScrapeResult:
    """
    Poll snapshot until ready, then fetch results.

    Generic polling utility that works with any dataset API by accepting
    status and fetch functions as callbacks.

    Args:
        get_status_func: Async function to get snapshot status (snapshot_id) -> status_str
        fetch_result_func: Async function to fetch results (snapshot_id) -> data
        snapshot_id: Snapshot identifier to poll
        poll_interval: Seconds between status checks (default: 10)
        poll_timeout: Maximum seconds to wait (default: 600)
        trigger_sent_at: Timestamp when trigger request was sent (optional)
        snapshot_id_received_at: When snapshot_id was received (optional)
        platform: Platform name for result metadata (optional)
        method: Method used: "web_scraper", "web_unlocker", "browser_api" (optional)
        cost_per_record: Cost per record for cost calculation (default: 0.001)

    Returns:
        ScrapeResult with data, timing, and metadata

    Example:
        >>> async def get_status(sid):
        ...     response = await session.get(f"/progress/{sid}")
        ...     data = await response.json()
        ...     return data["status"]
        >>>
        >>> async def fetch(sid):
        ...     response = await session.get(f"/snapshot/{sid}")
        ...     return await response.json()
        >>>
        >>> result = await poll_until_ready(
        ...     get_status_func=get_status,
        ...     fetch_result_func=fetch,
        ...     snapshot_id="abc123",
        ...     poll_interval=10,
        ...     poll_timeout=300
        ... )
    """
    start_time = datetime.now(timezone.utc)
    snapshot_polled_at: List[datetime] = []

    # Use provided timestamps or create new ones
    trigger_sent = trigger_sent_at or start_time
    snapshot_received = snapshot_id_received_at or start_time

    while True:
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

        # Check timeout
        if elapsed > poll_timeout:
            return ScrapeResult(
                success=False,
                url="",
                status="timeout",
                error=f"Polling timeout after {poll_timeout}s",
                snapshot_id=snapshot_id,
                platform=platform,
                method=method or "web_scraper",
                trigger_sent_at=trigger_sent,
                snapshot_id_received_at=snapshot_received,
                snapshot_polled_at=snapshot_polled_at,
                data_fetched_at=datetime.now(timezone.utc),
            )

        # Poll status
        poll_time = datetime.now(timezone.utc)
        snapshot_polled_at.append(poll_time)

        try:
            status = await get_status_func(snapshot_id)
        except Exception as e:
            return ScrapeResult(
                success=False,
                url="",
                status="error",
                error=f"Failed to get status: {str(e)}",
                snapshot_id=snapshot_id,
                platform=platform,
                method=method or "web_scraper",
                trigger_sent_at=trigger_sent,
                snapshot_id_received_at=snapshot_received,
                snapshot_polled_at=snapshot_polled_at,
                data_fetched_at=datetime.now(timezone.utc),
            )

        # Check if ready
        if status == "ready":
            # Fetch results
            data_fetched_at = datetime.now(timezone.utc)

            try:
                data = await fetch_result_func(snapshot_id)
            except Exception as e:
                return ScrapeResult(
                    success=False,
                    url="",
                    status="error",
                    error=f"Failed to fetch results: {str(e)}",
                    snapshot_id=snapshot_id,
                    platform=platform,
                    method=method or "web_scraper",
                    trigger_sent_at=trigger_sent,
                    snapshot_id_received_at=snapshot_received,
                    snapshot_polled_at=snapshot_polled_at,
                    data_fetched_at=data_fetched_at,
                )

            # Calculate metrics
            row_count = len(data) if isinstance(data, list) else None
            cost = (row_count * cost_per_record) if row_count else None

            return ScrapeResult(
                success=True,
                url="",
                status="ready",
                data=data,
                snapshot_id=snapshot_id,
                cost=cost,
                platform=platform,
                method=method or "web_scraper",
                trigger_sent_at=trigger_sent,
                snapshot_id_received_at=snapshot_received,
                snapshot_polled_at=snapshot_polled_at,
                data_fetched_at=data_fetched_at,
                row_count=row_count,
            )

        elif status in ("error", "failed"):
            return ScrapeResult(
                success=False,
                url="",
                status="error",
                error=f"Job failed with status: {status}",
                snapshot_id=snapshot_id,
                platform=platform,
                method=method or "web_scraper",
                trigger_sent_at=trigger_sent,
                snapshot_id_received_at=snapshot_received,
                snapshot_polled_at=snapshot_polled_at,
                data_fetched_at=datetime.now(timezone.utc),
            )

        # Still in progress - wait and poll again
        await asyncio.sleep(poll_interval)
