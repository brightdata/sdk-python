"""
Amazon Scraper - URL-based extraction for products, reviews, and sellers.

API Specifications:
- client.scrape.amazon.products(url, timeout=240)
- client.scrape.amazon.reviews(url, pastDays, keyWord, numOfReviews, timeout=240)
- client.scrape.amazon.sellers(url, timeout=240)

All methods use standard async workflow (trigger/poll/fetch).
"""

import asyncio
from typing import Union, List, Optional, Dict, Any
from datetime import datetime, timezone

from ..base import BaseWebScraper
from ..registry import register
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM
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
        ...     timeout=240
        ... )
    """
    
    # Amazon dataset IDs
    DATASET_ID = "gd_l7q7dkf244hwxbl93"  # Amazon Products
    DATASET_ID_REVIEWS = "gd_l1vq6tkpl34p7mq7c"  # Amazon Reviews
    DATASET_ID_SELLERS = "gd_lwjkkolem8c4o7j3s"  # Amazon Sellers
    
    PLATFORM_NAME = "amazon"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM  # Amazon scrapes can take longer
    COST_PER_RECORD = 0.001
    
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
        
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID,
            timeout=timeout
        )
    
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
        return asyncio.run(self.products_async(url, timeout=timeout))
    
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
        return asyncio.run(self.reviews_async(url, pastDays, keyWord, numOfReviews, timeout))
    
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
        
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_SELLERS,
            timeout=timeout
        )
    
    def sellers(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape Amazon sellers (sync wrapper).
        
        See sellers_async() for documentation.
        """
        return asyncio.run(self.sellers_async(url, timeout))
    
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
