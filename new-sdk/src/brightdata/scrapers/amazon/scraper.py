"""
Amazon Scraper - URL-based extraction for products, reviews, and sellers.

API Specifications:
- client.scrape.amazon.products(url, sync=True, timeout=65)
- client.scrape.amazon.reviews(url, pastDays, keyWord, numOfReviews, sync=True, timeout=65)
- client.scrape.amazon.sellers(url, sync=True, timeout=65)

All methods accept:
- url: str | list (required)
- sync: bool (default: True) - True=immediate, False=async polling
- timeout: int (default: 65 for sync, 30 for async)
"""

import asyncio
from typing import Union, List, Optional, Dict, Any
from datetime import datetime, timezone

from ..base import BaseWebScraper
from ..registry import register
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...exceptions import ValidationError, APIError


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
        ...     sync=True,
        ...     timeout=65
        ... )
    """
    
    # Amazon dataset IDs
    DATASET_ID = "gd_l7q7dkf244hwxbl93"  # Amazon Products
    DATASET_ID_REVIEWS = "gd_l1vq6tkpl34p7mq7c"  # Amazon Reviews
    DATASET_ID_SELLERS = "gd_lwjkkolem8c4o7j3s"  # Amazon Sellers
    
    PLATFORM_NAME = "amazon"
    MIN_POLL_TIMEOUT = 240  # Amazon scrapes can take longer
    COST_PER_RECORD = 0.001
    
    # API endpoints
    SCRAPE_URL = "https://api.brightdata.com/datasets/v3/scrape"  # Sync
    TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"  # Async
    STATUS_URL = "https://api.brightdata.com/datasets/v3/progress"
    RESULT_URL = "https://api.brightdata.com/datasets/v3/snapshot"
    
    # ============================================================================
    # PRODUCTS EXTRACTION (URL-based)
    # ============================================================================
    
    async def products_async(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon products from URLs (async).
        
        Args:
            url: Single product URL or list of product URLs (required)
            sync: Synchronous mode - True for immediate response, False for polling
            timeout: Request timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult or List[ScrapeResult] with product data
        
        Example:
            >>> result = await scraper.products_async(
            ...     url="https://amazon.com/dp/B0CRMZHDG8",
            ...     sync=True,
            ...     timeout=65
            ... )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        # Adjust timeout based on sync mode
        actual_timeout = timeout if sync else (timeout if timeout != 65 else 30)
        
        return await self._scrape_with_mode(
            url=url,
            dataset_id=self.DATASET_ID,
            sync=sync,
            timeout=actual_timeout
        )
    
    def products(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon products (sync).
        
        See products_async() for documentation.
        
        Example:
            >>> result = scraper.products(
            ...     url="https://amazon.com/dp/B123",
            ...     sync=True
            ... )
        """
        return asyncio.run(self.products_async(url, sync, timeout))
    
    # ============================================================================
    # REVIEWS EXTRACTION (URL-based with filters)
    # ============================================================================
    
    async def reviews_async(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon product reviews from URLs (async).
        
        Args:
            url: Single product URL or list of product URLs (required)
            pastDays: Number of past days to consider reviews from (optional)
            keyWord: Filter reviews by keyword (optional)
            numOfReviews: Number of reviews to scrape (optional)
            sync: Synchronous mode (default: True)
            timeout: Request timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult or List[ScrapeResult] with reviews data
        
        Example:
            >>> result = await scraper.reviews_async(
            ...     url="https://amazon.com/dp/B123",
            ...     pastDays=30,
            ...     keyWord="quality",
            ...     numOfReviews=100,
            ...     sync=True
            ... )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        # Build custom payload with review filters
        url_list = [url] if isinstance(url, str) else url
        payload = []
        
        for u in url_list:
            item: Dict[str, Any] = {"url": u}
            
            if pastDays is not None:
                item["pastDays"] = pastDays
            if keyWord is not None:
                item["keyWord"] = keyWord
            if numOfReviews is not None:
                item["numOfReviews"] = numOfReviews
            
            payload.append(item)
        
        # Adjust timeout
        actual_timeout = timeout if sync else (timeout if timeout != 65 else 30)
        
        # Use reviews dataset
        return await self._scrape_with_mode_custom_payload(
            url=url,
            payload=payload,
            dataset_id=self.DATASET_ID_REVIEWS,
            sync=sync,
            timeout=actual_timeout
        )
    
    def reviews(
        self,
        url: Union[str, List[str]],
        pastDays: Optional[int] = None,
        keyWord: Optional[str] = None,
        numOfReviews: Optional[int] = None,
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon reviews (sync).
        
        See reviews_async() for documentation.
        
        Example:
            >>> result = scraper.reviews(
            ...     url="https://amazon.com/dp/B123",
            ...     pastDays=7,
            ...     numOfReviews=50
            ... )
        """
        return asyncio.run(self.reviews_async(url, pastDays, keyWord, numOfReviews, sync, timeout))
    
    # ============================================================================
    # SELLERS EXTRACTION (URL-based)
    # ============================================================================
    
    async def sellers_async(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon seller information from URLs (async).
        
        Args:
            url: Single seller URL or list of seller URLs (required)
            sync: Synchronous mode (default: True)
            timeout: Request timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult or List[ScrapeResult] with seller data
        
        Example:
            >>> result = await scraper.sellers_async(
            ...     url="https://amazon.com/sp?seller=AXXXXXXXXXXX",
            ...     sync=True
            ... )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        # Adjust timeout
        actual_timeout = timeout if sync else (timeout if timeout != 65 else 30)
        
        return await self._scrape_with_mode(
            url=url,
            dataset_id=self.DATASET_ID_SELLERS,
            sync=sync,
            timeout=actual_timeout
        )
    
    def sellers(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon sellers (sync).
        
        See sellers_async() for documentation.
        """
        return asyncio.run(self.sellers_async(url, sync, timeout))
    
    # ============================================================================
    # CORE SCRAPING LOGIC (sync vs async modes)
    # ============================================================================
    
    async def _scrape_with_mode(
        self,
        url: Union[str, List[str]],
        dataset_id: str,
        sync: bool,
        timeout: int,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape with sync or async mode.
        
        Args:
            url: URL(s) to scrape
            dataset_id: Amazon dataset ID
            sync: True = /scrape endpoint (immediate), False = /trigger (polling)
            timeout: Request timeout
        
        Returns:
            ScrapeResult(s)
        """
        # Normalize to list
        is_single = isinstance(url, str)
        url_list = [url] if is_single else url
        
        # Build payload
        payload = [{"url": u} for u in url_list]
        
        return await self._scrape_with_mode_custom_payload(
            url=url,
            payload=payload,
            dataset_id=dataset_id,
            sync=sync,
            timeout=timeout
        )
    
    async def _scrape_with_mode_custom_payload(
        self,
        url: Union[str, List[str]],
        payload: List[Dict[str, Any]],
        dataset_id: str,
        sync: bool,
        timeout: int,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape with custom payload and sync/async mode."""
        is_single = isinstance(url, str)
        
        async with self.engine:
            if sync:
                # Synchronous mode - immediate response (shared method)
                result = await self._execute_with_sync_mode(
                    payload=payload,
                    dataset_id=dataset_id,
                    timeout=timeout
                )
            else:
                # Asynchronous mode - trigger/poll/fetch (shared method)
                result = await self._execute_with_async_mode(
                    payload=payload,
                    dataset_id=dataset_id,
                    timeout=timeout
                )
            
            # Return single or list based on input
            if is_single and isinstance(result.data, list) and len(result.data) == 1:
                result.url = url if isinstance(url, str) else url[0]
                result.data = result.data[0]
            
            return result
    
    # Removed - now using shared methods from BaseWebScraper:
    # - _execute_with_sync_mode()
    # - _execute_with_async_mode()
