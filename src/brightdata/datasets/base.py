"""
Base dataset class - provides common functionality for all datasets.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Literal, TYPE_CHECKING

from .models import DatasetMetadata, SnapshotStatus

if TYPE_CHECKING:
    from ..core.async_engine import AsyncEngine


class DatasetError(Exception):
    """Error related to dataset operations."""

    pass


class BaseDataset:
    """
    Base class for all dataset types.

    Provides common methods: get_metadata(), get_status(), download().
    Call the dataset directly to filter: await dataset(filter=..., records_limit=...)
    Subclasses set their own DATASET_ID and can add dataset-specific helpers.
    """

    BASE_URL = "https://api.brightdata.com"
    DATASET_ID: str = ""  # Override in subclasses
    NAME: str = ""  # Override in subclasses

    def __init__(self, engine: "AsyncEngine"):
        self._engine = engine
        self._metadata: Optional[DatasetMetadata] = None

    @property
    def dataset_id(self) -> str:
        return self.DATASET_ID

    @property
    def name(self) -> str:
        return self.NAME

    async def get_metadata(self) -> DatasetMetadata:
        """
        Get dataset field schema.

        Returns field names, types, and descriptions for this dataset.
        Use this to discover what fields you can filter by.

        Returns:
            DatasetMetadata with fields dict
        """
        if self._metadata is None:
            async with self._engine.get_from_url(
                f"{self.BASE_URL}/datasets/{self.DATASET_ID}/metadata"
            ) as response:
                data = await response.json()
            self._metadata = DatasetMetadata.from_dict(data)
        return self._metadata

    async def __call__(
        self,
        filter: Dict[str, Any],
        records_limit: Optional[int] = None,
    ) -> str:
        """
        Filter dataset records and create a snapshot.

        Returns snapshot_id immediately - does NOT wait for results.
        Use download() to poll and get the data.

        Args:
            filter: Filter criteria. Example:
                {"name": "industry", "operator": "=", "value": "Technology"}
                Or with AND/OR:
                {
                    "operator": "and",
                    "filters": [
                        {"name": "industry", "operator": "=", "value": "Technology"},
                        {"name": "followers", "operator": ">", "value": 10000}
                    ]
                }
            records_limit: Maximum number of records to return

        Returns:
            snapshot_id (str) - use with download() to get data
        """
        payload: Dict[str, Any] = {
            "dataset_id": self.DATASET_ID,
            "filter": filter,
        }
        if records_limit is not None:
            payload["records_limit"] = records_limit

        async with self._engine.post_to_url(
            f"{self.BASE_URL}/datasets/filter",
            json_data=payload,
        ) as response:
            data = await response.json()

        if "snapshot_id" not in data:
            error_msg = data.get("error") or data.get("message") or str(data)
            raise DatasetError(f"Failed to create snapshot: {error_msg}")

        return data["snapshot_id"]

    async def sample(self, records_limit: int = 10) -> str:
        """
        Get a sample of records without specifying a filter.

        Automatically discovers the first available field and uses
        'is_not_null' operator to fetch any available records.

        Args:
            records_limit: Maximum number of records to return (default: 10)

        Returns:
            snapshot_id (str) - use with download() to get data
        """
        metadata = await self.get_metadata()
        if not metadata.fields:
            raise DatasetError(f"Dataset {self.DATASET_ID} has no fields")

        first_field = list(metadata.fields.keys())[0]
        return await self(
            filter={"name": first_field, "operator": "is_not_null"},
            records_limit=records_limit,
        )

    async def get_status(self, snapshot_id: str) -> SnapshotStatus:
        """
        Check snapshot status.

        Args:
            snapshot_id: Snapshot ID from calling the dataset

        Returns:
            SnapshotStatus with status field: "scheduled", "building", "ready", or "failed"
        """
        async with self._engine.get_from_url(
            f"{self.BASE_URL}/datasets/snapshots/{snapshot_id}"
        ) as response:
            data = await response.json()
        return SnapshotStatus.from_dict(data)

    async def download(
        self,
        snapshot_id: str,
        format: Literal["json", "jsonl", "csv"] = "jsonl",
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Download snapshot data.

        Polls until snapshot is ready, then downloads and returns data.

        Args:
            snapshot_id: Snapshot ID from calling the dataset
            format: Response format (json, jsonl, csv)
            timeout: Max seconds to wait for snapshot to be ready
            poll_interval: Seconds between status checks

        Returns:
            List of records (dicts)

        Raises:
            DatasetError: If snapshot fails
            TimeoutError: If snapshot not ready within timeout
        """
        start_time = time.time()

        # Poll until ready
        while True:
            status = await self.get_status(snapshot_id)

            if status.status == "ready":
                break
            elif status.status == "failed":
                raise DatasetError(f"Snapshot failed: {status.error}")
            elif time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Snapshot {snapshot_id} not ready after {timeout}s "
                    f"(status: {status.status})"
                )

            await asyncio.sleep(poll_interval)

        # Download data
        async with self._engine.get_from_url(
            f"{self.BASE_URL}/datasets/snapshots/{snapshot_id}/download",
            params={"format": format},
        ) as response:
            import json

            # Check for HTTP errors
            if response.status >= 400:
                error_text = await response.text()
                raise DatasetError(f"Download failed (HTTP {response.status}): {error_text}")

            # Get raw text first
            text = await response.text()

            # Handle empty response
            if not text or not text.strip():
                return []

            # Try to parse based on content type and format
            content_type = response.headers.get("Content-Type", "")

            # Try JSON first (most common)
            if "application/json" in content_type or text.strip().startswith("["):
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    pass
                else:
                    # Successfully parsed as JSON
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "data" in data:
                        return data["data"]
                    else:
                        return [data] if data else []

            # Try JSONL (newline-delimited JSON)
            if "ndjson" in content_type or format == "jsonl" or "\n" in text.strip():
                try:
                    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
                    if lines:
                        data = [json.loads(line) for line in lines]
                        return data
                except json.JSONDecodeError:
                    pass

            # Last resort: try as single JSON object
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "data" in data:
                    return data["data"]
                else:
                    return [data] if data else []
            except json.JSONDecodeError:
                # Return raw text as fallback
                return [{"raw": text}]
