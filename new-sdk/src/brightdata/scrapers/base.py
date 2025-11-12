"""
Base scraper class for all platform-specific scrapers.

Philosophy:
- Build for future intelligent routing - architecture supports auto-detection
- Each platform should feel familiar once you know one
- Scrape vs search distinction should be clear and consistent
- Platform expertise belongs in platform classes, common patterns in base class
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone

from ..core.engine import AsyncEngine
from ..models import ScrapeResult
from ..exceptions import ValidationError, APIError, TimeoutError
from ..utils.validation import validate_url, validate_url_list


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
    
    # Class attributes (must be overridden by subclasses)
    DATASET_ID: str = ""
    PLATFORM_NAME: str = ""
    MIN_POLL_TIMEOUT: int = 180  # Minimum recommended timeout for this platform
    COST_PER_RECORD: float = 0.001  # Approximate cost per record
    
    # API endpoints
    TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"
    STATUS_URL = "https://api.brightdata.com/datasets/v3/progress"
    RESULT_URL = "https://api.brightdata.com/datasets/v3/snapshot"
    
    def __init__(self, bearer_token: Optional[str] = None):
        """
        Initialize platform scraper.
        
        Args:
            bearer_token: Bright Data API token. If None, loads from environment.
        
        Raises:
            ValidationError: If token not provided and not in environment
        """
        import os
        
        self.bearer_token = bearer_token or os.getenv("BRIGHTDATA_API_TOKEN")
        if not self.bearer_token:
            raise ValidationError(
                f"Bearer token required for {self.PLATFORM_NAME or 'scraper'}. "
                f"Provide bearer_token parameter or set BRIGHTDATA_API_TOKEN environment variable."
            )
        
        self.engine = AsyncEngine(self.bearer_token)
        
        # Verify subclass defined required attributes
        if not self.DATASET_ID:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define DATASET_ID class attribute"
            )
    
    # ============================================================================
    # CORE SCRAPING METHODS (URL-based extraction)
    # ============================================================================
    
    async def scrape_async(
        self,
        urls: Union[str, List[str]],
        include_errors: bool = True,
        poll_interval: int = 10,
        poll_timeout: Optional[int] = None,
        **kwargs
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
        # Normalize to list
        is_single = isinstance(urls, str)
        url_list = [urls] if is_single else urls
        
        # Validate URLs
        if is_single:
            validate_url(urls)
        else:
            validate_url_list(url_list)
        
        # Build payload
        payload = self._build_scrape_payload(url_list, **kwargs)
        
        # Execute trigger/poll/fetch workflow
        timeout = poll_timeout or self.MIN_POLL_TIMEOUT
        result = await self._execute_workflow_async(
            payload=payload,
            include_errors=include_errors,
            poll_interval=poll_interval,
            poll_timeout=timeout
        )
        
        # Return single result or list based on input
        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            # Extract single result from list
            result.url = urls
            result.data = result.data[0]
            return result
        
        return result
    
    def scrape(
        self,
        urls: Union[str, List[str]],
        **kwargs
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape URLs synchronously.
        
        See scrape_async() for full documentation.
        
        Example:
            >>> scraper = AmazonScraper(bearer_token="token")
            >>> result = scraper.scrape("https://amazon.com/dp/B123")
        """
        return asyncio.run(self.scrape_async(urls, **kwargs))
    
    # ============================================================================
    # WORKFLOW EXECUTION (Trigger → Poll → Fetch)
    # ============================================================================
    
    async def _execute_workflow_async(
        self,
        payload: List[Dict[str, Any]],
        include_errors: bool,
        poll_interval: int,
        poll_timeout: int,
    ) -> ScrapeResult:
        """
        Execute the complete trigger/poll/fetch workflow.
        
        1. Trigger: Send scrape request, get snapshot_id
        2. Poll: Wait for status to be "ready"
        3. Fetch: Retrieve the data
        
        Args:
            payload: Request payload for dataset API
            include_errors: Include error records
            poll_interval: Polling interval in seconds
            poll_timeout: Maximum wait time in seconds
        
        Returns:
            ScrapeResult with data or error
        """
        request_sent_at = datetime.now(timezone.utc)
        
        async with self.engine:
            # Step 1: Trigger collection
            snapshot_id = await self._trigger_async(payload, include_errors)
            
            if not snapshot_id:
                return ScrapeResult(
                    success=False,
                    url="",
                    status="error",
                    error="Failed to trigger scrape - no snapshot_id returned",
                    request_sent_at=request_sent_at,
                    data_received_at=datetime.now(timezone.utc),
                    platform=self.PLATFORM_NAME or None,
                )
            
            snapshot_id_received_at = datetime.now(timezone.utc)
            
            # Step 2 & 3: Poll until ready and fetch data
            result = await self._poll_and_fetch_async(
                snapshot_id=snapshot_id,
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
                request_sent_at=request_sent_at,
                snapshot_id_received_at=snapshot_id_received_at,
            )
            
            return result
    
    async def _trigger_async(
        self,
        payload: List[Dict[str, Any]],
        include_errors: bool,
    ) -> Optional[str]:
        """
        Trigger dataset collection and get snapshot_id.
        
        Args:
            payload: Request payload
            include_errors: Include error records
        
        Returns:
            snapshot_id or None if trigger failed
        """
        params = {
            "dataset_id": self.DATASET_ID,
            "include_errors": str(include_errors).lower(),
        }
        
        async with self.engine._session.post(
            self.TRIGGER_URL,
            json=payload,
            params=params,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("snapshot_id")
            else:
                error_text = await response.text()
                raise APIError(
                    f"Trigger failed (HTTP {response.status}): {error_text}",
                    status_code=response.status
                )
    
    async def _poll_and_fetch_async(
        self,
        snapshot_id: str,
        poll_interval: int,
        poll_timeout: int,
        request_sent_at: datetime,
        snapshot_id_received_at: datetime,
    ) -> ScrapeResult:
        """
        Poll snapshot until ready, then fetch results.
        
        Uses shared polling utility for consistent behavior.
        
        Args:
            snapshot_id: Snapshot identifier
            poll_interval: Seconds between polls
            poll_timeout: Maximum wait time
            request_sent_at: Original request timestamp
            snapshot_id_received_at: When snapshot_id was received
        
        Returns:
            ScrapeResult with data or error/timeout status
        """
        from ..utils.polling import poll_until_ready
        
        result = await poll_until_ready(
            get_status_func=self._get_status_async,
            fetch_result_func=self._fetch_result_async,
            snapshot_id=snapshot_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            request_sent_at=request_sent_at,
            snapshot_id_received_at=snapshot_id_received_at,
            platform=self.PLATFORM_NAME or None,
            cost_per_record=self.COST_PER_RECORD,
        )
        
        # Apply normalization if we got data
        if result.success and result.data:
            result.data = self.normalize_result(result.data)
        
        return result
    
    async def _get_status_async(self, snapshot_id: str) -> str:
        """Get snapshot status."""
        url = f"{self.STATUS_URL}/{snapshot_id}"
        
        async with self.engine._session.get(
            url,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("status", "unknown")
            else:
                return "error"
    
    async def _fetch_result_async(self, snapshot_id: str) -> Any:
        """Fetch snapshot results."""
        url = f"{self.RESULT_URL}/{snapshot_id}"
        params = {"format": "json"}
        
        async with self.engine._session.get(
            url,
            params=params,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise APIError(
                    f"Failed to fetch results (HTTP {response.status}): {error_text}",
                    status_code=response.status
                )
    
    # ============================================================================
    # DATA NORMALIZATION (Override in subclasses if needed)
    # ============================================================================
    
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
    
    # ============================================================================
    # PAYLOAD BUILDING (Override in subclasses for custom parameters)
    # ============================================================================
    
    def _build_scrape_payload(
        self,
        urls: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
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
            >>> # Base implementation
            >>> [{"url": "https://example.com"}]
            >>> 
            >>> # Platform override might add parameters:
            >>> [{"url": "https://amazon.com/dp/B123", "reviews_count": 100}]
        """
        return [{"url": url} for url in urls]
    
    # ============================================================================
    # ABSTRACT METHODS (Platform-specific search - must implement)
    # ============================================================================
    
    # NOTE: Search methods are platform-specific and defined in subclasses
    # Examples:
    # - LinkedInScraper: jobs(), profiles(), companies()
    # - AmazonScraper: products(), reviews()
    # - InstagramScraper: posts(), profiles()
    
    # ============================================================================
    # SYNC/ASYNC MODE SUPPORT (for platforms that need it)
    # ============================================================================
    
    SCRAPE_URL_SYNC = "https://api.brightdata.com/datasets/v3/scrape"
    
    async def _execute_with_sync_mode(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        timeout: int,
    ) -> ScrapeResult:
        """
        Execute scrape using sync mode (/scrape endpoint - immediate response).
        
        Shared implementation for platforms that support sync mode.
        Returns results immediately without polling.
        
        Args:
            payload: Request payload
            dataset_id: Dataset identifier
            timeout: Request timeout in seconds
        
        Returns:
            ScrapeResult with immediate data or error
        """
        request_sent_at = datetime.now(timezone.utc)
        
        params = {"dataset_id": dataset_id}
        
        async with self.engine._session.post(
            self.SCRAPE_URL_SYNC,
            json=payload,
            params=params,
            headers=self.engine._session.headers,
            timeout=timeout
        ) as response:
            data_received_at = datetime.now(timezone.utc)
            
            if response.status == 200:
                data = await response.json()
                row_count = len(data) if isinstance(data, list) else None
                cost = (row_count * self.COST_PER_RECORD) if row_count else None
                
                return ScrapeResult(
                    success=True,
                    url="",
                    status="ready",
                    data=data,
                    cost=cost,
                    platform=self.PLATFORM_NAME or None,
                    request_sent_at=request_sent_at,
                    data_received_at=data_received_at,
                    row_count=row_count,
                )
            else:
                error_text = await response.text()
                return ScrapeResult(
                    success=False,
                    url="",
                    status="error",
                    error=f"Scrape failed (HTTP {response.status}): {error_text}",
                    platform=self.PLATFORM_NAME or None,
                    request_sent_at=request_sent_at,
                    data_received_at=data_received_at,
                )
    
    async def _execute_with_async_mode(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        timeout: int,
    ) -> ScrapeResult:
        """
        Execute scrape using async mode (/trigger endpoint - requires polling).
        
        Shared implementation for platforms that support async mode.
        Triggers job, then polls until ready.
        
        Args:
            payload: Request payload
            dataset_id: Dataset identifier
            timeout: Maximum wait time in seconds
        
        Returns:
            ScrapeResult with polled data or error
        """
        request_sent_at = datetime.now(timezone.utc)
        
        # Trigger
        snapshot_id = await self._trigger_async(
            payload=payload,
            include_errors=True,
            dataset_id=dataset_id
        )
        
        if not snapshot_id:
            return ScrapeResult(
                success=False,
                url="",
                status="error",
                error="No snapshot_id returned from trigger",
                platform=self.PLATFORM_NAME or None,
                request_sent_at=request_sent_at,
                data_received_at=datetime.now(timezone.utc),
            )
        
        snapshot_id_received_at = datetime.now(timezone.utc)
        
        # Use shared polling utility
        from ..utils.polling import poll_until_ready
        
        result = await poll_until_ready(
            get_status_func=self._get_status_async,
            fetch_result_func=self._fetch_result_async,
            snapshot_id=snapshot_id,
            poll_interval=10,
            poll_timeout=timeout,
            request_sent_at=request_sent_at,
            snapshot_id_received_at=snapshot_id_received_at,
            platform=self.PLATFORM_NAME or None,
            cost_per_record=self.COST_PER_RECORD,
        )
        
        return result
    
    async def _trigger_async(
        self,
        payload: List[Dict[str, Any]],
        include_errors: bool,
        dataset_id: str | None = None,
    ) -> str | None:
        """
        Trigger dataset collection with optional dataset override.
        
        Args:
            payload: Request payload
            include_errors: Include error records
            dataset_id: Dataset ID (uses self.DATASET_ID if None)
        
        Returns:
            snapshot_id or None if trigger failed
        """
        ds_id = dataset_id or self.DATASET_ID
        
        params = {
            "dataset_id": ds_id,
            "include_errors": str(include_errors).lower(),
        }
        
        async with self.engine._session.post(
            self.TRIGGER_URL,
            json=payload,
            params=params,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("snapshot_id")
            else:
                error_text = await response.text()
                raise APIError(
                    f"Trigger failed (HTTP {response.status}): {error_text}",
                    status_code=response.status
                )
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        platform = self.PLATFORM_NAME or self.__class__.__name__
        dataset_id = self.DATASET_ID[:20] + "..." if len(self.DATASET_ID) > 20 else self.DATASET_ID
        return f"<{platform}Scraper dataset_id={dataset_id}>"


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def _run_blocking(coro):
    """
    Run coroutine in blocking mode.
    
    Handles both inside and outside event loop contexts.
    """
    try:
        loop = asyncio.get_running_loop()
        # Inside event loop - use thread pool
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No event loop - use asyncio.run()
        return asyncio.run(coro)
