"""
Scraper Studio API Client - HTTP operations for Bright Data's Scraper Studio API.

Handles all HTTP communication with Bright Data's DCA (Data Collection Automation) endpoints:
- Triggering real-time scrapes (trigger_immediate)
- Fetching real-time results (get_result)
- Checking job status (log)

Follows the same pattern as DatasetAPIClient and AsyncUnblockerClient.
"""

from typing import Dict, List, Any

from ..core.engine import AsyncEngine
from ..constants import HTTP_OK, HTTP_ACCEPTED
from ..exceptions import APIError, DataNotReadyError


BASE_URL = "https://api.brightdata.com"


class ScraperStudioAPIClient:
    """
    Client for Bright Data Scraper Studio API operations.

    Handles HTTP communication for DCA endpoints:
    - POST /dca/trigger_immediate → trigger single-input scrape
    - GET /dca/get_result → fetch real-time result
    - GET /dca/log/{job_id} → job status

    Example:
        >>> async with AsyncEngine(token) as engine:
        ...     client = ScraperStudioAPIClient(engine)
        ...     response_id = await client.trigger_immediate(
        ...         collector="c_abc123",
        ...         input={"url": "https://example.com"},
        ...     )
        ...     data = await client.fetch_immediate_result(response_id)
    """

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def trigger_immediate(
        self,
        collector: str,
        input: Dict[str, Any],
    ) -> str:
        """
        Trigger a real-time async scrape.

        Args:
            collector: Scraper collector ID (e.g., "c_abc123").
            input: Single input object (e.g., {"url": "https://..."}).

        Returns:
            response_id string for polling with fetch_immediate_result().

        Raises:
            APIError: If trigger request fails.
        """
        url = f"{BASE_URL}/dca/trigger_immediate"
        params = {"collector": collector}

        async with self.engine.post_to_url(url, json_data=input, params=params) as response:
            if response.status in (HTTP_OK, HTTP_ACCEPTED):
                data = await response.json()
                response_id = data.get("response_id")
                if not response_id:
                    raise APIError(f"No response_id in trigger_immediate response: {data}")
                return response_id
            else:
                error_text = await response.text()
                raise APIError(
                    f"trigger_immediate failed (HTTP {response.status}): {error_text}",
                    status_code=response.status,
                )

    async def fetch_immediate_result(
        self,
        response_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Fetch results from a real-time async scrape.

        Args:
            response_id: Response ID from trigger_immediate().

        Returns:
            List of scraped records.

        Raises:
            DataNotReadyError: If data is not ready yet (HTTP 202).
            APIError: If fetch request fails.
        """
        url = f"{BASE_URL}/dca/get_result"
        params = {"response_id": response_id}

        async with self.engine.get_from_url(url, params=params) as response:
            if response.status == HTTP_OK:
                return await response.json()
            elif response.status == 202:
                raise DataNotReadyError(f"Data not ready for response_id={response_id}")
            else:
                error_text = await response.text()
                raise APIError(
                    f"fetch_immediate_result failed (HTTP {response.status}): {error_text}",
                    status_code=response.status,
                )

    async def get_status(
        self,
        job_id: str,
    ) -> Dict[str, Any]:
        """
        Get job status/log.

        Args:
            job_id: Job ID (e.g., "j_abc123").

        Returns:
            Raw API response dict (parsed into JobStatus by service layer).

        Raises:
            APIError: If status request fails.
        """
        url = f"{BASE_URL}/dca/log/{job_id}"

        async with self.engine.get_from_url(url) as response:
            if response.status == HTTP_OK:
                return await response.json()
            else:
                error_text = await response.text()
                raise APIError(
                    f"get_status failed (HTTP {response.status}): {error_text}",
                    status_code=response.status,
                )
