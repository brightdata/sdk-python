"""
LinkedIn Scraper - URL-based extraction for profiles, companies, jobs, and posts.

API Specifications:
- client.scrape.linkedin.posts(url, sync=True, timeout=65)
- client.scrape.linkedin.jobs(url, sync=True, timeout=65)
- client.scrape.linkedin.profiles(url, sync=True, timeout=65)
- client.scrape.linkedin.companies(url, sync=True, timeout=65)

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


@register("linkedin")
class LinkedInScraper(BaseWebScraper):
    """
    LinkedIn scraper for URL-based extraction.
    
    Extracts structured data from LinkedIn URLs for:
    - Profiles
    - Companies
    - Jobs
    - Posts
    
    Example:
        >>> scraper = LinkedInScraper(bearer_token="token")
        >>> 
        >>> # Scrape profile
        >>> result = scraper.profiles(
        ...     url="https://linkedin.com/in/johndoe",
        ...     sync=True,
        ...     timeout=65
        ... )
    """
    
    # LinkedIn dataset IDs
    DATASET_ID = "gd_l1oojb10z2jye29kh"  # People Profiles
    DATASET_ID_COMPANIES = "gd_lhkq90okie75oj8mo"  # Companies
    DATASET_ID_JOBS = "gd_lj4v2v5oqpp3qb79j"  # Jobs
    DATASET_ID_POSTS = "gd_lwae11111pwxp6c4ea"  # Posts
    
    PLATFORM_NAME = "linkedin"
    MIN_POLL_TIMEOUT = 180
    COST_PER_RECORD = 0.002
    
    # API endpoints
    SCRAPE_URL = "https://api.brightdata.com/datasets/v3/scrape"  # Sync
    TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"  # Async
    
    # ============================================================================
    # POSTS EXTRACTION (URL-based)
    # ============================================================================
    
    async def posts_async(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn posts from URLs (async).
        
        Args:
            url: Single post URL or list of post URLs (required)
            sync: Synchronous mode - True for immediate response, False for polling
            timeout: Request timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult or List[ScrapeResult]
        
        Example:
            >>> result = await scraper.posts_async(
            ...     url="https://linkedin.com/feed/update/urn:li:activity:123",
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
            dataset_id=self.DATASET_ID_POSTS,
            sync=sync,
            timeout=actual_timeout
        )
    
    def posts(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn posts (sync).
        
        See posts_async() for documentation.
        """
        return asyncio.run(self.posts_async(url, sync, timeout))
    
    # ============================================================================
    # JOBS EXTRACTION (URL-based)
    # ============================================================================
    
    async def jobs_async(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn jobs from URLs (async).
        
        Args:
            url: Single job URL or list of job URLs (required)
            sync: Synchronous mode (default: True)
            timeout: Request timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult or List[ScrapeResult]
        
        Example:
            >>> result = await scraper.jobs_async(
            ...     url="https://linkedin.com/jobs/view/123456",
            ...     sync=True
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        actual_timeout = timeout if sync else (timeout if timeout != 65 else 30)
        
        return await self._scrape_with_mode(
            url=url,
            dataset_id=self.DATASET_ID_JOBS,
            sync=sync,
            timeout=actual_timeout
        )
    
    def jobs(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape LinkedIn jobs (sync)."""
        return asyncio.run(self.jobs_async(url, sync, timeout))
    
    # ============================================================================
    # PROFILES EXTRACTION (URL-based)
    # ============================================================================
    
    async def profiles_async(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn profiles from URLs (async).
        
        Args:
            url: Single profile URL or list of profile URLs (required)
            sync: Synchronous mode (default: True)
            timeout: Request timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult or List[ScrapeResult]
        
        Example:
            >>> result = await scraper.profiles_async(
            ...     url="https://linkedin.com/in/johndoe",
            ...     sync=True
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        actual_timeout = timeout if sync else (timeout if timeout != 65 else 30)
        
        return await self._scrape_with_mode(
            url=url,
            dataset_id=self.DATASET_ID,
            sync=sync,
            timeout=actual_timeout
        )
    
    def profiles(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape LinkedIn profiles (sync)."""
        return asyncio.run(self.profiles_async(url, sync, timeout))
    
    # ============================================================================
    # COMPANIES EXTRACTION (URL-based)
    # ============================================================================
    
    async def companies_async(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn companies from URLs (async).
        
        Args:
            url: Single company URL or list of company URLs (required)
            sync: Synchronous mode (default: True)
            timeout: Request timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult or List[ScrapeResult]
        
        Example:
            >>> result = await scraper.companies_async(
            ...     url="https://linkedin.com/company/microsoft",
            ...     sync=True
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        actual_timeout = timeout if sync else (timeout if timeout != 65 else 30)
        
        return await self._scrape_with_mode(
            url=url,
            dataset_id=self.DATASET_ID_COMPANIES,
            sync=sync,
            timeout=actual_timeout
        )
    
    def companies(
        self,
        url: Union[str, List[str]],
        sync: bool = True,
        timeout: int = 65,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape LinkedIn companies (sync)."""
        return asyncio.run(self.companies_async(url, sync, timeout))
    
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
            dataset_id: LinkedIn dataset ID
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
