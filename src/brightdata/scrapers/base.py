"""
Base scraper class for all platform-specific scrapers.

Philosophy:
- Build for future intelligent routing - architecture supports auto-detection
- Each platform should feel familiar once you know one
- Scrape vs search distinction should be clear and consistent
- Platform expertise belongs in platform classes, common patterns in base class
- Single responsibility: public interface and coordination, not implementation
"""

import asyncio
import os
import concurrent.futures
from abc import ABC
from typing import List, Dict, Any, Optional, Union

from ..core.engine import AsyncEngine
from ..models import ScrapeResult
from ..exceptions import ValidationError, APIError
from ..utils.validation import validate_url, validate_url_list
from ..utils.function_detection import get_caller_function_name
from ..constants import (
    DEFAULT_POLL_INTERVAL,
    DEFAULT_MIN_POLL_TIMEOUT,
    DEFAULT_COST_PER_RECORD,
)
from .api_client import DatasetAPIClient
from .workflow import WorkflowExecutor
from .job import ScrapeJob


class BaseWebScraper(ABC):
    """
    Base class for all platform-specific scrapers.

    Provides common patterns for:
    - Trigger/poll/fetch workflow (Datasets API v3)
    - URL-based scraping (scrape method)
    - Parameter-based discovery (search methods - platform-specific)
    - Data normalization and result formatting
    - Error handling and retry logic
    - Cost tracking and timing metrics

    Platform-specific scrapers inherit from this and implement:
    - DATASET_ID: Bright Data dataset identifier
    - Platform-specific search methods
    - Custom data normalization if needed

    Example:
        >>> @register("amazon")
        >>> class AmazonScraper(BaseWebScraper):
        ...     DATASET_ID = "gd_l7q7dkf244hwxbl93"
        ...
        ...     async def products_async(self, keyword: str, **kwargs):
        ...         # Platform-specific search implementation
        ...         pass
    """

    DATASET_ID: str = ""
    PLATFORM_NAME: str = ""
    MIN_POLL_TIMEOUT: int = DEFAULT_MIN_POLL_TIMEOUT
    COST_PER_RECORD: float = DEFAULT_COST_PER_RECORD

    def __init__(self, bearer_token: Optional[str] = None, engine: Optional[AsyncEngine] = None):
        """
        Initialize platform scraper.

        Args:
            bearer_token: Bright Data API token. If None, loads from environment.
            engine: Optional AsyncEngine instance. If provided, reuses the existing engine
                   (recommended when using via client to share connection pool and rate limiter).
                   If None, creates a new engine (for standalone usage).

        Raises:
            ValidationError: If token not provided and not in environment
        """
        self.bearer_token = bearer_token or os.getenv("BRIGHTDATA_API_TOKEN")
        if not self.bearer_token:
            raise ValidationError(
                f"Bearer token required for {self.PLATFORM_NAME or 'scraper'}. "
                f"Provide bearer_token parameter or set BRIGHTDATA_API_TOKEN environment variable."
            )

        # Reuse engine if provided (for resource efficiency), otherwise create new one
        self.engine = engine if engine is not None else AsyncEngine(self.bearer_token)
        self.api_client = DatasetAPIClient(self.engine)
        self.workflow_executor = WorkflowExecutor(
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME or None,
            cost_per_record=self.COST_PER_RECORD,
        )

        if not self.DATASET_ID:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define DATASET_ID class attribute"
            )

    async def scrape_async(
        self,
        urls: Union[str, List[str]],
        include_errors: bool = True,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: Optional[int] = None,
        **kwargs,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape one or more URLs asynchronously.

        This is the URL-based extraction method - provide URLs directly.
        For keyword-based discovery, use platform-specific search methods.

        Args:
            urls: Single URL string or list of URLs to scrape
            include_errors: Include error records in results
            poll_interval: Seconds between status checks (default: 10)
            poll_timeout: Maximum seconds to wait (uses MIN_POLL_TIMEOUT if None)
            **kwargs: Additional platform-specific parameters

        Returns:
            ScrapeResult for single URL, or List[ScrapeResult] for multiple URLs

        Raises:
            ValidationError: If URLs are invalid
            APIError: If API request fails
            TimeoutError: If polling timeout exceeded

        Example:
            >>> scraper = AmazonScraper(bearer_token="token")
            >>> result = await scraper.scrape_async("https://amazon.com/dp/B123")
            >>> print(result.data)
        """
        is_single = isinstance(urls, str)
        url_list = [urls] if is_single else urls

        if is_single:
            validate_url(urls)
        else:
            validate_url_list(url_list)

        payload = self._build_scrape_payload(url_list, **kwargs)
        timeout = poll_timeout or self.MIN_POLL_TIMEOUT

        sdk_function = get_caller_function_name()

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID,
            poll_interval=poll_interval,
            poll_timeout=timeout,
            include_errors=include_errors,
            normalize_func=self.normalize_result,
            sdk_function=sdk_function,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = urls
            result.data = result.data[0]
            return result

        return result

    def scrape(
        self, urls: Union[str, List[str]], **kwargs
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape URLs synchronously.

        See scrape_async() for full documentation.

        Example:
            >>> scraper = AmazonScraper(bearer_token="token")
            >>> result = scraper.scrape("https://amazon.com/dp/B123")
        """
        return asyncio.run(self.scrape_async(urls, **kwargs))

    def normalize_result(self, data: Any) -> Any:
        """
        Normalize result data to consistent format.

        Base implementation returns data as-is. Override in platform-specific
        scrapers to transform API responses into consistent format.

        Args:
            data: Raw data from Bright Data API

        Returns:
            Normalized data in platform-specific format

        Example:
            >>> class AmazonScraper(BaseWebScraper):
            ...     def normalize_result(self, data):
            ...         # Transform Amazon API response
            ...         if isinstance(data, list):
            ...             return [self._normalize_product(item) for item in data]
            ...         return data
        """
        return data

    def _build_scrape_payload(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Build payload for scrape operation.

        Base implementation creates simple URL payload. Override to add
        platform-specific parameters.

        Args:
            urls: List of URLs to scrape
            **kwargs: Additional platform-specific parameters

        Returns:
            Payload list for Datasets API

        Example:
            >>> [{"url": "https://example.com"}]
            >>>
            >>> [{"url": "https://amazon.com/dp/B123", "reviews_count": 100}]
        """
        return [{"url": url} for url in urls]

    # ============================================================================
    # TRIGGER/STATUS/FETCH INTERFACE (Manual Control)
    # ============================================================================

    async def _trigger_scrape_async(
        self, urls: Union[str, List[str]], sdk_function: Optional[str] = None, **kwargs
    ) -> ScrapeJob:
        """
        Trigger scrape job (internal async method).

        Starts a scrape operation and returns a Job object for status checking and result fetching.
        This is the internal implementation - platform scrapers should expose their own
        typed trigger methods (e.g., products_trigger_async, profiles_trigger_async).

        Args:
            urls: URL or list of URLs to scrape
            sdk_function: SDK function name for monitoring
            **kwargs: Additional platform-specific parameters

        Returns:
            ScrapeJob object with snapshot_id

        Example:
            >>> job = await scraper._trigger_scrape_async("https://example.com")
            >>> print(f"Job ID: {job.snapshot_id}")
        """
        # Validate and normalize URLs
        if isinstance(urls, str):
            validate_url(urls)
            url_list = [urls]
        else:
            validate_url_list(urls)
            url_list = urls

        # Build payload
        payload = self._build_scrape_payload(url_list, **kwargs)

        # Trigger via API
        snapshot_id = await self.api_client.trigger(
            payload=payload,
            dataset_id=self.DATASET_ID,
            include_errors=True,
            sdk_function=sdk_function,
        )

        if not snapshot_id:
            raise APIError("Failed to trigger scrape - no snapshot_id returned")

        # Return Job object
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def _trigger_scrape(
        self, urls: Union[str, List[str]], sdk_function: Optional[str] = None, **kwargs
    ) -> ScrapeJob:
        """Trigger scrape job (internal sync wrapper)."""
        return _run_blocking(self._trigger_scrape_async(urls, sdk_function=sdk_function, **kwargs))

    async def _check_status_async(self, snapshot_id: str) -> str:
        """
        Check scrape job status (internal async method).

        Args:
            snapshot_id: Snapshot identifier from trigger operation

        Returns:
            Status string: "ready", "in_progress", "error", etc.

        Example:
            >>> status = await scraper._check_status_async(snapshot_id)
            >>> print(f"Status: {status}")
        """
        return await self.api_client.get_status(snapshot_id)

    def _check_status(self, snapshot_id: str) -> str:
        """Check scrape job status (internal sync wrapper)."""
        return _run_blocking(self._check_status_async(snapshot_id))

    async def _fetch_results_async(self, snapshot_id: str, format: str = "json") -> Any:
        """
        Fetch scrape job results (internal async method).

        Args:
            snapshot_id: Snapshot identifier from trigger operation
            format: Result format ("json" or "raw")

        Returns:
            Scraped data

        Example:
            >>> data = await scraper._fetch_results_async(snapshot_id)
        """
        return await self.api_client.fetch_result(snapshot_id, format=format)

    def _fetch_results(self, snapshot_id: str, format: str = "json") -> Any:
        """Fetch scrape job results (internal sync wrapper)."""
        return _run_blocking(self._fetch_results_async(snapshot_id, format=format))

    def __repr__(self) -> str:
        """String representation for debugging."""
        platform = self.PLATFORM_NAME or self.__class__.__name__
        dataset_id = self.DATASET_ID[:20] + "..." if len(self.DATASET_ID) > 20 else self.DATASET_ID
        return f"<{platform}Scraper dataset_id={dataset_id}>"


def _run_blocking(coro):
    """
    Run coroutine in blocking mode.

    Handles both inside and outside event loop contexts.
    """
    try:
        asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)
