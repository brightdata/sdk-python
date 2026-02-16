"""Base SERP service with separated responsibilities."""

import asyncio
import aiohttp
import json
import re
import time
import warnings
from typing import Union, List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone

from .url_builder import BaseURLBuilder
from .data_normalizer import BaseDataNormalizer
from ...core.engine import AsyncEngine
from ...models import SearchResult
from ...constants import HTTP_OK
from ...exceptions import ValidationError
from ...utils.validation import validate_zone_name
from ...utils.retry import retry_with_backoff
from ...utils.function_detection import get_caller_function_name
from ..async_unblocker import AsyncUnblockerClient


class BaseSERPService:
    """
    Base class for SERP (Search Engine Results Page) services.

    Uses dependency injection for URL building and data normalization
    to follow single responsibility principle.
    """

    SEARCH_ENGINE: str = ""
    ENDPOINT = "/request"
    DEFAULT_TIMEOUT = 30
    PAGE_SIZE = 10
    MAX_PAGES = 20
    PAGINATION_TIMEOUT = 300

    def __init__(
        self,
        engine: AsyncEngine,
        url_builder: BaseURLBuilder,
        data_normalizer: BaseDataNormalizer,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """
        Initialize SERP service.

        Args:
            engine: AsyncEngine for HTTP operations
            url_builder: URL builder for this search engine
            data_normalizer: Data normalizer for this search engine
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.engine = engine
        self.url_builder = url_builder
        self.data_normalizer = data_normalizer
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries

        # Async unblocker client for async mode support
        self.async_unblocker = AsyncUnblockerClient(engine)

    async def search(
        self,
        query: Union[str, List[str]],
        zone: str,
        location: Optional[str] = None,
        language: str = "en",
        device: str = "desktop",
        num_results: int = 10,
        mode: str = "sync",
        poll_interval: int = 2,
        poll_timeout: int = 30,
        **kwargs,
    ) -> Union[SearchResult, List[SearchResult]]:
        """
        Perform search asynchronously.

        Args:
            query: Search query string or list of queries
            zone: Bright Data zone for SERP API
            location: Geographic location
            language: Language code
            device: Device type
            num_results: Number of results to return
            mode: "sync" (default, blocking) or "async" (non-blocking with polling)
            poll_interval: Seconds between polls (async mode only, default: 2)
            poll_timeout: Max wait time in seconds (async mode only, default: 30)
            **kwargs: Engine-specific parameters

        Returns:
            SearchResult for single query, List[SearchResult] for multiple

        Note:
            - Sync mode (default): Uses /request endpoint, blocks until results ready
            - Async mode: Uses /unblocker/req + /unblocker/get_result, polls for results
            - Both modes return the same normalized data structure
            - For synchronous usage, use SyncBrightDataClient instead:
            >>> with SyncBrightDataClient() as client:
            ...     result = client.search.google(query)
        """
        is_single = isinstance(query, str)
        query_list = [query] if is_single else query

        self._validate_zone(zone)
        self._validate_queries(query_list)

        # Warn if pagination requested with async mode (not supported)
        if mode == "async" and num_results > self.PAGE_SIZE and self.SEARCH_ENGINE == "google":
            warnings.warn(
                f"Pagination (num_results={num_results}) is not supported in async mode. "
                f"Only first page (~{self.PAGE_SIZE} results) will be returned. "
                f"Use mode='sync' for pagination support.",
                UserWarning,
                stacklevel=2,
            )

        # Route based on mode
        if mode == "async":
            # Async mode: use unblocker endpoints with polling
            if len(query_list) == 1:
                return await self._search_single_async_unblocker(
                    query=query_list[0],
                    zone=zone,
                    location=location,
                    language=language,
                    device=device,
                    num_results=num_results,
                    poll_interval=poll_interval,
                    poll_timeout=poll_timeout,
                    **kwargs,
                )
            else:
                return await self._search_multiple_async_unblocker(
                    queries=query_list,
                    zone=zone,
                    location=location,
                    language=language,
                    device=device,
                    num_results=num_results,
                    poll_interval=poll_interval,
                    poll_timeout=poll_timeout,
                    **kwargs,
                )
        else:
            # Sync mode (default): use /request endpoint (existing behavior)
            if len(query_list) == 1:
                result = await self._search_single_async(
                    query=query_list[0],
                    zone=zone,
                    location=location,
                    language=language,
                    device=device,
                    num_results=num_results,
                    **kwargs,
                )
                return result
            else:
                return await self._search_multiple_async(
                    queries=query_list,
                    zone=zone,
                    location=location,
                    language=language,
                    device=device,
                    num_results=num_results,
                    **kwargs,
                )

    async def _search_single_async(
        self,
        query: str,
        zone: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs,
    ) -> SearchResult:
        """Execute single search query with retry logic."""
        # Route to pagination for Google when requesting more than one page
        if num_results > self.PAGE_SIZE and self.SEARCH_ENGINE == "google":
            return await self._search_with_pagination(
                query=query,
                zone=zone,
                location=location,
                language=language,
                device=device,
                num_results=num_results,
                **kwargs,
            )

        # Single page request
        trigger_sent_at = datetime.now(timezone.utc)

        search_url = self.url_builder.build(
            query=query,
            location=location,
            language=language,
            device=device,
            num_results=num_results,
            **kwargs,
        )

        raw_data, data_fetched_at, error = await self._execute_serp_request(
            search_url=search_url,
            zone=zone,
            trigger_sent_at=trigger_sent_at,
        )

        if error:
            return SearchResult(
                success=False,
                query={"q": query},
                error=f"Search failed: {error}",
                search_engine=self.SEARCH_ENGINE,
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=data_fetched_at,
            )

        normalized_data = self.data_normalizer.normalize(raw_data)

        return SearchResult(
            success=True,
            query={"q": query, "location": location, "language": language},
            data=normalized_data.get("results", []),
            total_found=normalized_data.get("total_results"),
            search_engine=self.SEARCH_ENGINE,
            country=location,
            results_per_page=num_results,
            trigger_sent_at=trigger_sent_at,
            data_fetched_at=data_fetched_at,
        )

    async def _execute_serp_request(
        self,
        search_url: str,
        zone: str,
        trigger_sent_at: datetime,
    ) -> Tuple[Dict[str, Any], datetime, Optional[str]]:
        """
        Execute a single SERP request and parse response.

        Returns:
            Tuple of (raw_data, data_fetched_at, error)
            If error is not None, raw_data will be empty dict.
        """
        response_format = "json" if "brd_json=1" in search_url else "raw"

        payload = {
            "zone": zone,
            "url": search_url,
            "format": response_format,
            "method": "GET",
        }

        sdk_function = get_caller_function_name()
        if sdk_function:
            payload["sdk_function"] = sdk_function

        async def _make_request():
            async with self.engine.post_to_url(
                f"{self.engine.BASE_URL}{self.ENDPOINT}",
                json_data=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as response:
                data_fetched_at = datetime.now(timezone.utc)

                if response.status == HTTP_OK:
                    text = await response.text()
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        try:
                            data = await response.json()
                        except Exception:
                            data = {"raw_html": text}

                    # Handle wrapped response format (status_code/headers/body)
                    if isinstance(data, dict) and "body" in data and "status_code" in data:
                        body = data.get("body", "")
                        if isinstance(body, str) and body.strip().startswith("<"):
                            data = {"body": body, "status_code": data.get("status_code")}
                        else:
                            try:
                                data = json.loads(body) if isinstance(body, str) else body
                            except (json.JSONDecodeError, TypeError):
                                data = {"body": body, "status_code": data.get("status_code")}

                    return (data, data_fetched_at, None)
                else:
                    error_text = await response.text()
                    return ({}, data_fetched_at, f"HTTP {response.status}: {error_text}")

        try:
            return await retry_with_backoff(_make_request, max_retries=self.max_retries)
        except Exception as e:
            return ({}, datetime.now(timezone.utc), f"Request error: {str(e)}")

    async def _search_with_pagination(
        self,
        query: str,
        zone: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs,
    ) -> SearchResult:
        """
        Execute search with sequential pagination (Google only).

        Fetches pages one at a time until num_results reached or no more results.
        """
        trigger_sent_at = datetime.now(timezone.utc)
        pagination_start_time = time.time()

        all_results: List[Dict[str, Any]] = []
        pages_fetched = 0
        current_start = 0
        google_total_results = None
        last_error = None

        while len(all_results) < num_results and pages_fetched < self.MAX_PAGES:
            # Check total timeout
            elapsed = time.time() - pagination_start_time
            if elapsed > self.PAGINATION_TIMEOUT:
                last_error = f"Pagination timeout after {int(elapsed)}s ({pages_fetched} pages)"
                break

            # Build URL for current page
            search_url = self.url_builder.build(
                query=query,
                location=location,
                language=language,
                device=device,
                num_results=min(self.PAGE_SIZE, num_results - len(all_results)),
                start=current_start,
                **kwargs,
            )

            # Execute request
            raw_data, data_fetched_at, error = await self._execute_serp_request(
                search_url=search_url,
                zone=zone,
                trigger_sent_at=trigger_sent_at,
            )

            if error:
                if pages_fetched == 0:
                    return SearchResult(
                        success=False,
                        query={"q": query, "location": location, "language": language},
                        error=f"Search failed: {error}",
                        search_engine=self.SEARCH_ENGINE,
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                    )
                last_error = f"Page {pages_fetched + 1} failed: {error}"
                break

            pages_fetched += 1

            # Extract pagination info BEFORE normalizing
            pagination = raw_data.get("pagination", {}) if isinstance(raw_data, dict) else {}

            # Normalize data
            normalized_data = self.data_normalizer.normalize(raw_data)
            page_results = normalized_data.get("results", [])

            if not page_results:
                break

            # Preserve Google's total from first page
            if pages_fetched == 1:
                google_total_results = normalized_data.get("total_results")

            all_results.extend(page_results)

            # Determine next page offset
            next_page_start = pagination.get("next_page_start")

            if next_page_start is None:
                next_link = pagination.get("next_page_link", "")
                if next_link:
                    match = re.search(r"start=(\d+)", next_link)
                    if match:
                        next_page_start = int(match.group(1))

            if next_page_start is None or next_page_start <= current_start:
                break

            current_start = next_page_start

        final_results = all_results[:num_results]

        return SearchResult(
            success=True,
            query={"q": query, "location": location, "language": language},
            data=final_results,
            total_found=google_total_results,
            search_engine=self.SEARCH_ENGINE,
            country=location,
            results_per_page=self.PAGE_SIZE,
            trigger_sent_at=trigger_sent_at,
            data_fetched_at=datetime.now(timezone.utc),
            error=last_error,
        )

    async def _search_multiple_async(
        self,
        queries: List[str],
        zone: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs,
    ) -> List[SearchResult]:
        """Execute multiple search queries concurrently."""
        tasks = [
            self._search_single_async(
                query=q,
                zone=zone,
                location=location,
                language=language,
                device=device,
                num_results=num_results,
                **kwargs,
            )
            for q in queries
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    SearchResult(
                        success=False,
                        query={"q": queries[i]},
                        error=f"Exception: {str(result)}",
                        search_engine=self.SEARCH_ENGINE,
                        trigger_sent_at=datetime.now(timezone.utc),
                        data_fetched_at=datetime.now(timezone.utc),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def _search_single_async_unblocker(
        self,
        query: str,
        zone: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        poll_interval: int,
        poll_timeout: int,
        **kwargs,
    ) -> SearchResult:
        """
        Execute single search using async unblocker endpoints.

        This method:
        1. Builds search URL
        2. Triggers async request via /unblocker/req
        3. Polls /unblocker/get_result until ready or timeout
        4. Fetches and normalizes results

        Note: Response from async endpoint is already parsed SERP data
        (unlike sync endpoint which may wrap it in status_code/body structure).
        """
        trigger_sent_at = datetime.now(timezone.utc)

        # Build search URL with brd_json=1 for parsed results
        search_url = self.url_builder.build(
            query=query,
            location=location,
            language=language,
            device=device,
            num_results=num_results,
            **kwargs,
        )

        # Trigger async request (no customer_id needed - derived from token)
        response_id = await self.async_unblocker.trigger(zone=zone, url=search_url)

        if not response_id:
            return SearchResult(
                success=False,
                query={"q": query},
                error="Failed to trigger async request (no response_id received)",
                search_engine=self.SEARCH_ENGINE,
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=datetime.now(timezone.utc),
            )

        # Poll until ready or timeout
        start_time = datetime.now(timezone.utc)

        while True:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Check timeout
            if elapsed > poll_timeout:
                return SearchResult(
                    success=False,
                    query={"q": query},
                    error=f"Polling timeout after {poll_timeout}s (response_id: {response_id})",
                    search_engine=self.SEARCH_ENGINE,
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=datetime.now(timezone.utc),
                )

            # Check status
            status = await self.async_unblocker.get_status(zone, response_id)

            if status == "ready":
                # Results are ready - fetch them
                data_fetched_at = datetime.now(timezone.utc)

                try:
                    # Fetch results
                    data = await self.async_unblocker.fetch_result(zone, response_id)

                    # Data from async endpoint is already parsed SERP format
                    # The data_normalizer.normalize() will handle it
                    normalized_data = self.data_normalizer.normalize(data)

                    return SearchResult(
                        success=True,
                        query={"q": query, "location": location, "language": language},
                        data=normalized_data.get("results", []),
                        total_found=normalized_data.get("total_results"),
                        search_engine=self.SEARCH_ENGINE,
                        country=location,
                        results_per_page=num_results,
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                    )
                except Exception as e:
                    return SearchResult(
                        success=False,
                        query={"q": query},
                        error=f"Failed to fetch results: {str(e)}",
                        search_engine=self.SEARCH_ENGINE,
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                    )

            elif status == "error":
                return SearchResult(
                    success=False,
                    query={"q": query},
                    error=f"Async request failed (response_id: {response_id})",
                    search_engine=self.SEARCH_ENGINE,
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=datetime.now(timezone.utc),
                )

            # Still pending - wait and retry
            await asyncio.sleep(poll_interval)

    async def _search_multiple_async_unblocker(
        self,
        queries: List[str],
        zone: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        poll_interval: int,
        poll_timeout: int,
        **kwargs,
    ) -> List[SearchResult]:
        """
        Execute multiple searches using async unblocker.

        Triggers all searches concurrently, then polls each independently.
        This is more efficient than sequential execution.
        """
        tasks = [
            self._search_single_async_unblocker(
                query=q,
                zone=zone,
                location=location,
                language=language,
                device=device,
                num_results=num_results,
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
                **kwargs,
            )
            for q in queries
        ]

        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, converting exceptions to SearchResult errors
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    SearchResult(
                        success=False,
                        query={"q": queries[i]},
                        error=f"Exception: {str(result)}",
                        search_engine=self.SEARCH_ENGINE,
                        trigger_sent_at=datetime.now(timezone.utc),
                        data_fetched_at=datetime.now(timezone.utc),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    def _validate_queries(self, queries: List[str]) -> None:
        """Validate search queries."""
        if not queries:
            raise ValidationError("Query list cannot be empty")

        for query in queries:
            if not query or not isinstance(query, str):
                raise ValidationError(f"Invalid query: {query}. Must be non-empty string.")

    def _validate_zone(self, zone: str) -> None:
        """
        Validate zone name format.

        Note: This validates format only. Zone existence and SERP support
        are verified when the API request is made. If a zone doesn't support
        SERP, the API will return an error that will be caught and returned
        as a SearchResult with error field.
        """
        validate_zone_name(zone)
