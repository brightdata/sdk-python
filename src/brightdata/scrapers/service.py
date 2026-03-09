"""
Scraping service namespace.

Provides hierarchical access to specialized scrapers and generic scraping.
All methods are async-only. For sync usage, use SyncBrightDataClient.
"""

from typing import TYPE_CHECKING

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
        self._perplexity = None
        self._tiktok = None
        self._youtube = None
        self._digikey = None
        self._reddit = None

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
            from .amazon import AmazonScraper

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
            from .linkedin import LinkedInScraper

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
            from .chatgpt import ChatGPTScraper

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
            from .facebook import FacebookScraper

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
            from .instagram import InstagramScraper

            self._instagram = InstagramScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._instagram

    @property
    def perplexity(self):
        """
        Access Perplexity AI scraper.

        Returns:
            PerplexityScraper instance for Perplexity AI search

        Example:
            >>> # Single search
            >>> result = await client.scrape.perplexity.search(
            ...     prompt="What are the latest AI trends?",
            ...     country="US"
            ... )
            >>>
            >>> # Batch search
            >>> result = await client.scrape.perplexity.search(
            ...     prompt=["What is Python?", "What is JavaScript?"],
            ...     country=["US", "GB"]
            ... )
        """
        if self._perplexity is None:
            from .perplexity import PerplexityScraper

            self._perplexity = PerplexityScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._perplexity

    @property
    def tiktok(self):
        """
        Access TikTok scraper.

        Returns:
            TikTokScraper instance for TikTok data extraction

        Example:
            >>> # Collect profile data
            >>> result = await client.scrape.tiktok.profiles(
            ...     url="https://www.tiktok.com/@username"
            ... )
            >>>
            >>> # Collect posts
            >>> result = await client.scrape.tiktok.posts(
            ...     url="https://www.tiktok.com/@user/video/123456"
            ... )
            >>>
            >>> # Discover posts by keyword
            >>> result = await client.scrape.tiktok.posts_by_keyword(
            ...     keyword="#trending",
            ...     num_of_posts=50
            ... )
            >>>
            >>> # Collect comments
            >>> result = await client.scrape.tiktok.comments(
            ...     url="https://www.tiktok.com/@user/video/123456"
            ... )
            >>>
            >>> # Fast API - posts from profile
            >>> result = await client.scrape.tiktok.posts_by_profile_fast(
            ...     url="https://www.tiktok.com/@bbc"
            ... )
        """
        if self._tiktok is None:
            from .tiktok import TikTokScraper

            self._tiktok = TikTokScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._tiktok

    @property
    def youtube(self):
        """
        Access YouTube scraper.

        Returns:
            YouTubeScraper instance for YouTube data extraction

        Example:
            >>> # Collect video data
            >>> result = await client.scrape.youtube.videos(
            ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            ... )
            >>>
            >>> # Collect channel data
            >>> result = await client.scrape.youtube.channels(
            ...     url="https://www.youtube.com/@MrBeast/about"
            ... )
            >>>
            >>> # Collect comments
            >>> result = await client.scrape.youtube.comments(
            ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            ...     num_of_comments=100
            ... )
        """
        if self._youtube is None:
            from .youtube import YouTubeScraper

            self._youtube = YouTubeScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._youtube

    @property
    def digikey(self):
        """
        Access DigiKey scraper.

        Returns:
            DigiKeyScraper instance for DigiKey product scraping

        Example:
            >>> # Collect product data
            >>> result = await client.scrape.digikey.products(
            ...     url="https://www.digikey.com/en/products/detail/..."
            ... )
            >>>
            >>> # Discover by category
            >>> result = await client.scrape.digikey.discover_by_category(
            ...     url="https://www.digikey.com/en/products/category/..."
            ... )
        """
        if self._digikey is None:
            from .digikey import DigiKeyScraper

            self._digikey = DigiKeyScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._digikey

    @property
    def reddit(self):
        """
        Access Reddit scraper.

        Returns:
            RedditScraper instance for Reddit data extraction

        Example:
            >>> # Collect post data
            >>> result = await client.scrape.reddit.posts(
            ...     url="https://www.reddit.com/r/python/comments/..."
            ... )
            >>>
            >>> # Discover posts by keyword
            >>> result = await client.scrape.reddit.posts_by_keyword(
            ...     keyword="machine learning",
            ...     sort_by="Top"
            ... )
            >>>
            >>> # Collect comments
            >>> result = await client.scrape.reddit.comments(
            ...     url="https://www.reddit.com/r/python/comments/.../comment/..."
            ... )
        """
        if self._reddit is None:
            from .reddit import RedditScraper

            self._reddit = RedditScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._reddit
