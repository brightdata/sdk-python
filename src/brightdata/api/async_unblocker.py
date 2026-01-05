"""Async unblocker client for non-blocking requests.

This client handles Bright Data's async unblocker endpoints which support
both SERP and Web Unlocker services in non-blocking mode.

Endpoints:
- POST /unblocker/req → Triggers async request, returns x-response-id header
- GET /unblocker/get_result → Polls for results (202 pending, 200 ready)

Key Design Decisions:
- customer_id is OPTIONAL for both SERP and Web Unlocker (derived from bearer token)
- Uses AsyncEngine for all HTTP operations (reuses auth, rate limiting)
- Simple status model: "ready", "pending", or "error"
- Minimal abstraction - just wraps the two endpoints

Performance Note:
- SERP async: ~3 seconds response time
- Web Unlocker async: ~145 seconds response time (sync mode is faster!)
- See devdocs/web_unlocker_async_inspection.md for details
"""

from typing import Optional, Any
from ..core.engine import AsyncEngine
from ..exceptions import APIError


class AsyncUnblockerClient:
    """
    Client for async unblocker endpoints.

    Supports both SERP and Web Unlocker async modes using:
    - POST /unblocker/req → returns x-response-id header
    - GET /unblocker/get_result → polls for results

    Example:
        >>> async with AsyncEngine(token) as engine:
        ...     client = AsyncUnblockerClient(engine)
        ...
        ...     # Trigger async request
        ...     response_id = await client.trigger(
        ...         zone="my_zone",
        ...         url="https://example.com"
        ...     )
        ...
        ...     # Poll until ready
        ...     while True:
        ...         status = await client.get_status(zone="my_zone", response_id=response_id)
        ...         if status == "ready":
        ...             data = await client.fetch_result(zone="my_zone", response_id=response_id)
        ...             break
        ...         elif status == "error":
        ...             break
        ...         await asyncio.sleep(2)
    """

    TRIGGER_ENDPOINT = "/unblocker/req"
    FETCH_ENDPOINT = "/unblocker/get_result"

    def __init__(self, engine: AsyncEngine):
        """
        Initialize async unblocker client.

        Args:
            engine: AsyncEngine instance with bearer token auth
        """
        self.engine = engine

    async def trigger(
        self,
        zone: str,
        url: str,
        customer: Optional[str] = None,
        **kwargs  # Additional params like country, format, etc.
    ) -> Optional[str]:
        """
        Trigger async unblocker request.

        Args:
            zone: Zone name (e.g., "serp_api4", "unblocker_zone")
            url: Target URL to scrape/search
            customer: Customer ID (optional, derived from bearer token if not provided)
            **kwargs: Additional request parameters (e.g., country, format, method)

        Returns:
            response_id from x-response-id header, or None if trigger failed

        Note:
            customer_id is optional for both SERP and Web Unlocker.

        Example:
            >>> response_id = await client.trigger(
            ...     zone="my_serp_zone",
            ...     url="https://www.google.com/search?q=test&brd_json=1"
            ... )
        """
        params = {"zone": zone}

        # Add customer to query params if provided
        if customer:
            params["customer"] = customer

        payload = {"url": url}

        # Merge additional params into payload
        payload.update(kwargs)

        async with self.engine.post_to_url(
            f"{self.engine.BASE_URL}{self.TRIGGER_ENDPOINT}",
            params=params,
            json_data=payload
        ) as response:
            # Extract response_id from x-response-id header
            # Note: This is different from datasets API which returns snapshot_id in body
            response_id = response.headers.get("x-response-id")
            return response_id

    async def get_status(
        self,
        zone: str,
        response_id: str,
        customer: Optional[str] = None
    ) -> str:
        """
        Check if response is ready.

        Args:
            zone: Zone name
            response_id: Response ID from trigger()
            customer: Customer ID (optional, derived from bearer token if not provided)

        Returns:
            - "ready" if HTTP 200 (results available)
            - "pending" if HTTP 202 (still processing)
            - "error" for any other status

        Example:
            >>> status = await client.get_status(
            ...     zone="my_zone",
            ...     response_id="s4w7t1767082074477rtu2rth43mk8",
            ...     customer="hl_67e5ed38"
            ... )
            >>> if status == "ready":
            ...     # Fetch results
        """
        params = {
            "zone": zone,
            "response_id": response_id
        }

        # Add customer to query params if provided
        if customer:
            params["customer"] = customer

        async with self.engine.get_from_url(
            f"{self.engine.BASE_URL}{self.FETCH_ENDPOINT}",
            params=params
        ) as response:
            if response.status == 200:
                return "ready"
            elif response.status == 202:
                return "pending"
            else:
                # Any other status (4xx, 5xx) is treated as error
                return "error"

    async def fetch_result(
        self,
        zone: str,
        response_id: str,
        response_format: str = "json",
        customer: Optional[str] = None
    ) -> Any:
        """
        Fetch results when ready.

        Important: Only call this when get_status() returns "ready".
        If called while still pending, will raise APIError.

        Args:
            zone: Zone name
            response_id: Response ID from trigger()
            response_format: How to parse response - "json" or "raw" (default: "json")
            customer: Customer ID (optional, derived from bearer token if not provided)

        Returns:
            Response data (parsed JSON dict/list or raw text string)

        Raises:
            APIError: If response not ready (HTTP 202) or fetch fails

        Example:
            >>> # SERP results (JSON)
            >>> data = await client.fetch_result(
            ...     zone="my_serp_zone",
            ...     response_id="s4w7t1767082074477rtu2rth43mk8",
            ...     response_format="json"
            ... )
            >>> # Web Unlocker HTML (raw text)
            >>> html = await client.fetch_result(
            ...     zone="my_web_zone",
            ...     response_id="s4w7t1767082074477rtu2rth43mk8",
            ...     response_format="raw",
            ...     customer="hl_67e5ed38"
            ... )
        """
        params = {
            "zone": zone,
            "response_id": response_id
        }

        # Add customer to query params if provided
        if customer:
            params["customer"] = customer

        async with self.engine.get_from_url(
            f"{self.engine.BASE_URL}{self.FETCH_ENDPOINT}",
            params=params
        ) as response:
            if response.status == 200:
                # Success - parse based on format
                if response_format == "json":
                    return await response.json()
                else:
                    return await response.text()
            elif response.status == 202:
                # Still pending - caller should have checked status first
                raise APIError("Response not ready yet (HTTP 202). Check status before fetching.")
            else:
                # Error occurred
                error_text = await response.text()
                raise APIError(f"Fetch failed (HTTP {response.status}): {error_text}")
