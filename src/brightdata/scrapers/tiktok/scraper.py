"""
TikTok scraper - URL-based collection for profiles, posts, comments, and fast API variants.

Supports:
- Profiles: collect by URL
- Posts: collect by URL
- Comments: collect by URL
- Fast API variants for high-speed scraping

For discovery/search operations, see search.py which contains TikTokSearchScraper.

API Specifications:
- client.scrape.tiktok.profiles(url, ...)                    # async
- client.scrape.tiktok.profiles_sync(url, ...)               # sync
- client.scrape.tiktok.posts(url, ...)                       # async
- client.scrape.tiktok.posts_sync(url, ...)                  # sync
- client.scrape.tiktok.comments(url, ...)                    # async
- client.scrape.tiktok.comments_sync(url, ...)               # sync
- client.scrape.tiktok.posts_by_profile_fast(url, ...)       # async (fast API)
- client.scrape.tiktok.posts_by_url_fast(url, ...)           # async (fast API)
- client.scrape.tiktok.posts_by_search_url_fast(url, ...)    # async (fast API)
"""

import asyncio
from typing import List, Any, Optional, Union, Dict

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, COST_PER_RECORD_TIKTOK


@register("tiktok")
class TikTokScraper(BaseWebScraper):
    """
    TikTok scraper for URL-based collection.

    Extracts structured data from TikTok URLs for:
    - Profiles
    - Posts (videos)
    - Comments
    - Fast API variants for high-speed scraping

    For discovery operations (by keyword, search URL, etc.), use TikTokSearchScraper.

    Example:
        >>> scraper = TikTokScraper(bearer_token="token")
        >>>
        >>> # Collect profile data
        >>> result = await scraper.profiles(
        ...     url="https://www.tiktok.com/@username"
        ... )
        >>>
        >>> # Collect post data
        >>> result = await scraper.posts(
        ...     url="https://www.tiktok.com/@user/video/123456"
        ... )
        >>>
        >>> # Collect comments
        >>> result = await scraper.comments(
        ...     url="https://www.tiktok.com/@user/video/123456"
        ... )
    """

    # Dataset IDs
    DATASET_ID = "gd_l1villgoiiidt09ci"  # Profiles (default)
    DATASET_ID_PROFILES = "gd_l1villgoiiidt09ci"
    DATASET_ID_POSTS = "gd_lu702nij2f790tmv9h"
    DATASET_ID_COMMENTS = "gd_lkf2st302ap89utw5k"
    DATASET_ID_POSTS_BY_PROFILE_FAST = "gd_m7n5v2gq296pex2f5m"
    DATASET_ID_POSTS_BY_URL_FAST = "gd_m736hjp71lejc5dc0l"
    DATASET_ID_POSTS_BY_SEARCH_URL_FAST = "gd_m7n5ixlw1gc4no56kx"

    PLATFORM_NAME = "tiktok"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = COST_PER_RECORD_TIKTOK

    # ============================================================================
    # PROFILES - Collect by URL
    # ============================================================================

    async def profiles(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect TikTok profile data by URL (async).

        Args:
            url: Profile URL(s) like https://www.tiktok.com/@username
            country: Country code for request context (optional)
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with profile data

        Example:
            >>> result = await scraper.profiles(
            ...     url="https://www.tiktok.com/@username"
            ... )
            >>> print(result.data)
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_PROFILES,
            timeout=timeout,
            country=country,
        )

    def profiles_sync(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect TikTok profile data by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.profiles(url, country, timeout)

        return asyncio.run(_run())

    # --- Profiles Trigger/Status/Fetch ---

    async def profiles_trigger(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
    ) -> ScrapeJob:
        """Trigger TikTok profiles collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u, "country": country or ""} for u in url_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_PROFILES
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def profiles_trigger_sync(
        self, url: Union[str, List[str]], country: Optional[str] = None
    ) -> ScrapeJob:
        """Trigger TikTok profiles collection (sync)."""
        return asyncio.run(self.profiles_trigger(url, country))

    async def profiles_status(self, snapshot_id: str) -> str:
        """Check TikTok profiles collection status."""
        return await self._check_status_async(snapshot_id)

    def profiles_status_sync(self, snapshot_id: str) -> str:
        """Check TikTok profiles collection status (sync)."""
        return asyncio.run(self.profiles_status(snapshot_id))

    async def profiles_fetch(self, snapshot_id: str) -> Any:
        """Fetch TikTok profiles results."""
        return await self._fetch_results_async(snapshot_id)

    def profiles_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch TikTok profiles results (sync)."""
        return asyncio.run(self.profiles_fetch(snapshot_id))

    # ============================================================================
    # POSTS - Collect by URL
    # ============================================================================

    async def posts(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect TikTok post data by URL (async).

        Args:
            url: Post URL(s) like https://www.tiktok.com/@user/video/123456
            country: Country code for request context (optional)
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with post data

        Example:
            >>> result = await scraper.posts(
            ...     url="https://www.tiktok.com/@user/video/7433494424040017194"
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_POSTS,
            timeout=timeout,
            country=country,
        )

    def posts_sync(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect TikTok post data by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts(url, country, timeout)

        return asyncio.run(_run())

    # --- Posts Trigger/Status/Fetch ---

    async def posts_trigger(
        self, url: Union[str, List[str]], country: Optional[str] = None
    ) -> ScrapeJob:
        """Trigger TikTok posts collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u, "country": country or ""} for u in url_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_POSTS
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def posts_trigger_sync(
        self, url: Union[str, List[str]], country: Optional[str] = None
    ) -> ScrapeJob:
        """Trigger TikTok posts collection (sync)."""
        return asyncio.run(self.posts_trigger(url, country))

    async def posts_status(self, snapshot_id: str) -> str:
        """Check TikTok posts collection status."""
        return await self._check_status_async(snapshot_id)

    def posts_status_sync(self, snapshot_id: str) -> str:
        """Check TikTok posts collection status (sync)."""
        return asyncio.run(self.posts_status(snapshot_id))

    async def posts_fetch(self, snapshot_id: str) -> Any:
        """Fetch TikTok posts results."""
        return await self._fetch_results_async(snapshot_id)

    def posts_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch TikTok posts results (sync)."""
        return asyncio.run(self.posts_fetch(snapshot_id))

    # ============================================================================
    # COMMENTS - Collect by URL
    # ============================================================================

    async def comments(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect TikTok comments from video URL(s) (async).

        Args:
            url: Video URL(s) to collect comments from
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with comments

        Example:
            >>> result = await scraper.comments(
            ...     url="https://www.tiktok.com/@user/video/7216019547806092550"
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        is_single = isinstance(url, str)
        url_list = [url] if is_single else url
        payload = [{"url": u} for u in url_list]

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_COMMENTS,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]
        return result

    def comments_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect TikTok comments (sync)."""

        async def _run():
            async with self.engine:
                return await self.comments(url, timeout)

        return asyncio.run(_run())

    # --- Comments Trigger/Status/Fetch ---

    async def comments_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger TikTok comments collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u} for u in url_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_COMMENTS
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def comments_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger TikTok comments collection (sync)."""
        return asyncio.run(self.comments_trigger(url))

    async def comments_status(self, snapshot_id: str) -> str:
        """Check TikTok comments collection status."""
        return await self._check_status_async(snapshot_id)

    def comments_status_sync(self, snapshot_id: str) -> str:
        """Check TikTok comments collection status (sync)."""
        return asyncio.run(self.comments_status(snapshot_id))

    async def comments_fetch(self, snapshot_id: str) -> Any:
        """Fetch TikTok comments results."""
        return await self._fetch_results_async(snapshot_id)

    def comments_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch TikTok comments results (sync)."""
        return asyncio.run(self.comments_fetch(snapshot_id))

    # ============================================================================
    # FAST API - Posts by Profile
    # ============================================================================

    async def posts_by_profile_fast(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect TikTok posts from profile using Fast API (async).

        Faster response times compared to discovery endpoints.

        Args:
            url: Profile URL(s) like https://www.tiktok.com/@username
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with posts

        Example:
            >>> result = await scraper.posts_by_profile_fast(
            ...     url="https://www.tiktok.com/@bbc"
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_POSTS_BY_PROFILE_FAST,
            timeout=timeout,
        )

    def posts_by_profile_fast_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect TikTok posts from profile using Fast API (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_profile_fast(url, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # FAST API - Posts by URL (discover/channel/music/explore pages)
    # ============================================================================

    async def posts_by_url_fast(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect TikTok posts from various URLs using Fast API (async).

        Supports discover, channel, music, and explore pages.

        Args:
            url: TikTok URL(s) - discover, channel, music, or explore pages
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with posts

        Example:
            >>> result = await scraper.posts_by_url_fast(
            ...     url=[
            ...         "https://www.tiktok.com/discover/dog",
            ...         "https://www.tiktok.com/channel/anime",
            ...         "https://www.tiktok.com/explore?lang=en"
            ...     ]
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        is_single = isinstance(url, str)
        url_list = [url] if is_single else url
        # This endpoint does not accept country field
        payload = [{"url": u} for u in url_list]

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS_BY_URL_FAST,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]
        return result

    def posts_by_url_fast_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect TikTok posts by URL using Fast API (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_url_fast(url, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # FAST API - Posts by Search URL
    # ============================================================================

    async def posts_by_search_url_fast(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[Union[int, List[int]]] = None,
        country: Optional[Union[str, List[str]]] = None,
        start_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Collect TikTok posts from search URL using Fast API (async).

        Args:
            url: TikTok search URL(s)
            num_of_posts: Number of posts to collect per URL
            country: Country code(s) for request context
            start_date: Start date filter (MM-DD-YYYY format)
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult with posts from search

        Example:
            >>> result = await scraper.posts_by_search_url_fast(
            ...     url="https://www.tiktok.com/search?q=cats",
            ...     num_of_posts=10
            ... )
        """
        urls = [url] if isinstance(url, str) else url
        batch_size = len(urls)
        nums = self._normalize_param(num_of_posts, batch_size, None)
        countries = self._normalize_param(country, batch_size, "")

        payload = []
        for i in range(batch_size):
            item: Dict[str, Any] = {"url": urls[i], "country": countries[i]}
            if nums[i] is not None:
                item["num_of_posts"] = nums[i]
            if start_date:
                item["start_date"] = start_date
            payload.append(item)

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS_BY_SEARCH_URL_FAST,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
        )
        return result

    def posts_by_search_url_fast_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[Union[int, List[int]]] = None,
        country: Optional[Union[str, List[str]]] = None,
        start_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Collect TikTok posts from search URL using Fast API (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_search_url_fast(
                    url, num_of_posts, country, start_date, timeout
                )

        return asyncio.run(_run())

    # ============================================================================
    # CORE SCRAPING LOGIC
    # ============================================================================

    async def _scrape_urls(
        self,
        url: Union[str, List[str]],
        dataset_id: str,
        timeout: int,
        country: Optional[str] = None,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape URLs using standard async workflow."""
        is_single = isinstance(url, str)
        url_list = [url] if is_single else url

        payload = [{"url": u, "country": country or ""} for u in url_list]

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

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]
            return result
        elif not is_single and isinstance(result.data, list):
            from ...models import ScrapeResult as SR

            results = []
            for url_item, data_item in zip(url_list, result.data):
                results.append(
                    SR(
                        success=True,
                        data=data_item,
                        url=url_item,
                        platform=result.platform,
                        method=result.method,
                        trigger_sent_at=result.trigger_sent_at,
                        snapshot_id_received_at=result.snapshot_id_received_at,
                        snapshot_polled_at=result.snapshot_polled_at,
                        data_fetched_at=result.data_fetched_at,
                        snapshot_id=result.snapshot_id,
                        cost=result.cost / len(result.data) if result.cost else None,
                    )
                )
            return results
        return result

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

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
