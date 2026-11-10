"""
Search service namespace for search engines, platform discovery, and Bright Search.

Provides access to search engine result scrapers with normalized
data across different search engines.
All methods are async-only. For sync usage, use SyncBrightDataClient.
"""

from typing import Optional, Union, List, Dict, Any, Literal, TYPE_CHECKING

from ..models import SearchResult
from ..bright_search.models import (
    BrightSearchDebug,
    BrightSearchMode,
    BrightSearchPage,
    BrightSearchQuery,
    BrightSearchView,
)

if TYPE_CHECKING:
    from ..client import BrightDataClient
    from ..bright_search.service import BrightSearchService
    from .google import GoogleSERPService
    from .bing import BingSERPService
    from .yandex import YandexSERPService
    from ..scrapers.amazon.search import AmazonSearchScraper
    from ..scrapers.linkedin.search import LinkedInSearchScraper
    from ..scrapers.chatgpt.search import ChatGPTSearchService
    from ..scrapers.instagram.search import InstagramSearchScraper
    from ..scrapers.tiktok.search import TikTokSearchScraper
    from ..scrapers.youtube.search import YouTubeSearchScraper


class SearchService:
    """
    Search service namespace, including direct entity search through Bright Search.

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
        self._tiktok_search: Optional["TikTokSearchScraper"] = None
        self._youtube_search: Optional["YouTubeSearchScraper"] = None
        self._pinterest_search = None
        self._bright_search_service: Optional["BrightSearchService"] = None

    def _bright_search(self) -> "BrightSearchService":
        self._client._ensure_initialized()
        if self._bright_search_service is None:
            from ..bright_search.service import BrightSearchService

            self._bright_search_service = BrightSearchService(self._client.engine)
        return self._bright_search_service

    async def company(
        self,
        query: BrightSearchQuery,
        *,
        mode: BrightSearchMode,
        source: Optional[str] = None,
        view: Optional[BrightSearchView] = None,
        offset: int = 0,
        limit: int = 10,
        debug: Optional[BrightSearchDebug] = None,
    ) -> BrightSearchPage:
        """Search company records and return one Bright Search page.

        Use a structured query with mode="ludicrous", or natural language
        with mode="instant" or "smart". Source and view default on the server
        to linkedin_company and id_only. Each call makes one search request;
        pagination and retries are explicit caller decisions.

        Example:
            >>> async with BrightDataClient(auto_create_zones=False) as client:
            ...     page = await client.search.company(
            ...         "US software companies", mode="instant", view="summary"
            ...     )
            ...     for document in page.documents:
            ...         print(document["bright_id"], document["data"].get("name"))
        """
        return await self._bright_search().search(
            "company",
            query,
            mode=mode,
            source=source,
            view=view,
            offset=offset,
            limit=limit,
            debug=debug,
        )

    async def people(
        self,
        query: BrightSearchQuery,
        *,
        mode: BrightSearchMode,
        source: Optional[str] = None,
        view: Optional[BrightSearchView] = None,
        offset: int = 0,
        limit: int = 10,
        debug: Optional[BrightSearchDebug] = None,
    ) -> BrightSearchPage:
        """Search people records using the same options as company().

        The default source is linkedin_people. All projected entity fields
        are optional; matched is a reached count, not generally a total.
        """
        return await self._bright_search().search(
            "people",
            query,
            mode=mode,
            source=source,
            view=view,
            offset=offset,
            limit=limit,
            debug=debug,
        )

    async def ecom(
        self,
        query: Dict[str, Any],
        *,
        mode: Literal["ludicrous"],
        source: Optional[str] = None,
        view: Optional[BrightSearchView] = None,
        offset: int = 0,
        limit: int = 10,
        debug: Optional[BrightSearchDebug] = None,
    ) -> BrightSearchPage:
        """Search product records with a structured query and mode="ludicrous".

        The default source retail_products supports id_only, full, and custom
        field lists; it does not publish a summary view.
        """
        return await self._bright_search().search(
            "ecom",
            query,
            mode=mode,
            source=source,
            view=view,
            offset=offset,
            limit=limit,
            debug=debug,
        )

    async def google(
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
            >>> async with BrightDataClient() as client:
            ...     result = await client.search.google(
            ...         query="python tutorial",
            ...         location="United States",
            ...         num_results=20
            ...     )
        """
        from .google import GoogleSERPService

        if self._google_service is None:
            self._google_service = GoogleSERPService(
                engine=self._client.engine,
                timeout=self._client.timeout,
            )

        zone = zone or self._client.serp_zone
        return await self._google_service.search(
            query=query,
            zone=zone,
            location=location,
            language=language,
            device=device,
            num_results=num_results,
            **kwargs,
        )

    async def bing(
        self,
        query: Union[str, List[str]],
        location: Optional[str] = None,
        language: str = "en",
        num_results: int = 10,
        zone: Optional[str] = None,
        **kwargs,
    ) -> Union[SearchResult, List[SearchResult]]:
        """Search Bing asynchronously."""
        from .bing import BingSERPService

        if self._bing_service is None:
            self._bing_service = BingSERPService(
                engine=self._client.engine,
                timeout=self._client.timeout,
            )

        zone = zone or self._client.serp_zone
        return await self._bing_service.search(
            query=query,
            zone=zone,
            location=location,
            language=language,
            num_results=num_results,
            **kwargs,
        )

    async def yandex(
        self,
        query: Union[str, List[str]],
        location: Optional[str] = None,
        language: str = "ru",
        num_results: int = 10,
        zone: Optional[str] = None,
        **kwargs,
    ) -> Union[SearchResult, List[SearchResult]]:
        """Search Yandex asynchronously."""
        from .yandex import YandexSERPService

        if self._yandex_service is None:
            self._yandex_service = YandexSERPService(
                engine=self._client.engine,
                timeout=self._client.timeout,
            )

        zone = zone or self._client.serp_zone
        return await self._yandex_service.search(
            query=query,
            zone=zone,
            location=location,
            language=language,
            num_results=num_results,
            **kwargs,
        )

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
    def chatgpt(self):
        """
        Access ChatGPT search service for prompt-based discovery.

        Returns:
            ChatGPTSearchService for sending prompts to ChatGPT

        Example:
            >>> # Single prompt
            >>> result = await client.search.chatgpt.prompt(
            ...     prompt="Explain Python async programming",
            ...     country="us",
            ...     webSearch=True
            ... )
            >>>
            >>> # Batch prompts
            >>> result = await client.search.chatgpt.prompt(
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

    @property
    def tiktok(self):
        """
        Access TikTok search service for discovery operations.

        Returns:
            TikTokSearchScraper for discovering profiles and posts

        Example:
            >>> # Discover profiles by search URL
            >>> result = await client.search.tiktok.profiles(
            ...     search_url="https://www.tiktok.com/search?q=music",
            ...     country="US"
            ... )
            >>>
            >>> # Discover posts by keyword
            >>> result = await client.search.tiktok.posts_by_keyword(
            ...     keyword="#trending",
            ...     num_of_posts=50
            ... )
            >>>
            >>> # Discover posts from profile
            >>> result = await client.search.tiktok.posts_by_profile(
            ...     url="https://www.tiktok.com/@username",
            ...     num_of_posts=20
            ... )
        """
        if self._tiktok_search is None:
            from ..scrapers.tiktok.search import TikTokSearchScraper

            self._tiktok_search = TikTokSearchScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._tiktok_search

    @property
    def youtube(self):
        """
        Access YouTube search service for discovery operations.

        Returns:
            YouTubeSearchScraper for discovering videos and channels

        Example:
            >>> # Discover videos by keyword
            >>> result = await client.search.youtube.videos_by_keyword(
            ...     keyword="python tutorial",
            ...     num_of_videos=20
            ... )
            >>>
            >>> # Discover videos by hashtag
            >>> result = await client.search.youtube.videos_by_hashtag(
            ...     hashtag="#coding",
            ...     num_of_videos=50
            ... )
            >>>
            >>> # Discover videos from channel
            >>> result = await client.search.youtube.videos_by_channel(
            ...     url="https://www.youtube.com/@MrBeast",
            ...     num_of_videos=100
            ... )
            >>>
            >>> # Discover channels by keyword
            >>> result = await client.search.youtube.channels_by_keyword(
            ...     keyword="tech review",
            ...     num_of_channels=10
            ... )
        """
        if self._youtube_search is None:
            from ..scrapers.youtube.search import YouTubeSearchScraper

            self._youtube_search = YouTubeSearchScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._youtube_search

    @property
    def pinterest(self):
        """
        Access Pinterest search service for discovery operations.

        Returns:
            PinterestSearchScraper for discovering posts and profiles

        Example:
            >>> # Discover posts by keyword
            >>> result = await client.search.pinterest.posts_by_keyword(
            ...     keyword="spaghetti recipes",
            ...     videos_only=True
            ... )
            >>>
            >>> # Discover posts from profile
            >>> result = await client.search.pinterest.posts_by_profile(
            ...     url="https://www.pinterest.com/grandmapowpow/",
            ...     num_of_posts=20
            ... )
            >>>
            >>> # Discover profiles by keyword
            >>> result = await client.search.pinterest.profiles(
            ...     keyword="mtv"
            ... )
        """
        if self._pinterest_search is None:
            from ..scrapers.pinterest.search import PinterestSearchScraper

            self._pinterest_search = PinterestSearchScraper(
                bearer_token=self._client.token, engine=self._client.engine
            )
        return self._pinterest_search
