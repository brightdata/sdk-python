"""
YouTube parameter-based discovery scraper.

Supports:
- Videos discovery by explore page
- Videos discovery by hashtag
- Videos discovery by keyword
- Videos discovery by search filters
- Videos discovery by channel URL
- Channels discovery by keyword

API Specifications:
- client.search.youtube.videos_by_explore(url, ...)           # async
- client.search.youtube.videos_by_hashtag(hashtag, ...)       # async
- client.search.youtube.videos_by_keyword(keyword, ...)       # async
- client.search.youtube.videos_by_search_filters(...)         # async
- client.search.youtube.videos_by_channel(url, ...)           # async
- client.search.youtube.channels_by_keyword(keyword, ...)     # async
"""

import asyncio
import os
from typing import List, Dict, Any, Optional, Union

from ..api_client import DatasetAPIClient
from ..workflow import WorkflowExecutor
from ...core.engine import AsyncEngine
from ...models import ScrapeResult
from ...exceptions import ValidationError
from ...constants import (
    COST_PER_RECORD_YOUTUBE,
    DEFAULT_TIMEOUT_MEDIUM,
    DEFAULT_POLL_INTERVAL,
)
from ...utils.function_detection import get_caller_function_name


class YouTubeSearchScraper:
    """
    YouTube scraper for parameter-based content discovery.

    Unlike YouTubeScraper (URL-based collection), this class discovers content
    using parameters like keywords, hashtags, search filters, and channel URLs.

    Example:
        >>> scraper = YouTubeSearchScraper(bearer_token="...")
        >>>
        >>> # Discover videos by keyword
        >>> result = await scraper.videos_by_keyword(
        ...     keyword="python tutorial",
        ...     num_of_posts=20
        ... )
        >>>
        >>> # Discover videos by hashtag
        >>> result = await scraper.videos_by_hashtag(
        ...     hashtag="trending",
        ...     num_of_posts=50
        ... )
        >>>
        >>> # Discover videos from channel
        >>> result = await scraper.videos_by_channel(
        ...     url="https://www.youtube.com/@MrBeast/videos",
        ...     num_of_posts=20
        ... )
    """

    # Dataset IDs
    DATASET_ID_VIDEOS = "gd_lk56epmy2i5g7lzu0k"
    DATASET_ID_CHANNELS = "gd_lk538t2k2p1k3oos71"

    # Platform configuration
    PLATFORM_NAME = "youtube"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = COST_PER_RECORD_YOUTUBE

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        engine: Optional[AsyncEngine] = None,
    ):
        """
        Initialize YouTube search scraper.

        Args:
            bearer_token: Bright Data API token. If None, loads from environment.
            engine: Optional AsyncEngine instance for connection reuse.
        """
        self.bearer_token = bearer_token or os.getenv("BRIGHTDATA_API_TOKEN")
        if not self.bearer_token:
            raise ValidationError(
                "Bearer token required for YouTube search. "
                "Provide bearer_token parameter or set BRIGHTDATA_API_TOKEN environment variable."
            )

        self.engine = engine if engine is not None else AsyncEngine(self.bearer_token)
        self.api_client = DatasetAPIClient(self.engine)
        self.workflow_executor = WorkflowExecutor(
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    # ============================================================================
    # CONTEXT MANAGER SUPPORT
    # ============================================================================

    async def __aenter__(self):
        """Async context manager entry."""
        await self.engine.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.engine.__aexit__(exc_type, exc_val, exc_tb)

    # ============================================================================
    # INTERNAL HELPERS
    # ============================================================================

    async def _execute_discovery(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        discover_by: str,
        timeout: int,
    ) -> ScrapeResult:
        """Execute discovery operation with extra query parameters."""
        sdk_function = get_caller_function_name()

        extra_params = {
            "type": "discover_new",
            "discover_by": discover_by,
        }

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=dataset_id,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            extra_params=extra_params,
        )

        return result

    def _normalize_param(
        self,
        param: Optional[Union[Any, List[Any]]],
        target_length: int,
        default_value: Any = None,
    ) -> List[Any]:
        """Normalize parameter to list of specified length."""
        if param is None:
            return [default_value] * target_length

        if isinstance(param, (str, bool, int)):
            return [param] * target_length

        if isinstance(param, list):
            if len(param) < target_length:
                last_val = param[-1] if param else default_value
                return param + [last_val] * (target_length - len(param))
            return param[:target_length]

        return [default_value] * target_length

    # ============================================================================
    # VIDEOS DISCOVERY (by explore page)
    # ============================================================================

    async def videos_by_explore(
        self,
        url: Union[str, List[str]],
        all_tabs: Optional[bool] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover YouTube videos from explore/trending pages.

        Args:
            url: YouTube explore URL(s)
                 Example: "https://www.youtube.com/gaming/games"
            all_tabs: Whether to scrape all tabs on the page
            country: Country code(s) for request context
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered videos

        Example:
            >>> result = await scraper.videos_by_explore(
            ...     url="https://www.youtube.com/gaming/games",
            ...     country="US"
            ... )
        """
        urls = [url] if isinstance(url, str) else url
        batch_size = len(urls)
        countries = self._normalize_param(country, batch_size, "")

        payload = []
        for i in range(batch_size):
            # API expects empty strings for optional fields
            item: Dict[str, Any] = {
                "url": urls[i],
                "country": countries[i],
            }
            if all_tabs is not None:
                item["all_tabs"] = all_tabs
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_VIDEOS,
            discover_by="explore",
            timeout=timeout,
        )

    def videos_by_explore_sync(
        self,
        url: Union[str, List[str]],
        all_tabs: Optional[bool] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of videos_by_explore()."""

        async def _run():
            async with self.engine:
                return await self.videos_by_explore(url, all_tabs, country, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # VIDEOS DISCOVERY (by hashtag)
    # ============================================================================

    async def videos_by_hashtag(
        self,
        hashtag: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover YouTube videos by hashtag.

        Args:
            hashtag: Hashtag(s) to search for (without #)
                     Example: "trending", "music"
            num_of_posts: Maximum number of videos to return
            posts_to_not_include: Video IDs to exclude
            start_date: Filter videos on or after this date (MM-DD-YYYY)
            end_date: Filter videos on or before this date (MM-DD-YYYY)
            country: Country code(s) for request context
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered videos

        Example:
            >>> result = await scraper.videos_by_hashtag(
            ...     hashtag="trending",
            ...     num_of_posts=50,
            ...     country="US"
            ... )
        """
        hashtags = [hashtag] if isinstance(hashtag, str) else hashtag
        batch_size = len(hashtags)
        countries = self._normalize_param(country, batch_size, "")

        payload = []
        for i in range(batch_size):
            # API expects empty strings for optional fields
            item: Dict[str, Any] = {
                "hashtag": hashtags[i],
                "start_date": start_date or "",
                "end_date": end_date or "",
                "country": countries[i],
            }
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if posts_to_not_include:
                item["posts_to_not_include"] = posts_to_not_include
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_VIDEOS,
            discover_by="hashtag",
            timeout=timeout,
        )

    def videos_by_hashtag_sync(
        self,
        hashtag: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of videos_by_hashtag()."""

        async def _run():
            async with self.engine:
                return await self.videos_by_hashtag(
                    hashtag,
                    num_of_posts,
                    posts_to_not_include,
                    start_date,
                    end_date,
                    country,
                    timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # VIDEOS DISCOVERY (by keyword)
    # ============================================================================

    async def videos_by_keyword(
        self,
        keyword: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover YouTube videos by keyword search.

        Args:
            keyword: Search keyword(s)
                     Example: "python tutorial", "best volleyball plays"
            num_of_posts: Maximum number of videos to return
            start_date: Filter videos on or after this date (MM-DD-YYYY)
            end_date: Filter videos on or before this date (MM-DD-YYYY)
            country: Country code(s) for request context
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered videos

        Example:
            >>> result = await scraper.videos_by_keyword(
            ...     keyword="python tutorial",
            ...     num_of_posts=20,
            ...     start_date="01-01-2024",
            ...     end_date="12-31-2024"
            ... )
        """
        keywords = [keyword] if isinstance(keyword, str) else keyword
        batch_size = len(keywords)
        countries = self._normalize_param(country, batch_size, "")

        payload = []
        for i in range(batch_size):
            # API expects empty strings for optional fields
            item: Dict[str, Any] = {
                "keyword": keywords[i],
                "start_date": start_date or "",
                "end_date": end_date or "",
                "country": countries[i],
            }
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_VIDEOS,
            discover_by="keyword",
            timeout=timeout,
        )

    def videos_by_keyword_sync(
        self,
        keyword: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of videos_by_keyword()."""

        async def _run():
            async with self.engine:
                return await self.videos_by_keyword(
                    keyword, num_of_posts, start_date, end_date, country, timeout
                )

        return asyncio.run(_run())

    # ============================================================================
    # VIDEOS DISCOVERY (by search filters)
    # ============================================================================

    async def videos_by_search_filters(
        self,
        keyword_search: Union[str, List[str]],
        upload_date: Optional[str] = None,
        video_type: Optional[str] = None,
        duration: Optional[str] = None,
        features: Optional[str] = None,
        sort_by: Optional[str] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover YouTube videos using search filters.

        Args:
            keyword_search: Search keyword(s)
            upload_date: Filter by upload date
                         Options: "Last hour", "Today", "This week", "This month", "This year"
            video_type: Filter by type - "Video", "Channel", "Playlist", "Movie"
            duration: Filter by duration
                      Options: "Under 4 minutes", "4-20 minutes", "Over 20 minutes"
            features: Filter by features
                      Options: "4K", "HD", "Creative Commons", "360°", "VR180", etc.
            sort_by: Sort order - "Relevance", "Upload date", "View count", "Rating"
            country: Country code(s) for request context
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered videos

        Example:
            >>> result = await scraper.videos_by_search_filters(
            ...     keyword_search="music",
            ...     upload_date="Today",
            ...     video_type="Video",
            ...     duration="Under 4 minutes",
            ...     features="4K"
            ... )
        """
        keywords = [keyword_search] if isinstance(keyword_search, str) else keyword_search
        batch_size = len(keywords)
        countries = self._normalize_param(country, batch_size, "")

        payload = []
        for i in range(batch_size):
            # API expects empty strings for optional fields
            item: Dict[str, Any] = {
                "keyword_search": keywords[i],
                "upload_date": upload_date or "",
                "type": video_type or "",
                "duration": duration or "",
                "features": features or "",
                "sort_by": sort_by or "",
                "country": countries[i],
            }
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_VIDEOS,
            discover_by="search_filters",
            timeout=timeout,
        )

    def videos_by_search_filters_sync(
        self,
        keyword_search: Union[str, List[str]],
        upload_date: Optional[str] = None,
        video_type: Optional[str] = None,
        duration: Optional[str] = None,
        features: Optional[str] = None,
        sort_by: Optional[str] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of videos_by_search_filters()."""

        async def _run():
            async with self.engine:
                return await self.videos_by_search_filters(
                    keyword_search,
                    upload_date,
                    video_type,
                    duration,
                    features,
                    sort_by,
                    country,
                    timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # VIDEOS DISCOVERY (by channel URL)
    # ============================================================================

    async def videos_by_channel(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order_by: Optional[str] = None,
        time_period: Optional[str] = None,
        country: Optional[str] = None,
        transcription_language: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover YouTube videos from a channel URL.

        Args:
            url: Channel videos/shorts/streams URL(s)
                 Example: "https://www.youtube.com/@Shakira/videos"
                          "https://www.youtube.com/@TaylorSwift/shorts"
                          "https://www.youtube.com/@T1_Faker/streams"
            num_of_posts: Maximum number of videos to return (0 for all)
            start_date: Filter videos on or after this date (MM-DD-YYYY)
            end_date: Filter videos on or before this date (MM-DD-YYYY)
            order_by: Sort order - "Latest", "Popular", "Oldest"
            time_period: Time period filter (e.g., "1 year ago", "1 month ago")
            country: Country code for request context
            transcription_language: Language for transcriptions
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered videos

        Example:
            >>> result = await scraper.videos_by_channel(
            ...     url="https://www.youtube.com/@MrBeast/videos",
            ...     num_of_posts=20,
            ...     order_by="Latest"
            ... )
        """
        urls = [url] if isinstance(url, str) else url

        payload = []
        for u in urls:
            # API expects empty strings for optional fields
            item: Dict[str, Any] = {
                "url": u,
                "start_date": start_date or "",
                "end_date": end_date or "",
                "order_by": order_by or "",
                "time_period": time_period or "",
                "country": country or "",
                "transcription_language": transcription_language or "",
            }
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_VIDEOS,
            discover_by="url",
            timeout=timeout,
        )

    def videos_by_channel_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order_by: Optional[str] = None,
        time_period: Optional[str] = None,
        country: Optional[str] = None,
        transcription_language: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of videos_by_channel()."""

        async def _run():
            async with self.engine:
                return await self.videos_by_channel(
                    url,
                    num_of_posts,
                    start_date,
                    end_date,
                    order_by,
                    time_period,
                    country,
                    transcription_language,
                    timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # CHANNELS DISCOVERY (by keyword)
    # ============================================================================

    async def channels_by_keyword(
        self,
        keyword: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover YouTube channels by keyword search.

        Args:
            keyword: Search keyword(s)
                     Example: "popular music", "gaming"
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered channels

        Example:
            >>> result = await scraper.channels_by_keyword(
            ...     keyword="popular music"
            ... )
            >>> for channel in result.data:
            ...     print(channel["name"])
        """
        keywords = [keyword] if isinstance(keyword, str) else keyword
        payload = [{"keyword": kw} for kw in keywords]

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_CHANNELS,
            discover_by="keyword",
            timeout=timeout,
        )

    def channels_by_keyword_sync(
        self,
        keyword: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of channels_by_keyword()."""

        async def _run():
            async with self.engine:
                return await self.channels_by_keyword(keyword, timeout)

        return asyncio.run(_run())
