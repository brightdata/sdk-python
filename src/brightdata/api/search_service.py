"""
Search service namespace (SERP API).

Provides access to search engine result scrapers with normalized
data across different search engines.
"""

import asyncio
from typing import Optional, Union, List, TYPE_CHECKING

from ..models import SearchResult

if TYPE_CHECKING:
    from ..client import BrightDataClient
    from .serp.google import GoogleSERPService
    from .serp.bing import BingSERPService
    from .serp.yandex import YandexSERPService
    from ..scrapers.amazon.search import AmazonSearchScraper
    from ..scrapers.linkedin.search import LinkedInSearchScraper
    from ..scrapers.chatgpt.search import ChatGPTSearchService
    from ..scrapers.instagram.search import InstagramSearchScraper


class SearchService:
    """
    Search service namespace (SERP API).

    Provides access to search engine result scrapers with normalized
    data across different search engines.

    Example:
        >>> # Google search
        >>> result = client.search.google(
        ...     query="python tutorial",
        ...     location="United States"
        ... )
        >>>
        >>> # Access results
        >>> for item in result.data:
        ...     print(item['title'], item['url'])
    """

    def __init__(self, client: "BrightDataClient"):
        """Initialize search service with client reference."""
        self._client = client
        self._google_service: Optional["GoogleSERPService"] = None
        self._bing_service: Optional["BingSERPService"] = None
        self._yandex_service: Optional["YandexSERPService"] = None
        self._amazon_search: Optional["AmazonSearchScraper"] = None
        self._linkedin_search: Optional["LinkedInSearchScraper"] = None
        self._chatgpt_search: Optional["ChatGPTSearchService"] = None
        self._instagram_search: Optional["InstagramSearchScraper"] = None

    async def google_async(
        self,
        query: Union[str, List[str]],
        location: Optional[str] = None,
        language: str = "en",
        device: str = "desktop",
        num_results: int = 10,
        zone: Optional[str] = None,
        **kwargs,
    ) -> Union[SearchResult, List[SearchResult]]:
        """
        Search Google asynchronously.

        Args:
            query: Search query or list of queries
            location: Geographic location (e.g., "United States", "New York")
            language: Language code (e.g., "en", "es", "fr")
            device: Device type ("desktop", "mobile", "tablet")
            num_results: Number of results to return (default: 10)
            zone: SERP zone (uses client default if not provided)
            **kwargs: Additional Google-specific parameters

        Returns:
            SearchResult with normalized Google search data

        Example:
            >>> result = await client.search.google_async(
            ...     query="python tutorial",
            ...     location="United States",
            ...     num_results=20
            ... )
        """
        from .serp import GoogleSERPService

        if self._google_service is None:
            self._google_service = GoogleSERPService(
                engine=self._client.engine,
                timeout=self._client.timeout,
            )

        zone = zone or self._client.serp_zone
        return await self._google_service.search_async(
            query=query,
            zone=zone,
            location=location,
            language=language,
            device=device,
            num_results=num_results,
            **kwargs,
        )

    def google(
        self, query: Union[str, List[str]], **kwargs
    ) -> Union[SearchResult, List[SearchResult]]:
        """
        Search Google synchronously.

        See google_async() for full documentation.

        Example:
            >>> result = client.search.google(
            ...     query="python tutorial",
            ...     location="United States"
            ... )
        """

        async def _run():
            async with self._client.engine:
                return await self.google_async(query, **kwargs)

        return asyncio.run(_run())

    async def bing_async(
        self,
        query: Union[str, List[str]],
        location: Optional[str] = None,
        language: str = "en",
        num_results: int = 10,
        zone: Optional[str] = None,
        **kwargs,
    ) -> Union[SearchResult, List[SearchResult]]:
        """Search Bing asynchronously."""
        from .serp import BingSERPService

        if self._bing_service is None:
            self._bing_service = BingSERPService(
                engine=self._client.engine,
                timeout=self._client.timeout,
            )

        zone = zone or self._client.serp_zone
        return await self._bing_service.search_async(
            query=query,
            zone=zone,
            location=location,
            language=language,
            num_results=num_results,
            **kwargs,
        )

    def bing(self, query: Union[str, List[str]], **kwargs):
        """Search Bing synchronously."""

        async def _run():
            async with self._client.engine:
                return await self.bing_async(query, **kwargs)

        return asyncio.run(_run())

    async def yandex_async(
        self,
        query: Union[str, List[str]],
        location: Optional[str] = None,
        language: str = "ru",
        num_results: int = 10,
        zone: Optional[str] = None,
        **kwargs,
    ) -> Union[SearchResult, List[SearchResult]]:
        """Search Yandex asynchronously."""
        from .serp import YandexSERPService

        if self._yandex_service is None:
            self._yandex_service = YandexSERPService(
                engine=self._client.engine,
                timeout=self._client.timeout,
            )

        zone = zone or self._client.serp_zone
        return await self._yandex_service.search_async(
            query=query,
            zone=zone,
            location=location,
            language=language,
            num_results=num_results,
            **kwargs,
        )

    def yandex(self, query: Union[str, List[str]], **kwargs):
        """Search Yandex synchronously."""

        async def _run():
            async with self._client.engine:
                return await self.yandex_async(query, **kwargs)

        return asyncio.run(_run())

    @property
    def amazon(self):
        """
        Access Amazon search service for parameter-based discovery.

        Returns:
            AmazonSearchScraper for discovering products by keyword and filters

        Example:
            >>> # Search by keyword
            >>> result = client.search.amazon.products(
            ...     keyword="laptop",
            ...     min_price=50000,  # $500 in cents
            ...     max_price=200000,  # $2000 in cents
            ...     prime_eligible=True
            ... )
            >>>
            >>> # Search by category
            >>> result = client.search.amazon.products(
            ...     keyword="wireless headphones",
            ...     category="electronics",
            ...     condition="new"
            ... )
        """
        if self._amazon_search is None:
            from ..scrapers.amazon.search import AmazonSearchScraper

            self._amazon_search = AmazonSearchScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._amazon_search

    @property
    def linkedin(self):
        """
        Access LinkedIn search service for parameter-based discovery.

        Returns:
            LinkedInSearchScraper for discovering posts, profiles, and jobs

        Example:
            >>> # Discover posts from profile
            >>> result = client.search.linkedin.posts(
            ...     profile_url="https://linkedin.com/in/johndoe",
            ...     start_date="2025-01-01",
            ...     end_date="2025-12-31"
            ... )
            >>>
            >>> # Find profiles by name
            >>> result = client.search.linkedin.profiles(
            ...     firstName="John",
            ...     lastName="Doe"
            ... )
            >>>
            >>> # Find jobs by criteria
            >>> result = client.search.linkedin.jobs(
            ...     keyword="python developer",
            ...     location="New York",
            ...     remote=True
            ... )
        """
        if self._linkedin_search is None:
            from ..scrapers.linkedin.search import LinkedInSearchScraper

            self._linkedin_search = LinkedInSearchScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._linkedin_search

    @property
    def chatGPT(self):
        """
        Access ChatGPT search service for prompt-based discovery.

        Returns:
            ChatGPTSearchService for sending prompts to ChatGPT

        Example:
            >>> # Single prompt
            >>> result = client.search.chatGPT(
            ...     prompt="Explain Python async programming",
            ...     country="us",
            ...     webSearch=True
            ... )
            >>>
            >>> # Batch prompts
            >>> result = client.search.chatGPT(
            ...     prompt=["What is Python?", "What is JavaScript?"],
            ...     country=["us", "us"],
            ...     webSearch=[False, True]
            ... )
        """
        if self._chatgpt_search is None:
            from ..scrapers.chatgpt.search import ChatGPTSearchService

            self._chatgpt_search = ChatGPTSearchService(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._chatgpt_search

    @property
    def instagram(self):
        """
        Access Instagram search service for discovery operations.

        Returns:
            InstagramSearchScraper for discovering posts and reels

        Example:
            >>> # Discover posts from profile
            >>> result = client.search.instagram.posts(
            ...     url="https://instagram.com/username",
            ...     num_of_posts=10,
            ...     post_type="reel"
            ... )
            >>>
            >>> # Discover reels from profile
            >>> result = client.search.instagram.reels(
            ...     url="https://instagram.com/username",
            ...     num_of_posts=50,
            ...     start_date="01-01-2025",
            ...     end_date="12-31-2025"
            ... )
        """
        if self._instagram_search is None:
            from ..scrapers.instagram.search import InstagramSearchScraper

            self._instagram_search = InstagramSearchScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._instagram_search
