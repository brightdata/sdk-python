"""
LinkedIn Scraper - URL-based extraction for profiles, companies, jobs, and posts.

This module contains the LinkedInScraper class which provides URL-based extraction
for LinkedIn profiles, companies, jobs, and posts. All methods use the standard
async workflow (trigger/poll/fetch).

API Specifications:
- client.scrape.linkedin.posts(url, timeout=180)
- client.scrape.linkedin.jobs(url, timeout=180)
- client.scrape.linkedin.profiles(url, timeout=180)
- client.scrape.linkedin.companies(url, timeout=180)

All methods accept:
- url: str | list (required) - Single URL or list of URLs
- timeout: int (default: 180) - Maximum wait time in seconds for polling

For search/discovery operations, see search.py which contains LinkedInSearchScraper.
"""

import asyncio
from typing import Union, List, Optional, Dict, Any
from datetime import datetime, timezone

from ..base import BaseWebScraper
from ..registry import register
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_SHORT
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
        ...     timeout=180
        ... )
    """
    
    # LinkedIn dataset IDs
    DATASET_ID = "gd_l1oojb10z2jye29kh"  # People Profiles
    DATASET_ID_COMPANIES = "gd_lhkq90okie75oj8mo"  # Companies
    DATASET_ID_JOBS = "gd_lj4v2v5oqpp3qb79j"  # Jobs
    DATASET_ID_POSTS = "gd_lwae11111pwxp6c4ea"  # Posts
    
    PLATFORM_NAME = "linkedin"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_SHORT
    COST_PER_RECORD = 0.002
    
    # ============================================================================
    # POSTS EXTRACTION (URL-based)
    # ============================================================================
    
    async def posts_async(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn posts from URLs (async).
        
        Uses standard async workflow: trigger job, poll until ready, then fetch results.
        
        Args:
            url: Single post URL or list of post URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 180)
        
        Returns:
            ScrapeResult or List[ScrapeResult]
        
        Example:
            >>> result = await scraper.posts_async(
            ...     url="https://linkedin.com/feed/update/urn:li:activity:123",
            ...     timeout=180
            ... )
        """
        # Validate URLs
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_POSTS,
            timeout=timeout
        )
    
    def posts(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn posts (sync wrapper).
        
        See posts_async() for documentation.
        """
        return asyncio.run(self.posts_async(url, timeout))
    
    # ============================================================================
    # JOBS EXTRACTION (URL-based)
    # ============================================================================
    
    async def jobs_async(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn jobs from URLs (async).
        
        Uses standard async workflow: trigger job, poll until ready, then fetch results.
        
        Args:
            url: Single job URL or list of job URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 180)
        
        Returns:
            ScrapeResult or List[ScrapeResult]
        
        Example:
            >>> result = await scraper.jobs_async(
            ...     url="https://linkedin.com/jobs/view/123456",
            ...     timeout=180
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_JOBS,
            timeout=timeout
        )
    
    def jobs(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape LinkedIn jobs (sync wrapper)."""
        return asyncio.run(self.jobs_async(url, timeout))
    
    # ============================================================================
    # PROFILES EXTRACTION (URL-based)
    # ============================================================================
    
    async def profiles_async(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn profiles from URLs (async).
        
        Uses standard async workflow: trigger job, poll until ready, then fetch results.
        
        Args:
            url: Single profile URL or list of profile URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 180)
        
        Returns:
            ScrapeResult or List[ScrapeResult]
        
        Example:
            >>> result = await scraper.profiles_async(
            ...     url="https://linkedin.com/in/johndoe",
            ...     timeout=180
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID,
            timeout=timeout
        )
    
    def profiles(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape LinkedIn profiles (sync wrapper)."""
        return asyncio.run(self.profiles_async(url, timeout))
    
    # ============================================================================
    # COMPANIES EXTRACTION (URL-based)
    # ============================================================================
    
    async def companies_async(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape LinkedIn companies from URLs (async).
        
        Uses standard async workflow: trigger job, poll until ready, then fetch results.
        
        Args:
            url: Single company URL or list of company URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 180)
        
        Returns:
            ScrapeResult or List[ScrapeResult]
        
        Example:
            >>> result = await scraper.companies_async(
            ...     url="https://linkedin.com/company/microsoft",
            ...     timeout=180
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)
        
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_COMPANIES,
            timeout=timeout
        )
    
    def companies(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape LinkedIn companies (sync wrapper)."""
        return asyncio.run(self.companies_async(url, timeout))
    
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
            dataset_id: LinkedIn dataset ID
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
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
        )
        
        # Return single or list based on input
        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]
        
        return result
