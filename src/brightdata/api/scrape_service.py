"""
Scraping service namespace.

Provides hierarchical access to specialized scrapers and generic scraping.
"""

import asyncio
from typing import Union, List, TYPE_CHECKING

from ..models import ScrapeResult

if TYPE_CHECKING:
    from ..client import BrightDataClient


class ScrapeService:
    """
    Scraping service namespace.

    Provides hierarchical access to specialized scrapers and generic scraping.
    """

    def __init__(self, client: "BrightDataClient"):
        """Initialize scrape service with client reference."""
        self._client = client
        self._amazon = None
        self._linkedin = None
        self._chatgpt = None
        self._facebook = None
        self._instagram = None
        self._generic = None

    @property
    def amazon(self):
        """
        Access Amazon scraper.

        Returns:
            AmazonScraper instance for Amazon product scraping and search

        Example:
            >>> # URL-based scraping
            >>> result = client.scrape.amazon.scrape("https://amazon.com/dp/B123")
            >>>
            >>> # Keyword-based search
            >>> result = client.scrape.amazon.products(keyword="laptop")
        """
        if self._amazon is None:
            from ..scrapers.amazon import AmazonScraper

            self._amazon = AmazonScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._amazon

    @property
    def linkedin(self):
        """
        Access LinkedIn scraper.

        Returns:
            LinkedInScraper instance for LinkedIn data extraction

        Example:
            >>> # URL-based scraping
            >>> result = client.scrape.linkedin.scrape("https://linkedin.com/in/johndoe")
            >>>
            >>> # Search for jobs
            >>> result = client.scrape.linkedin.jobs(keyword="python", location="NYC")
            >>>
            >>> # Search for profiles
            >>> result = client.scrape.linkedin.profiles(keyword="data scientist")
            >>>
            >>> # Search for companies
            >>> result = client.scrape.linkedin.companies(keyword="tech startup")
        """
        if self._linkedin is None:
            from ..scrapers.linkedin import LinkedInScraper

            self._linkedin = LinkedInScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._linkedin

    @property
    def chatgpt(self):
        """
        Access ChatGPT scraper.

        Returns:
            ChatGPTScraper instance for ChatGPT interactions

        Example:
            >>> # Single prompt
            >>> result = client.scrape.chatgpt.prompt("Explain async programming")
            >>>
            >>> # Multiple prompts
            >>> result = client.scrape.chatgpt.prompts([
            ...     "What is Python?",
            ...     "What is JavaScript?"
            ... ])
        """
        if self._chatgpt is None:
            from ..scrapers.chatgpt import ChatGPTScraper

            self._chatgpt = ChatGPTScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._chatgpt

    @property
    def facebook(self):
        """
        Access Facebook scraper.

        Returns:
            FacebookScraper instance for Facebook data extraction

        Example:
            >>> # Posts from profile
            >>> result = client.scrape.facebook.posts_by_profile(
            ...     url="https://facebook.com/profile",
            ...     num_of_posts=10
            ... )
            >>>
            >>> # Posts from group
            >>> result = client.scrape.facebook.posts_by_group(
            ...     url="https://facebook.com/groups/example"
            ... )
            >>>
            >>> # Comments from post
            >>> result = client.scrape.facebook.comments(
            ...     url="https://facebook.com/post/123456",
            ...     num_of_comments=100
            ... )
            >>>
            >>> # Reels from profile
            >>> result = client.scrape.facebook.reels(
            ...     url="https://facebook.com/profile"
            ... )
        """
        if self._facebook is None:
            from ..scrapers.facebook import FacebookScraper

            self._facebook = FacebookScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._facebook

    @property
    def instagram(self):
        """
        Access Instagram scraper.

        Returns:
            InstagramScraper instance for Instagram data extraction

        Example:
            >>> # Scrape profile
            >>> result = client.scrape.instagram.profiles(
            ...     url="https://instagram.com/username"
            ... )
            >>>
            >>> # Scrape post
            >>> result = client.scrape.instagram.posts(
            ...     url="https://instagram.com/p/ABC123"
            ... )
            >>>
            >>> # Scrape comments
            >>> result = client.scrape.instagram.comments(
            ...     url="https://instagram.com/p/ABC123"
            ... )
            >>>
            >>> # Scrape reel
            >>> result = client.scrape.instagram.reels(
            ...     url="https://instagram.com/reel/ABC123"
            ... )
        """
        if self._instagram is None:
            from ..scrapers.instagram import InstagramScraper

            self._instagram = InstagramScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._instagram

    @property
    def generic(self):
        """Access generic web scraper (Web Unlocker)."""
        if self._generic is None:
            self._generic = GenericScraper(self._client)
        return self._generic


class GenericScraper:
    """Generic web scraper using Web Unlocker API."""

    def __init__(self, client: "BrightDataClient"):
        """Initialize generic scraper."""
        self._client = client

    async def url_async(
        self,
        url: Union[str, List[str]],
        country: str = "",
        response_format: str = "raw",
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape URL(s) asynchronously."""
        return await self._client.scrape_url_async(
            url=url,
            country=country,
            response_format=response_format,
        )

    def url(self, *args, **kwargs) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape URL(s) synchronously."""

        async def _run():
            async with self._client.engine:
                return await self.url_async(*args, **kwargs)

        return asyncio.run(_run())
