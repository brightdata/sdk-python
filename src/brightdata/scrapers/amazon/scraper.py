"""
Amazon Scraper - URL-based extraction for products, reviews, and sellers.

API Specifications:
- client.scrape.amazon.products(url, timeout=240)        # async
- client.scrape.amazon.products_sync(url, timeout=240)   # sync
- client.scrape.amazon.reviews(url, timeout=240)         # async
- client.scrape.amazon.reviews_sync(url, timeout=240)    # sync
- client.scrape.amazon.sellers(url, timeout=240)         # async
- client.scrape.amazon.sellers_sync(url, timeout=240)    # sync

All async methods use standard async workflow (trigger/poll/fetch).
Sync methods use asyncio.run() internally.
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

    async def products(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon products from URLs.

        Uses standard async workflow: trigger job, poll until ready, then fetch results.

        Args:
            url: Single product URL or list of product URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with product data

        Example:
            >>> async with AmazonScraper(token="...") as scraper:
            ...     result = await scraper.products(
            ...         url="https://amazon.com/dp/B0CRMZHDG8",
            ...         timeout=240
            ...     )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(url=url, dataset_id=self.DATASET_ID, timeout=timeout)


    def products_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon products from URLs (sync version).

        See products() for full documentation.
        """
        async def _run():
            async with self.engine:
                return await self.products(url, timeout)
        return asyncio.run(_run())

    # ============================================================================
    # PRODUCTS TRIGGER/STATUS/FETCH (Manual Control)
    # ============================================================================

    async def products_trigger(
        self,
        url: Union[str, List[str]],
    ) -> ScrapeJob:
        """
        Trigger Amazon products scrape (manual control).

        Starts a scrape operation and returns immediately with a Job object.
        Use the Job to check status and fetch results when ready.

        Args:
            url: Single product URL or list of product URLs

        Returns:
            ScrapeJob object for status checking and result fetching

        Example:
            >>> async with AmazonScraper(token="...") as scraper:
            ...     job = await scraper.products_trigger("https://amazon.com/dp/B123")
            ...     print(f"Job ID: {job.snapshot_id}")
            ...     status = await job.status()
            ...     if status == "ready":
            ...         data = await job.fetch()
        """
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url, sdk_function=sdk_function or "products_trigger"
        )


    def products_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger Amazon products scrape (sync version)."""
        return asyncio.run(self.products_trigger(url))

    async def products_status(self, snapshot_id: str) -> str:
        """
        Check Amazon products scrape status.

        Args:
            snapshot_id: Snapshot ID from trigger operation

        Returns:
            Status string: "ready", "in_progress", "error"

        Example:
            >>> status = await scraper.products_status(snapshot_id)
        """
        return await self._check_status_async(snapshot_id)


    def products_status_sync(self, snapshot_id: str) -> str:
        """Check Amazon products scrape status (sync version)."""
        return asyncio.run(self.products_status(snapshot_id))

    async def products_fetch(self, snapshot_id: str) -> Any:
        """
        Fetch Amazon products scrape results.

        Args:
            snapshot_id: Snapshot ID from trigger operation

        Returns:
            Product data

        Example:
            >>> data = await scraper.products_fetch(snapshot_id)
        """
        return await self._fetch_results_async(snapshot_id)


    def products_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Amazon products scrape results (sync version)."""
        return asyncio.run(self.products_fetch(snapshot_id))

    # ============================================================================
    # REVIEWS EXTRACTION (URL-based with filters)
    # ============================================================================

    async def reviews(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon product reviews from URLs.

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
            >>> async with AmazonScraper(token="...") as scraper:
            ...     result = await scraper.reviews(
            ...         url="https://amazon.com/dp/B123",
            ...         pastDays=30,
            ...         keyWord="quality",
            ...         numOfReviews=100,
            ...         timeout=240
            ...     )
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
        elif not is_single and isinstance(result.data, list):
            from ...models import ScrapeResult

            results = []
            url_list = url if isinstance(url, list) else [url]
            for url_item, data_item in zip(url_list, result.data):
                results.append(
                    ScrapeResult(
                        success=True,
                        data=data_item,
                        url=url_item,
                        platform=result.platform,
                        method=result.method,
                        trigger_sent_at=result.trigger_sent_at,
                        snapshot_id_received_at=result.snapshot_id_received_at,
                        snapshot_polled_at=result.snapshot_polled_at,
                        data_fetched_at=result.data_fetched_at,
                        snapshot_id=result.snapshot_id,
                        cost=result.cost / len(result.data) if result.cost else None,
                    )
                )
            return results
        return result


    def reviews_sync(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon product reviews from URLs (sync version).

        See reviews() for full documentation.
        """
        async def _run():
            async with self.engine:
                return await self.reviews(url, pastDays, keyWord, numOfReviews, timeout)
        return asyncio.run(_run())

    # ============================================================================
    # REVIEWS TRIGGER/STATUS/FETCH (Manual Control)
    # ============================================================================

    async def reviews_trigger(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
    ) -> ScrapeJob:
        """
        Trigger Amazon reviews scrape (manual control).

        Starts a scrape operation and returns immediately with a Job object.

        Args:
            url: Single product URL or list of product URLs
            pastDays: Number of past days to consider reviews from (optional)
            keyWord: Filter reviews by keyword (optional)
            numOfReviews: Number of reviews to scrape (optional)

        Returns:
            ScrapeJob object for status checking and result fetching

        Example:
            >>> job = await scraper.reviews_trigger("https://amazon.com/dp/B123", pastDays=30)
            >>> status = await job.status()
            >>> data = await job.fetch()
        """
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_REVIEWS,
            sdk_function=sdk_function or "reviews_trigger",
        )


    def reviews_trigger_sync(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger Amazon reviews scrape (sync version)."""
        return asyncio.run(self.reviews_trigger(url, pastDays, keyWord, numOfReviews))

    async def reviews_status(self, snapshot_id: str) -> str:
        """Check Amazon reviews scrape status."""
        return await self._check_status_async(snapshot_id)


    def reviews_status_sync(self, snapshot_id: str) -> str:
        """Check Amazon reviews scrape status (sync version)."""
        return asyncio.run(self.reviews_status(snapshot_id))

    async def reviews_fetch(self, snapshot_id: str) -> Any:
        """Fetch Amazon reviews scrape results."""
        return await self._fetch_results_async(snapshot_id)


    def reviews_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Amazon reviews scrape results (sync version)."""
        return asyncio.run(self.reviews_fetch(snapshot_id))

    # ============================================================================
    # SELLERS EXTRACTION (URL-based)
    # ============================================================================

    async def sellers(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon seller information from URLs.

        Uses standard async workflow: trigger job, poll until ready, then fetch results.

        Args:
            url: Single seller URL or list of seller URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with seller data

        Example:
            >>> async with AmazonScraper(token="...") as scraper:
            ...     result = await scraper.sellers(
            ...         url="https://amazon.com/sp?seller=AXXXXXXXXXXX",
            ...         timeout=240
            ...     )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(url=url, dataset_id=self.DATASET_ID_SELLERS, timeout=timeout)


    def sellers_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon seller information from URLs (sync version).

        See sellers() for full documentation.
        """
        async def _run():
            async with self.engine:
                return await self.sellers(url, timeout)
        return asyncio.run(_run())

    # ============================================================================
    # SELLERS TRIGGER/STATUS/FETCH (Manual Control)
    # ============================================================================

    async def sellers_trigger(
        self,
        url: Union[str, List[str]],
    ) -> ScrapeJob:
        """
        Trigger Amazon sellers scrape (manual control).

        Starts a scrape operation and returns immediately with a Job object.

        Args:
            url: Single seller URL or list of seller URLs

        Returns:
            ScrapeJob object for status checking and result fetching

        Example:
            >>> job = await scraper.sellers_trigger("https://amazon.com/sp?seller=AXXX")
            >>> await job.wait()
            >>> data = await job.fetch()
        """
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_SELLERS,
            sdk_function=sdk_function or "sellers_trigger",
        )


    def sellers_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger Amazon sellers scrape (sync version)."""
        return asyncio.run(self.sellers_trigger(url))

    async def sellers_status(self, snapshot_id: str) -> str:
        """Check Amazon sellers scrape status."""
        return await self._check_status_async(snapshot_id)


    def sellers_status_sync(self, snapshot_id: str) -> str:
        """Check Amazon sellers scrape status (sync version)."""
        return asyncio.run(self.sellers_status(snapshot_id))

    async def sellers_fetch(self, snapshot_id: str) -> Any:
        """Fetch Amazon sellers scrape results."""
        return await self._fetch_results_async(snapshot_id)


    def sellers_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Amazon sellers scrape results (sync version)."""
        return asyncio.run(self.sellers_fetch(snapshot_id))

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
        elif not is_single and isinstance(result.data, list):
            from ...models import ScrapeResult

            results = []
            for url_item, data_item in zip(url_list, result.data):
                results.append(
                    ScrapeResult(
                        success=True,
                        data=data_item,
                        url=url_item,
                        platform=result.platform,
                        method=result.method,
                        trigger_sent_at=result.trigger_sent_at,
                        snapshot_id_received_at=result.snapshot_id_received_at,
                        snapshot_polled_at=result.snapshot_polled_at,
                        data_fetched_at=result.data_fetched_at,
                        snapshot_id=result.snapshot_id,
                        cost=result.cost / len(result.data) if result.cost else None,
                    )
                )
            return results
        return result
