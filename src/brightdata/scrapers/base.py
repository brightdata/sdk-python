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
from abc import ABC
from typing import List, Dict, Any, Optional, Union

from ..core.engine import AsyncEngine
from ..models import ScrapeResult
from ..exceptions import ValidationError
from ..utils.validation import validate_url, validate_url_list
from ..utils.function_detection import get_caller_function_name
from ..constants import (
    DEFAULT_POLL_INTERVAL,
    DEFAULT_MIN_POLL_TIMEOUT,
    DEFAULT_COST_PER_RECORD,
)
from .api_client import DatasetAPIClient
from .workflow import WorkflowExecutor


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
            >>> [{"url": "https://example.com"}]
            >>> 
            >>> [{"url": "https://amazon.com/dp/B123", "reviews_count": 100}]
        """
        return [{"url": url} for url in urls]
    
    
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
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)
