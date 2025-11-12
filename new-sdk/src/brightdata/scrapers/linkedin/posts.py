"""LinkedIn posts scraper - URL-based extraction."""

import asyncio
from typing import Union, List, Optional
from datetime import datetime, timezone

from ..base import BaseWebScraper
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...exceptions import ValidationError, APIError


class LinkedInPostsScraper(BaseWebScraper):
    """
    LinkedIn posts scraper for URL-based extraction.
    
    Scrapes LinkedIn post data from specific URLs.
    
    Example:
        >>> scraper = LinkedInPostsScraper(bearer_token="token")
        >>> result = scraper.scrape_posts(
        ...     url="https://linkedin.com/feed/update/...",
        ...     sync=True,
        ...     timeout=65
        ... )
    """
    
    DATASET_ID = "gd_lwae11111pwxp6c4ea"  # LinkedIn Posts dataset
    PLATFORM_NAME = "linkedin_posts"
    MIN_POLL_TIMEOUT = 180
    
    async def scrape_posts_async(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn posts from URLs (async).
        
        Args:
            url: Single URL string or list of post URLs (required)
            sync: Synchronous mode (default: True)
            timeout: Request timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult for single URL, or List[ScrapeResult] for multiple URLs
        
        Example:
            >>> result = await scraper.scrape_posts_async(
            ...     url="https://linkedin.com/feed/update/urn:li:activity:123",
            ...     sync=True,
            ...     timeout=65
            ... )
        """
        # Use base scrape_async with appropriate timeout
        actual_timeout = timeout if not sync else 65
        
        return await self.scrape_async(
            urls=url,
            poll_timeout=actual_timeout,
        )
    
    def scrape_posts(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn posts from URLs (sync).
        
        See scrape_posts_async() for full documentation.
        """
        return asyncio.run(self.scrape_posts_async(url, sync, timeout))

