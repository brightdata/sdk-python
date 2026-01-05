"""Web Unlocker API - High-level service wrapper for Bright Data's Web Unlocker proxy service.

All methods are async-only. For sync usage, use SyncBrightDataClient.
"""

from typing import Union, List, Optional, Dict, Any
from datetime import datetime, timezone
import asyncio

from .base import BaseAPI
from .async_unblocker import AsyncUnblockerClient
from ..models import ScrapeResult
from ..utils.validation import (
    validate_url,
    validate_url_list,
    validate_zone_name,
    validate_country_code,
    validate_timeout,
    validate_response_format,
    validate_http_method,
)
from ..utils.url import extract_root_domain
from ..utils.function_detection import get_caller_function_name
from ..constants import HTTP_OK
from ..exceptions import ValidationError, APIError


class WebUnlockerService(BaseAPI):
    """
    High-level service wrapper around Bright Data's Web Unlocker proxy service.

    Provides simple HTTP-based scraping with anti-bot capabilities. This is the
    fastest, most cost-effective option for basic HTML extraction without JavaScript rendering.

    Example:
        >>> async with AsyncEngine(token) as engine:
        ...     service = WebUnlockerService(engine)
        ...     result = await service.scrape_async("https://example.com", zone="my_zone")
        ...     print(result.data)
    """

    ENDPOINT = "/request"

    def __init__(self, engine):
        """
        Initialize Web Unlocker service.

        Args:
            engine: AsyncEngine instance for HTTP operations
        """
        super().__init__(engine)
        # Initialize async unblocker client for async mode support
        self.async_unblocker = AsyncUnblockerClient(engine)

    async def _execute_async(self, *args: Any, **kwargs: Any) -> Any:
        """Execute API operation asynchronously."""
        return await self.scrape_async(*args, **kwargs)

    async def scrape_async(
        self,
        url: Union[str, List[str]],
        zone: str,
        country: str = "",
        response_format: str = "raw",
        method: str = "GET",
        timeout: Optional[int] = None,
        mode: str = "sync",
        poll_interval: int = 2,
        poll_timeout: int = 180,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape URL(s) asynchronously using Web Unlocker API.

        Args:
            url: Single URL string or list of URLs to scrape.
            zone: Bright Data zone identifier.
            country: Two-letter ISO country code for proxy location (optional).
            response_format: Response format - "json" for structured data, "raw" for HTML string.
            method: HTTP method for the request (default: "GET").
            timeout: Request timeout in seconds (uses engine default if not provided).
            mode: "sync" (default, blocking) or "async" (non-blocking with polling).
            poll_interval: Seconds between polls (async mode only, default: 2).
            poll_timeout: Max wait time in seconds (async mode only, default: 180).

        Warning:
            Web Unlocker async mode takes ~145 seconds to complete. For faster results,
            use sync mode (default). See devdocs/web_unlocker_async_inspection.md.

        Returns:
            ScrapeResult for single URL, or List[ScrapeResult] for multiple URLs.

        Raises:
            ValidationError: If input validation fails.
            APIError: If API request fails.

        Note:
            - Sync mode (default): Uses /request endpoint, blocks until results ready
            - Async mode: Uses /unblocker/req + /unblocker/get_result, polls for results
            - Both modes return the same ScrapeResult structure
        """
        validate_zone_name(zone)
        validate_response_format(response_format)
        validate_http_method(method)
        validate_country_code(country)

        if timeout is not None:
            validate_timeout(timeout)

        # Route based on mode
        if mode == "async":
            # Async mode: use unblocker endpoints with polling
            if isinstance(url, list):
                validate_url_list(url)
                return await self._scrape_multiple_async_unblocker(
                    urls=url,
                    zone=zone,
                    country=country,
                    response_format=response_format,
                    method=method,
                    poll_interval=poll_interval,
                    poll_timeout=poll_timeout,
                )
            else:
                validate_url(url)
                return await self._scrape_single_async_unblocker(
                    url=url,
                    zone=zone,
                    country=country,
                    response_format=response_format,
                    method=method,
                    poll_interval=poll_interval,
                    poll_timeout=poll_timeout,
                )
        else:
            # Sync mode (default): use /request endpoint (existing behavior)
            if isinstance(url, list):
                validate_url_list(url)
                return await self._scrape_multiple_async(
                    urls=url,
                    zone=zone,
                    country=country,
                    response_format=response_format,
                    method=method,
                    timeout=timeout,
                )
            else:
                validate_url(url)
                return await self._scrape_single_async(
                    url=url,
                    zone=zone,
                    country=country,
                    response_format=response_format,
                    method=method,
                    timeout=timeout,
                )

    async def _scrape_single_async(
        self,
        url: str,
        zone: str,
        country: str,
        response_format: str,
        method: str,
        timeout: Optional[int],
    ) -> ScrapeResult:
        """Scrape a single URL."""
        trigger_sent_at = datetime.now(timezone.utc)

        payload: Dict[str, Any] = {
            "zone": zone,
            "url": url,
            "format": response_format,
            "method": method,
        }

        if country:
            payload["country"] = country.upper()

        sdk_function = get_caller_function_name()
        if sdk_function:
            payload["sdk_function"] = sdk_function

        try:
            # Make the request and read response body immediately
            async with self.engine.post_to_url(
                f"{self.engine.BASE_URL}{self.ENDPOINT}", json_data=payload
            ) as response:
                data_fetched_at = datetime.now(timezone.utc)

                if response.status == HTTP_OK:
                    if response_format == "json":
                        try:
                            data = await response.json()
                        except (ValueError, TypeError) as e:
                            raise APIError(f"Failed to parse JSON response: {str(e)}")
                    else:
                        data = await response.text()

                    root_domain = extract_root_domain(url)
                    html_char_size = len(data) if isinstance(data, str) else None

                    return ScrapeResult(
                        success=True,
                        url=url,
                        status="ready",
                        data=data,
                        cost=None,
                        method="web_unlocker",
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                        root_domain=root_domain,
                        html_char_size=html_char_size,
                    )
                else:
                    error_text = await response.text()
                    return ScrapeResult(
                        success=False,
                        url=url,
                        status="error",
                        error=f"API returned status {response.status}: {error_text}",
                        method="web_unlocker",
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                    )

        except Exception as e:
            data_fetched_at = datetime.now(timezone.utc)

            if isinstance(e, (ValidationError, APIError)):
                raise

            return ScrapeResult(
                success=False,
                url=url,
                status="error",
                error=f"Unexpected error: {str(e)}",
                method="web_unlocker",
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=data_fetched_at,
            )

    async def _scrape_multiple_async(
        self,
        urls: List[str],
        zone: str,
        country: str,
        response_format: str,
        method: str,
        timeout: Optional[int],
    ) -> List[ScrapeResult]:
        """Scrape multiple URLs concurrently."""
        tasks = [
            self._scrape_single_async(
                url=url,
                zone=zone,
                country=country,
                response_format=response_format,
                method=method,
                timeout=timeout,
            )
            for url in urls
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results: List[ScrapeResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ScrapeResult(
                        success=False,
                        url=urls[i],
                        status="error",
                        error=f"Exception: {str(result)}",
                        trigger_sent_at=datetime.now(timezone.utc),
                        data_fetched_at=datetime.now(timezone.utc),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def _scrape_single_async_unblocker(
        self,
        url: str,
        zone: str,
        country: str,
        response_format: str,
        method: str,
        poll_interval: int,
        poll_timeout: int,
    ) -> ScrapeResult:
        """
        Scrape single URL using async unblocker endpoints.

        This method:
        1. Triggers async request via /unblocker/req
        2. Polls /unblocker/get_result until ready or timeout
        3. Fetches and returns scraped content
        """
        trigger_sent_at = datetime.now(timezone.utc)

        # Trigger async request
        try:
            response_id = await self.async_unblocker.trigger(
                zone=zone,
                url=url,
                format=response_format,
                method=method,
                country=country.upper() if country else None
            )
        except Exception as e:
            return ScrapeResult(
                success=False,
                url=url,
                status="error",
                error=f"Failed to trigger async request: {str(e)}",
                method="web_unlocker",
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=datetime.now(timezone.utc),
            )

        if not response_id:
            return ScrapeResult(
                success=False,
                url=url,
                status="error",
                error="Failed to trigger async request (no response_id received)",
                method="web_unlocker",
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=datetime.now(timezone.utc),
            )

        # Poll until ready or timeout
        start_time = datetime.now(timezone.utc)

        while True:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Check timeout
            if elapsed > poll_timeout:
                return ScrapeResult(
                    success=False,
                    url=url,
                    status="timeout",
                    error=f"Polling timeout after {poll_timeout}s (response_id: {response_id})",
                    method="web_unlocker",
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=datetime.now(timezone.utc),
                )

            # Check status
            try:
                status = await self.async_unblocker.get_status(zone, response_id)
            except Exception as e:
                return ScrapeResult(
                    success=False,
                    url=url,
                    status="error",
                    error=f"Failed to check status: {str(e)}",
                    method="web_unlocker",
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=datetime.now(timezone.utc),
                )

            if status == "ready":
                # Results ready - fetch them
                data_fetched_at = datetime.now(timezone.utc)

                try:
                    data = await self.async_unblocker.fetch_result(
                        zone,
                        response_id,
                        response_format=response_format
                    )

                    root_domain = extract_root_domain(url)
                    html_char_size = len(data) if isinstance(data, str) else None

                    return ScrapeResult(
                        success=True,
                        url=url,
                        status="ready",
                        data=data,
                        cost=None,
                        method="web_unlocker",
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                        root_domain=root_domain,
                        html_char_size=html_char_size,
                    )
                except Exception as e:
                    return ScrapeResult(
                        success=False,
                        url=url,
                        status="error",
                        error=f"Failed to fetch results: {str(e)}",
                        method="web_unlocker",
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                    )

            elif status == "error":
                return ScrapeResult(
                    success=False,
                    url=url,
                    status="error",
                    error=f"Async request failed (response_id: {response_id})",
                    method="web_unlocker",
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=datetime.now(timezone.utc),
                )

            # Still pending - wait and retry
            await asyncio.sleep(poll_interval)

    async def _scrape_multiple_async_unblocker(
        self,
        urls: List[str],
        zone: str,
        country: str,
        response_format: str,
        method: str,
        poll_interval: int,
        poll_timeout: int,
    ) -> List[ScrapeResult]:
        """Execute multiple scrapes using async unblocker."""
        tasks = [
            self._scrape_single_async_unblocker(
                url=url,
                zone=zone,
                country=country,
                response_format=response_format,
                method=method,
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
            )
            for url in urls
        ]

        # Execute all scrapes concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, converting exceptions to ScrapeResult errors
        processed_results: List[ScrapeResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ScrapeResult(
                        success=False,
                        url=urls[i],
                        status="error",
                        error=f"Exception: {str(result)}",
                        method="web_unlocker",
                        trigger_sent_at=datetime.now(timezone.utc),
                        data_fetched_at=datetime.now(timezone.utc),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    scrape = scrape_async
