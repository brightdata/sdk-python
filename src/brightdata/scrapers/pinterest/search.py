"""
Pinterest parameter-based discovery scraper.

Supports:
- Posts discovery by keyword
- Posts discovery by profile URL
- Profiles discovery by keyword

API Specifications:
- client.search.pinterest.posts_by_keyword(keyword, ...)         # async
- client.search.pinterest.posts_by_keyword_sync(keyword, ...)    # sync
- client.search.pinterest.posts_by_profile(url, ...)             # async
- client.search.pinterest.posts_by_profile_sync(url, ...)        # sync
- client.search.pinterest.profiles(keyword, ...)                 # async
- client.search.pinterest.profiles_sync(keyword, ...)            # sync
"""

import asyncio
from typing import Any

from ...constants import (
    DEFAULT_COST_PER_RECORD,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_TIMEOUT_MEDIUM,
)
from ...models import ScrapeResult
from ...utils.function_detection import get_caller_function_name
from ..base import ScraperCore


class PinterestSearchScraper(ScraperCore):
    """
    Pinterest scraper for parameter-based content discovery.

    Unlike PinterestScraper (URL-based collection), this class discovers content
    using parameters like keywords, profile URLs, and filters.

    Example:
        >>> scraper = PinterestSearchScraper(bearer_token="...")
        >>>
        >>> # Discover posts by keyword
        >>> result = await scraper.posts_by_keyword(
        ...     keyword="spaghetti recipes",
        ...     videos_only=True
        ... )
        >>>
        >>> # Discover posts from profile
        >>> result = await scraper.posts_by_profile(
        ...     url="https://www.pinterest.com/grandmapowpow/",
        ...     num_of_posts=20
        ... )
        >>>
        >>> # Discover profiles by keyword
        >>> result = await scraper.profiles(keyword="mtv")
    """

    # Dataset IDs
    DATASET_ID_POSTS = "gd_lk0sjs4d21kdr7cnlv"
    DATASET_ID_PROFILES = "gd_lk0zv93c2m9qdph46z"

    # Platform configuration
    PLATFORM_NAME = "pinterest"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = DEFAULT_COST_PER_RECORD

    # Construction (token/engine/api_client/workflow_executor) and async
    # context-manager support are inherited from ScraperCore.

    # ============================================================================
    # INTERNAL HELPERS
    # ============================================================================

    async def _execute_discovery(
        self,
        payload: list[dict[str, Any]],
        dataset_id: str,
        discover_by: str,
        timeout: int,
    ) -> ScrapeResult:
        """
        Execute discovery operation with extra query parameters.

        Args:
            payload: Request payload
            dataset_id: Bright Data dataset identifier
            discover_by: Discovery type (keyword, profile_url)
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

    # ============================================================================
    # POSTS DISCOVERY (by keyword)
    # ============================================================================

    async def posts_by_keyword(
        self,
        keyword: str | list[str],
        videos_only: bool | None = None,
        new_posts: bool | None = None,
        top_posts: bool | None = None,
        food: bool | None = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover Pinterest posts by keyword.

        Args:
            keyword: Search keyword(s)
            videos_only: Only return video pins
            new_posts: Only return new/recent posts
            top_posts: Only return top-performing posts
            food: Filter for food-related content
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered posts

        Example:
            >>> result = await scraper.posts_by_keyword(
            ...     keyword="spaghetti recipes",
            ...     videos_only=True
            ... )
            >>> for post in result.data:
            ...     print(post["title"])
        """
        keywords = [keyword] if isinstance(keyword, str) else keyword

        payload = []
        for kw in keywords:
            item: dict[str, Any] = {"keyword": kw}
            if videos_only is not None:
                item["videos_only"] = videos_only
            if new_posts is not None:
                item["new posts"] = new_posts
            if top_posts is not None:
                item["top posts"] = top_posts
            if food is not None:
                item["food"] = food
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            discover_by="keyword",
            timeout=timeout,
        )

    def posts_by_keyword_sync(
        self,
        keyword: str | list[str],
        videos_only: bool | None = None,
        new_posts: bool | None = None,
        top_posts: bool | None = None,
        food: bool | None = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of posts_by_keyword()."""

        async def _run():
            async with self.engine:
                return await self.posts_by_keyword(
                    keyword, videos_only, new_posts, top_posts, food, timeout
                )

        return asyncio.run(_run())

    # ============================================================================
    # POSTS DISCOVERY (by profile URL)
    # ============================================================================

    async def posts_by_profile(
        self,
        url: str | list[str],
        num_of_posts: int | None = None,
        posts_to_not_include: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover Pinterest posts from a profile URL.

        Args:
            url: Profile URL(s) like https://www.pinterest.com/grandmapowpow/
            num_of_posts: Maximum number of posts to return
            posts_to_not_include: Post IDs to exclude from results
            start_date: Start date filter (MM-DD-YYYY format)
            end_date: End date filter (MM-DD-YYYY format)
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with posts from the profile

        Example:
            >>> result = await scraper.posts_by_profile(
            ...     url="https://www.pinterest.com/grandmapowpow/",
            ...     num_of_posts=20,
            ...     start_date="01-01-2025"
            ... )
        """
        urls = [url] if isinstance(url, str) else url

        payload = []
        for u in urls:
            item: dict[str, Any] = {"url": u}
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if posts_to_not_include:
                item["posts_to_not_include"] = posts_to_not_include
            if start_date:
                item["start_date"] = start_date
            if end_date:
                item["end_date"] = end_date
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            discover_by="profile_url",
            timeout=timeout,
        )

    def posts_by_profile_sync(
        self,
        url: str | list[str],
        num_of_posts: int | None = None,
        posts_to_not_include: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of posts_by_profile()."""

        async def _run():
            async with self.engine:
                return await self.posts_by_profile(
                    url, num_of_posts, posts_to_not_include, start_date, end_date, timeout
                )

        return asyncio.run(_run())

    # ============================================================================
    # PROFILES DISCOVERY (by keyword)
    # ============================================================================

    async def profiles(
        self,
        keyword: str | list[str],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover Pinterest profiles by keyword.

        Args:
            keyword: Search keyword(s) to find profiles
            timeout: Maximum seconds to wait (default: 240)

        Returns:
            ScrapeResult with discovered profiles

        Example:
            >>> result = await scraper.profiles(keyword="mtv")
            >>> for profile in result.data:
            ...     print(profile["username"])
        """
        keywords = [keyword] if isinstance(keyword, str) else keyword

        payload = [{"keyword": kw} for kw in keywords]

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_PROFILES,
            discover_by="keyword",
            timeout=timeout,
        )

    def profiles_sync(
        self,
        keyword: str | list[str],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Synchronous version of profiles()."""

        async def _run():
            async with self.engine:
                return await self.profiles(keyword, timeout)

        return asyncio.run(_run())
