"""
TikTok parameter-based discovery scraper.

Supports:
- Profile discovery by search URL
- Posts discovery by keyword/hashtag
- Posts discovery by profile URL
- Posts discovery by discover/explore URL

API Specifications:
- client.search.tiktok.profiles(search_url, ...)           # async
- client.search.tiktok.profiles_sync(search_url, ...)      # sync
- client.search.tiktok.posts_by_keyword(keyword, ...)      # async
- client.search.tiktok.posts_by_profile(url, ...)          # async
- client.search.tiktok.posts_by_url(url, ...)              # async
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
    COST_PER_RECORD_TIKTOK,
    DEFAULT_TIMEOUT_MEDIUM,
    DEFAULT_POLL_INTERVAL,
)
from ...utils.function_detection import get_caller_function_name


class TikTokSearchScraper:
    """
    TikTok scraper for parameter-based content discovery.

    Unlike TikTokScraper (URL-based collection), this class discovers content
    using parameters like keywords, search URLs, and profile filters.

    Example:
        >>> scraper = TikTokSearchScraper(bearer_token="...")
        >>>
        >>> # Discover profiles by search URL
        >>> result = await scraper.profiles(
        ...     search_url="https://www.tiktok.com/search?q=music"
        ... )
        >>>
        >>> # Discover posts by keyword
        >>> result = await scraper.posts_by_keyword(
        ...     keyword="#trending",
        ...     num_of_posts=50
        ... )
        >>>
        >>> # Discover posts from profile
        >>> result = await scraper.posts_by_profile(
        ...     url="https://www.tiktok.com/@username",
        ...     num_of_posts=20
        ... )
    """

    # Dataset IDs
    DATASET_ID_PROFILES = "gd_l1villgoiiidt09ci"
    DATASET_ID_POSTS = "gd_lu702nij2f790tmv9h"

    # Platform configuration
    PLATFORM_NAME = "tiktok"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = COST_PER_RECORD_TIKTOK

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        engine: Optional[AsyncEngine] = None,
    ):
        """
        Initialize TikTok search scraper.

        Args:
            bearer_token: Bright Data API token. If None, loads from environment.
            engine: Optional AsyncEngine instance for connection reuse.
        """
        self.bearer_token = bearer_token or os.getenv("BRIGHTDATA_API_TOKEN")
        if not self.bearer_token:
            raise ValidationError(
                "Bearer token required for TikTok search. "
                "Provide bearer_token parameter or set BRIGHTDATA_API_TOKEN environment variable."
            )

        # Reuse engine if provided, otherwise create new
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
        """
        Execute discovery operation with extra query parameters.

        Args:
            payload: Request payload
            dataset_id: Bright Data dataset identifier
            discover_by: Discovery type (search_url, keyword, profile_url, url)
            timeout: Maximum seconds to wait

        Returns:
            ScrapeResult with discovered data
        """
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
    # PROFILES DISCOVERY (by search URL)
    # ============================================================================

    async def profiles(
        self,
        search_url: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover TikTok profiles by search/explore URL.

        Args:
            search_url: TikTok search or explore URL(s)
                        Example: "https://www.tiktok.com/search?q=music"
            country: Country code(s) for request context (e.g., "US", "FR")
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered profiles

        Example:
            >>> result = await scraper.profiles(
            ...     search_url="https://www.tiktok.com/search?q=music",
            ...     country="US"
            ... )
            >>> for profile in result.data:
            ...     print(profile["username"])
        """
        urls = [search_url] if isinstance(search_url, str) else search_url
        batch_size = len(urls)
        countries = self._normalize_param(country, batch_size, "")

        payload = [{"search_url": urls[i], "country": countries[i]} for i in range(batch_size)]

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_PROFILES,
            discover_by="search_url",
            timeout=timeout,
        )

    def profiles_sync(
        self,
        search_url: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of profiles()."""

        async def _run():
            async with self.engine:
                return await self.profiles(search_url, country, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # POSTS DISCOVERY (by keyword/hashtag)
    # ============================================================================

    async def posts_by_keyword(
        self,
        keyword: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover TikTok posts by keyword or hashtag.

        Args:
            keyword: Search keyword(s) or hashtag(s)
                     Example: "#artist", "music", "#funnydogs"
            num_of_posts: Maximum number of posts to return
            posts_to_not_include: Post IDs to exclude from results
            country: Country code(s) for request context
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered posts

        Example:
            >>> result = await scraper.posts_by_keyword(
            ...     keyword="#trending",
            ...     num_of_posts=50,
            ...     country="US"
            ... )
            >>> for post in result.data:
            ...     print(post["description"])
        """
        keywords = [keyword] if isinstance(keyword, str) else keyword
        batch_size = len(keywords)
        countries = self._normalize_param(country, batch_size, "")

        payload = []
        for i in range(batch_size):
            item: Dict[str, Any] = {
                "search_keyword": keywords[i],
                "country": countries[i],
            }
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if posts_to_not_include:
                item["posts_to_not_include"] = posts_to_not_include
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            discover_by="keyword",
            timeout=timeout,
        )

    def posts_by_keyword_sync(
        self,
        keyword: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of posts_by_keyword()."""

        async def _run():
            async with self.engine:
                return await self.posts_by_keyword(
                    keyword, num_of_posts, posts_to_not_include, country, timeout
                )

        return asyncio.run(_run())

    # ============================================================================
    # POSTS DISCOVERY (by profile URL)
    # ============================================================================

    async def posts_by_profile(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        what_to_collect: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        post_type: Optional[str] = None,
        country: Optional[str] = None,
        sort_by: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover TikTok posts from a profile URL.

        Args:
            url: Profile URL(s) like https://www.tiktok.com/@username
            num_of_posts: Number of posts to collect (0 for all)
            posts_to_not_include: Post IDs to exclude
            what_to_collect: "Posts & Reposts" or other options
            start_date: Start date filter
            end_date: End date filter
            post_type: Filter by post type
            country: Country code for request context
            sort_by: Sort order for results
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with posts from the profile

        Example:
            >>> result = await scraper.posts_by_profile(
            ...     url="https://www.tiktok.com/@babyariel",
            ...     num_of_posts=20,
            ...     what_to_collect="Posts & Reposts"
            ... )
        """
        urls = [url] if isinstance(url, str) else url

        payload = []
        for u in urls:
            item: Dict[str, Any] = {"url": u}
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if posts_to_not_include:
                item["posts_to_not_include"] = posts_to_not_include
            if what_to_collect:
                item["what_to_collect"] = what_to_collect
            if start_date:
                item["start_date"] = start_date
            if end_date:
                item["end_date"] = end_date
            if post_type:
                item["post_type"] = post_type
            if country:
                item["country"] = country
            if sort_by:
                item["sort_by"] = sort_by
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            discover_by="profile_url",
            timeout=timeout,
        )

    def posts_by_profile_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        what_to_collect: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        post_type: Optional[str] = None,
        country: Optional[str] = None,
        sort_by: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of posts_by_profile()."""

        async def _run():
            async with self.engine:
                return await self.posts_by_profile(
                    url,
                    num_of_posts,
                    posts_to_not_include,
                    what_to_collect,
                    start_date,
                    end_date,
                    post_type,
                    country,
                    sort_by,
                    timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # POSTS DISCOVERY (by discover/explore URL)
    # ============================================================================

    async def posts_by_url(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover TikTok posts by discover/explore URL.

        Args:
            url: TikTok discover URL(s)
                 Example: "https://www.tiktok.com/discover/dog"
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered posts

        Example:
            >>> result = await scraper.posts_by_url(
            ...     url="https://www.tiktok.com/discover/dogs"
            ... )
        """
        urls = [url] if isinstance(url, str) else url
        # Note: API uses uppercase "URL" for this endpoint
        payload = [{"URL": u} for u in urls]

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            discover_by="url",
            timeout=timeout,
        )

    def posts_by_url_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of posts_by_url()."""

        async def _run():
            async with self.engine:
                return await self.posts_by_url(url, timeout)

        return asyncio.run(_run())
