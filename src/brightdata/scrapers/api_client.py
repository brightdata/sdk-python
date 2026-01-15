"""
Dataset API Client - HTTP operations for Bright Data Datasets API.

Handles all HTTP communication with Bright Data's Datasets API v3:
- Triggering dataset collection
- Checking snapshot status
- Fetching snapshot results
"""

from typing import List, Dict, Any, Optional

from ..core.engine import AsyncEngine
from ..constants import HTTP_OK
from ..exceptions import APIError


class DatasetAPIClient:
    """
    Client for Bright Data Datasets API v3 operations.

    Handles all HTTP communication for dataset operations:
    - Trigger collection and get snapshot_id
    - Check snapshot status
    - Fetch snapshot results

    This class encapsulates all API endpoint details and error handling.
    """

    TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"
    STATUS_URL = "https://api.brightdata.com/datasets/v3/progress"
    RESULT_URL = "https://api.brightdata.com/datasets/v3/snapshot"

    def __init__(self, engine: AsyncEngine):
        """
        Initialize dataset API client.

        Args:
            engine: AsyncEngine instance for HTTP operations
        """
        self.engine = engine

    async def trigger(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        include_errors: bool = True,
        sdk_function: Optional[str] = None,
        extra_params: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """
        Trigger dataset collection and get snapshot_id.

        Args:
            payload: Request payload for dataset collection
            dataset_id: Bright Data dataset identifier
            include_errors: Include error records in results
            sdk_function: SDK function name for monitoring
            extra_params: Additional query parameters (e.g., for discovery endpoints:
                          {"type": "discover_new", "discover_by": "user_name"})

        Returns:
            snapshot_id if successful, None otherwise

        Raises:
            APIError: If trigger request fails
        """
        params = {
            "dataset_id": dataset_id,
            "include_errors": str(include_errors).lower(),
        }

        if sdk_function:
            params["sdk_function"] = sdk_function

        if extra_params:
            params.update(extra_params)

        async with self.engine.post_to_url(
            self.TRIGGER_URL, json_data=payload, params=params
        ) as response:
            if response.status == HTTP_OK:
                data = await response.json()
                return data.get("snapshot_id")
            else:
                error_text = await response.text()
                raise APIError(
                    f"Trigger failed (HTTP {response.status}): {error_text}",
                    status_code=response.status,
                )

    async def get_status(self, snapshot_id: str) -> str:
        """
        Get snapshot status.

        Args:
            snapshot_id: Snapshot identifier

        Returns:
            Status string ("ready", "in_progress", "error", etc.)
        """
        url = f"{self.STATUS_URL}/{snapshot_id}"

        async with self.engine.get_from_url(url) as response:
            if response.status == HTTP_OK:
                data = await response.json()
                return data.get("status", "unknown")
            else:
                return "error"

    async def fetch_result(self, snapshot_id: str, format: str = "json") -> Any:
        """
        Fetch snapshot results.

        Args:
            snapshot_id: Snapshot identifier
            format: Result format ("json" or "raw")

        Returns:
            Result data (parsed JSON or raw text)

        Raises:
            APIError: If fetch request fails
        """
        url = f"{self.RESULT_URL}/{snapshot_id}"
        params = {"format": format}

        async with self.engine.get_from_url(url, params=params) as response:
            if response.status == HTTP_OK:
                if format == "json":
                    return await response.json()
                else:
                    return await response.text()
            else:
                error_text = await response.text()
                raise APIError(
                    f"Failed to fetch results (HTTP {response.status}): {error_text}",
                    status_code=response.status,
                )
