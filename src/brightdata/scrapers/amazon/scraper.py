"""
Amazon Scraper - URL-based extraction for products, reviews, and sellers.

API Specifications:
- client.scrape.amazon.products(url, timeout=240)
- client.scrape.amazon.reviews(url, pastDays, keyWord, numOfReviews, timeout=240)
- client.scrape.amazon.sellers(url, timeout=240)

All methods use standard async workflow (trigger/poll/fetch).
"""

import asyncio
from typing import Union, List, Optional, Any

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, DEFAULT_COST_PER_RECORD


@register("amazon")
class AmazonScraper(BaseWebScraper):
    """
    Amazon scraper for URL-based extraction.

    Extracts structured data from Amazon URLs for:
    - Products
    - Reviews
    - Sellers

    Example:
        >>> scraper = AmazonScraper(bearer_token="token")
        >>>
        >>> # Scrape product
        >>> result = scraper.products(
        ...     url="https://amazon.com/dp/B0CRMZHDG8",
        ...     timeout=240
        ... )
    """

    # Amazon dataset IDs
    DATASET_ID = "gd_l7q7dkf244hwjntr0"  # Amazon Products
    DATASET_ID_REVIEWS = "gd_le8e811kzy4ggddlq"  # Amazon Reviews
    DATASET_ID_SELLERS = "gd_lhotzucw1etoe5iw1k"  # Amazon Sellers

    PLATFORM_NAME = "amazon"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM  # Amazon scrapes can take longer
    COST_PER_RECORD = DEFAULT_COST_PER_RECORD

    # ============================================================================
    # PRODUCTS EXTRACTION (URL-based)
    # ============================================================================

    async def products_async(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon products from URLs (async).

        Uses standard async workflow: trigger job, poll until ready, then fetch results.

        Args:
            url: Single product URL or list of product URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with product data

        Example:
            >>> result = await scraper.products_async(
            ...     url="https://amazon.com/dp/B0CRMZHDG8",
            ...     timeout=240
            ... )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(url=url, dataset_id=self.DATASET_ID, timeout=timeout)

    def products(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon products (sync wrapper).

        See products_async() for documentation.

        Example:
            >>> result = scraper.products(
            ...     url="https://amazon.com/dp/B123",
            ...     timeout=240
            ... )
        """

        async def _run():
            async with self.engine:
                return await self.products_async(url, timeout=timeout)

        return asyncio.run(_run())

    # ============================================================================
    # PRODUCTS TRIGGER/STATUS/FETCH (Manual Control)
    # ============================================================================

    async def products_trigger_async(
        self,
        url: Union[str, List[str]],
    ) -> ScrapeJob:
        """
        Trigger Amazon products scrape (async - manual control).

        Starts a scrape operation and returns immediately with a Job object.
        Use the Job to check status and fetch results when ready.

        Args:
            url: Single product URL or list of product URLs

        Returns:
            ScrapeJob object for status checking and result fetching

        Example:
            >>> # Trigger and manual control
            >>> job = await scraper.products_trigger_async("https://amazon.com/dp/B123")
            >>> print(f"Job ID: {job.snapshot_id}")
            >>>
            >>> # Check status later
            >>> status = await job.status_async()
            >>> if status == "ready":
            ...     data = await job.fetch_async()
        """
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url, sdk_function=sdk_function or "products_trigger"
        )

    def products_trigger(
        self,
        url: Union[str, List[str]],
    ) -> ScrapeJob:
        """Trigger Amazon products scrape (sync wrapper)."""
        return asyncio.run(self.products_trigger_async(url))

    async def products_status_async(self, snapshot_id: str) -> str:
        """
        Check Amazon products scrape status (async).

        Args:
            snapshot_id: Snapshot ID from trigger operation

        Returns:
            Status string: "ready", "in_progress", "error"

        Example:
            >>> status = await scraper.products_status_async(snapshot_id)
        """
        return await self._check_status_async(snapshot_id)

    def products_status(self, snapshot_id: str) -> str:
        """Check Amazon products scrape status (sync wrapper)."""
        return asyncio.run(self.products_status_async(snapshot_id))

    async def products_fetch_async(self, snapshot_id: str) -> Any:
        """
        Fetch Amazon products scrape results (async).

        Args:
            snapshot_id: Snapshot ID from trigger operation

        Returns:
            Product data

        Example:
            >>> data = await scraper.products_fetch_async(snapshot_id)
        """
        return await self._fetch_results_async(snapshot_id)

    def products_fetch(self, snapshot_id: str) -> Any:
        """Fetch Amazon products scrape results (sync wrapper)."""
        return asyncio.run(self.products_fetch_async(snapshot_id))

    # ============================================================================
    # REVIEWS EXTRACTION (URL-based with filters)
    # ============================================================================

    async def reviews_async(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon product reviews from URLs (async).

        Uses standard async workflow: trigger job, poll until ready, then fetch results.

        Args:
            url: Single product URL or list of product URLs (required)
            pastDays: Number of past days to consider reviews from (optional)
            keyWord: Filter reviews by keyword (optional)
            numOfReviews: Number of reviews to scrape (optional)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with reviews data

        Example:
            >>> result = await scraper.reviews_async(
            ...     url="https://amazon.com/dp/B123",
            ...     pastDays=30,
            ...     keyWord="quality",
            ...     numOfReviews=100,
            ...     timeout=240
            ... )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        # Build payload - Amazon Reviews dataset only accepts URL
        # Note: pastDays, keyWord, numOfReviews are not supported by the API
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u} for u in url_list]

        # Use reviews dataset with standard async workflow
        is_single = isinstance(url, str)

        sdk_function = get_caller_function_name()

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_REVIEWS,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
        )

        # Return single or list based on input
        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]

        return result

    def reviews(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon reviews (sync wrapper).

        See reviews_async() for documentation.

        Example:
            >>> result = scraper.reviews(
            ...     url="https://amazon.com/dp/B123",
            ...     pastDays=7,
            ...     numOfReviews=50,
            ...     timeout=240
            ... )
        """

        async def _run():
            async with self.engine:
                return await self.reviews_async(url, pastDays, keyWord, numOfReviews, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # REVIEWS TRIGGER/STATUS/FETCH (Manual Control)
    # ============================================================================

    async def reviews_trigger_async(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
    ) -> ScrapeJob:
        """
        Trigger Amazon reviews scrape (async - manual control).

        Starts a scrape operation and returns immediately with a Job object.

        Args:
            url: Single product URL or list of product URLs
            pastDays: Number of past days to consider reviews from (optional)
            keyWord: Filter reviews by keyword (optional)
            numOfReviews: Number of reviews to scrape (optional)

        Returns:
            ScrapeJob object for status checking and result fetching

        Example:
            >>> job = await scraper.reviews_trigger_async("https://amazon.com/dp/B123", pastDays=30)
            >>> status = await job.status_async()
            >>> data = await job.fetch_async()
        """
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_REVIEWS,
            sdk_function=sdk_function or "reviews_trigger",
        )

    def reviews_trigger(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger Amazon reviews scrape (sync wrapper)."""
        return asyncio.run(self.reviews_trigger_async(url, pastDays, keyWord, numOfReviews))

    async def reviews_status_async(self, snapshot_id: str) -> str:
        """Check Amazon reviews scrape status (async)."""
        return await self._check_status_async(snapshot_id)

    def reviews_status(self, snapshot_id: str) -> str:
        """Check Amazon reviews scrape status (sync wrapper)."""
        return asyncio.run(self.reviews_status_async(snapshot_id))

    async def reviews_fetch_async(self, snapshot_id: str) -> Any:
        """Fetch Amazon reviews scrape results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def reviews_fetch(self, snapshot_id: str) -> Any:
        """Fetch Amazon reviews scrape results (sync wrapper)."""
        return asyncio.run(self.reviews_fetch_async(snapshot_id))

    # ============================================================================
    # SELLERS EXTRACTION (URL-based)
    # ============================================================================

    async def sellers_async(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon seller information from URLs (async).

        Uses standard async workflow: trigger job, poll until ready, then fetch results.

        Args:
            url: Single seller URL or list of seller URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with seller data

        Example:
            >>> result = await scraper.sellers_async(
            ...     url="https://amazon.com/sp?seller=AXXXXXXXXXXX",
            ...     timeout=240
            ... )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(url=url, dataset_id=self.DATASET_ID_SELLERS, timeout=timeout)

    def sellers(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon sellers (sync wrapper).

        See sellers_async() for documentation.
        """

        async def _run():
            async with self.engine:
                return await self.sellers_async(url, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # SELLERS TRIGGER/STATUS/FETCH (Manual Control)
    # ============================================================================

    async def sellers_trigger_async(
        self,
        url: Union[str, List[str]],
    ) -> ScrapeJob:
        """
        Trigger Amazon sellers scrape (async - manual control).

        Starts a scrape operation and returns immediately with a Job object.

        Args:
            url: Single seller URL or list of seller URLs

        Returns:
            ScrapeJob object for status checking and result fetching

        Example:
            >>> job = await scraper.sellers_trigger_async("https://amazon.com/sp?seller=AXXX")
            >>> await job.wait_async()
            >>> data = await job.fetch_async()
        """
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_SELLERS,
            sdk_function=sdk_function or "sellers_trigger",
        )

    def sellers_trigger(
        self,
        url: Union[str, List[str]],
    ) -> ScrapeJob:
        """Trigger Amazon sellers scrape (sync wrapper)."""
        return asyncio.run(self.sellers_trigger_async(url))

    async def sellers_status_async(self, snapshot_id: str) -> str:
        """Check Amazon sellers scrape status (async)."""
        return await self._check_status_async(snapshot_id)

    def sellers_status(self, snapshot_id: str) -> str:
        """Check Amazon sellers scrape status (sync wrapper)."""
        return asyncio.run(self.sellers_status_async(snapshot_id))

    async def sellers_fetch_async(self, snapshot_id: str) -> Any:
        """Fetch Amazon sellers scrape results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def sellers_fetch(self, snapshot_id: str) -> Any:
        """Fetch Amazon sellers scrape results (sync wrapper)."""
        return asyncio.run(self.sellers_fetch_async(snapshot_id))

    # ============================================================================
    # CORE SCRAPING LOGIC (Standard async workflow)
    # ============================================================================

    async def _scrape_urls(
        self,
        url: Union[str, List[str]],
        dataset_id: str,
        timeout: int,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape URLs using standard async workflow (trigger/poll/fetch).

        Args:
            url: URL(s) to scrape
            dataset_id: Amazon dataset ID
            timeout: Maximum wait time in seconds (for polling)

        Returns:
            ScrapeResult(s)
        """
        # Normalize to list
        is_single = isinstance(url, str)
        url_list = [url] if is_single else url

        # Build payload
        payload = [{"url": u} for u in url_list]

        # Use standard async workflow (trigger/poll/fetch)
        sdk_function = get_caller_function_name()

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=dataset_id,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            normalize_func=self.normalize_result,
            sdk_function=sdk_function,
        )

        # Return single or list based on input
        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]

        return result
