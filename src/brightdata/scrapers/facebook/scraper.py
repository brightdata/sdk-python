"""
Facebook Scraper - URL-based extraction for posts, comments, and reels.

This module contains the FacebookScraper class which provides URL-based extraction
for Facebook posts, comments, and reels. All methods use the standard async workflow
(trigger/poll/fetch).

API Specifications:
- client.scrape.facebook.posts_by_profile(url, num_of_posts=None, start_date=None, end_date=None, timeout=240)
- client.scrape.facebook.posts_by_group(url, num_of_posts=None, start_date=None, end_date=None, timeout=240)
- client.scrape.facebook.posts_by_url(url, timeout=240)
- client.scrape.facebook.comments(url, num_of_comments=None, start_date=None, end_date=None, timeout=240)
- client.scrape.facebook.reels(url, num_of_posts=None, start_date=None, end_date=None, timeout=240)

All methods accept:
- url: str | list (required) - Single URL or list of URLs
- timeout: int (default: 240) - Maximum wait time in seconds for polling
- Additional parameters vary by method (see method docstrings)
"""

import asyncio
from typing import Union, List, Optional, Dict, Any

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, COST_PER_RECORD_FACEBOOK


@register("facebook")
class FacebookScraper(BaseWebScraper):
    """
    Facebook scraper for URL-based extraction.

    Extracts structured data from Facebook URLs for:
    - Posts (by profile, group, or post URL)
    - Comments (by post URL)
    - Reels (by profile URL)

    Example:
        >>> scraper = FacebookScraper(bearer_token="token")
        >>>
        >>> # Async usage
        >>> result = await scraper.posts_by_profile(
        ...     url="https://facebook.com/profile",
        ...     num_of_posts=10,
        ...     timeout=240
        ... )
        >>>
        >>> # Sync usage
        >>> result = scraper.posts_by_profile_sync(
        ...     url="https://facebook.com/profile",
        ...     num_of_posts=10,
        ...     timeout=240
        ... )
    """

    # Facebook dataset IDs
    DATASET_ID = "gd_lkaxegm826bjpoo9m5"  # Default: Posts by Profile URL
    DATASET_ID_POSTS_PROFILE = "gd_lkaxegm826bjpoo9m5"  # Posts by Profile URL
    DATASET_ID_POSTS_GROUP = "gd_lz11l67o2cb3r0lkj3"  # Posts by Group URL
    DATASET_ID_POSTS_URL = "gd_lyclm1571iy3mv57zw"  # Posts by Post URL
    DATASET_ID_COMMENTS = "gd_lkay758p1eanlolqw8"  # Comments by Post URL
    DATASET_ID_REELS = "gd_lyclm3ey2q6rww027t"  # Reels by Profile URL

    PLATFORM_NAME = "facebook"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = COST_PER_RECORD_FACEBOOK

    # ============================================================================
    # POSTS API - By Profile URL
    # ============================================================================

    async def posts_by_profile(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect posts from Facebook profile URL (async).

        Collects detailed post data from Facebook profiles including post details,
        page/profile details, and attachments/media.

        Args:
            url: Facebook profile URL or list of URLs (required)
            num_of_posts: Number of recent posts to collect (optional, no limit if omitted)
            posts_to_not_include: Array of post IDs to exclude from results
            start_date: Start date for filtering posts in MM-DD-YYYY format
            end_date: End date for filtering posts in MM-DD-YYYY format
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with post data

        Example:
            >>> result = await scraper.posts_by_profile(
            ...     url="https://facebook.com/profile",
            ...     num_of_posts=10,
            ...     start_date="01-01-2025",
            ...     end_date="12-31-2025",
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_with_params(
            url=url,
            dataset_id=self.DATASET_ID_POSTS_PROFILE,
            num_of_posts=num_of_posts,
            posts_to_not_include=posts_to_not_include,
            start_date=start_date,
            end_date=end_date,
            timeout=timeout,
            sdk_function="posts_by_profile",
        )

    def posts_by_profile_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect posts from Facebook profile URL (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_profile(
                    url, num_of_posts, posts_to_not_include, start_date, end_date, timeout
                )

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def posts_by_profile_trigger(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> "ScrapeJob":
        """Trigger Facebook posts by profile scrape (async - manual control)."""
        from ..job import ScrapeJob

        get_caller_function_name()

        url_list = [url] if isinstance(url, str) else url
        payload = []
        for u in url_list:
            item = {"url": u}
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if posts_to_not_include:
                item["posts_to_not_include"] = posts_to_not_include
            if start_date:
                item["start_date"] = start_date
            if end_date:
                item["end_date"] = end_date
            payload.append(item)

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_POSTS_PROFILE
        )

        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def posts_by_profile_trigger_sync(self, url: Union[str, List[str]], **kwargs) -> "ScrapeJob":
        """Trigger Facebook posts by profile scrape (sync wrapper)."""
        return asyncio.run(self.posts_by_profile_trigger(url, **kwargs))

    async def posts_by_profile_status(self, snapshot_id: str) -> str:
        """Check Facebook posts by profile status (async)."""
        return await self._check_status_async(snapshot_id)

    def posts_by_profile_status_sync(self, snapshot_id: str) -> str:
        """Check Facebook posts by profile status (sync wrapper)."""
        return asyncio.run(self.posts_by_profile_status(snapshot_id))

    async def posts_by_profile_fetch(self, snapshot_id: str) -> Any:
        """Fetch Facebook posts by profile results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def posts_by_profile_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Facebook posts by profile results (sync wrapper)."""
        return asyncio.run(self.posts_by_profile_fetch(snapshot_id))

    # ============================================================================
    # POSTS API - By Group URL
    # ============================================================================

    async def posts_by_group(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect posts from Facebook group URL (async).

        Collects detailed posts from Facebook groups including post details,
        group details, user details, and attachments/external links.

        Args:
            url: Facebook group URL or list of URLs (required)
            num_of_posts: Number of posts to collect (optional, no limit if omitted)
            posts_to_not_include: Array of post IDs to exclude from results
            start_date: Start date for filtering posts in MM-DD-YYYY format
            end_date: End date for filtering posts in MM-DD-YYYY format
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with post data

        Example:
            >>> result = await scraper.posts_by_group(
            ...     url="https://facebook.com/groups/example",
            ...     num_of_posts=20,
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_with_params(
            url=url,
            dataset_id=self.DATASET_ID_POSTS_GROUP,
            num_of_posts=num_of_posts,
            posts_to_not_include=posts_to_not_include,
            start_date=start_date,
            end_date=end_date,
            timeout=timeout,
            sdk_function="posts_by_group",
        )

    def posts_by_group_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect posts from Facebook group URL (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_group(
                    url, num_of_posts, posts_to_not_include, start_date, end_date, timeout
                )

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def posts_by_group_trigger(
        self, url: Union[str, List[str]], **kwargs
    ) -> "ScrapeJob":
        """Trigger Facebook posts by group scrape (async - manual control)."""
        from ..job import ScrapeJob

        get_caller_function_name()
        url_list = [url] if isinstance(url, str) else url
        payload = [
            {"url": u, **{k: v for k, v in kwargs.items() if v is not None}} for u in url_list
        ]
        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_POSTS_GROUP
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def posts_by_group_trigger_sync(self, url: Union[str, List[str]], **kwargs) -> "ScrapeJob":
        """Trigger Facebook posts by group scrape (sync wrapper)."""
        return asyncio.run(self.posts_by_group_trigger(url, **kwargs))

    async def posts_by_group_status(self, snapshot_id: str) -> str:
        """Check Facebook posts by group status (async)."""
        return await self._check_status_async(snapshot_id)

    def posts_by_group_status_sync(self, snapshot_id: str) -> str:
        """Check Facebook posts by group status (sync wrapper)."""
        return asyncio.run(self.posts_by_group_status(snapshot_id))

    async def posts_by_group_fetch(self, snapshot_id: str) -> Any:
        """Fetch Facebook posts by group results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def posts_by_group_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Facebook posts by group results (sync wrapper)."""
        return asyncio.run(self.posts_by_group_fetch(snapshot_id))

    # ============================================================================
    # POSTS API - By Post URL
    # ============================================================================

    async def posts_by_url(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect detailed data from specific Facebook post URLs (async).

        Collects comprehensive data from specific Facebook posts including post details,
        page/profile details, and attachments/media.

        Args:
            url: Facebook post URL or list of URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with post data

        Example:
            >>> result = await scraper.posts_by_url(
            ...     url="https://facebook.com/post/123456",
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_POSTS_URL,
            timeout=timeout,
            sdk_function="posts_by_url",
        )

    def posts_by_url_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect detailed data from specific Facebook post URLs (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_url(url, timeout)

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def posts_by_url_trigger(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Facebook posts by URL scrape (async - manual control)."""

        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_POSTS_URL,
            sdk_function=sdk_function or "posts_by_url_trigger",
        )

    def posts_by_url_trigger_sync(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Facebook posts by URL scrape (sync wrapper)."""
        return asyncio.run(self.posts_by_url_trigger(url))

    async def posts_by_url_status(self, snapshot_id: str) -> str:
        """Check Facebook posts by URL status (async)."""
        return await self._check_status_async(snapshot_id)

    def posts_by_url_status_sync(self, snapshot_id: str) -> str:
        """Check Facebook posts by URL status (sync wrapper)."""
        return asyncio.run(self.posts_by_url_status(snapshot_id))

    async def posts_by_url_fetch(self, snapshot_id: str) -> Any:
        """Fetch Facebook posts by URL results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def posts_by_url_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Facebook posts by URL results (sync wrapper)."""
        return asyncio.run(self.posts_by_url_fetch(snapshot_id))

    # ============================================================================
    # COMMENTS API - By Post URL
    # ============================================================================

    async def comments(
        self,
        url: Union[str, List[str]],
        num_of_comments: Optional[int] = None,
        comments_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect comments from Facebook post URL (async).

        Collects detailed comment data from Facebook posts including comment details,
        user details, post metadata, and attachments/media.

        Args:
            url: Facebook post URL or list of URLs (required)
            num_of_comments: Number of comments to collect (optional, no limit if omitted)
            comments_to_not_include: Array of comment IDs to exclude
            start_date: Start date for filtering comments in MM-DD-YYYY format
            end_date: End date for filtering comments in MM-DD-YYYY format
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with comment data

        Example:
            >>> result = await scraper.comments(
            ...     url="https://facebook.com/post/123456",
            ...     num_of_comments=100,
            ...     start_date="01-01-2025",
            ...     end_date="12-31-2025",
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_with_params(
            url=url,
            dataset_id=self.DATASET_ID_COMMENTS,
            num_of_comments=num_of_comments,
            comments_to_not_include=comments_to_not_include,
            start_date=start_date,
            end_date=end_date,
            timeout=timeout,
            sdk_function="comments",
        )

    def comments_sync(
        self,
        url: Union[str, List[str]],
        num_of_comments: Optional[int] = None,
        comments_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect comments from Facebook post URL (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.comments(
                    url, num_of_comments, comments_to_not_include, start_date, end_date, timeout
                )

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def comments_trigger(self, url: Union[str, List[str]], **kwargs) -> "ScrapeJob":
        """Trigger Facebook comments scrape (async - manual control)."""
        from ..job import ScrapeJob

        get_caller_function_name()
        url_list = [url] if isinstance(url, str) else url
        payload = [
            {"url": u, **{k: v for k, v in kwargs.items() if v is not None}} for u in url_list
        ]
        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_COMMENTS
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def comments_trigger_sync(self, url: Union[str, List[str]], **kwargs) -> "ScrapeJob":
        """Trigger Facebook comments scrape (sync wrapper)."""
        return asyncio.run(self.comments_trigger(url, **kwargs))

    async def comments_status(self, snapshot_id: str) -> str:
        """Check Facebook comments status (async)."""
        return await self._check_status_async(snapshot_id)

    def comments_status_sync(self, snapshot_id: str) -> str:
        """Check Facebook comments status (sync wrapper)."""
        return asyncio.run(self.comments_status(snapshot_id))

    async def comments_fetch(self, snapshot_id: str) -> Any:
        """Fetch Facebook comments results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def comments_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Facebook comments results (sync wrapper)."""
        return asyncio.run(self.comments_fetch(snapshot_id))

    # ============================================================================
    # REELS API - By Profile URL
    # ============================================================================

    async def reels(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect reels from Facebook profile URL (async).

        Collects detailed data about Facebook reels from public profiles including
        reel details, page/profile details, and attachments/media.

        Args:
            url: Facebook profile URL or list of URLs (required)
            num_of_posts: Number of reels to collect (default: up to 1600)
            posts_to_not_include: Array of reel IDs to exclude
            start_date: Start of the date range for filtering reels
            end_date: End of the date range for filtering reels
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with reel data

        Example:
            >>> result = await scraper.reels(
            ...     url="https://facebook.com/profile",
            ...     num_of_posts=50,
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_with_params(
            url=url,
            dataset_id=self.DATASET_ID_REELS,
            num_of_posts=num_of_posts,
            posts_to_not_include=posts_to_not_include,
            start_date=start_date,
            end_date=end_date,
            timeout=timeout,
            sdk_function="reels",
        )

    def reels_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect reels from Facebook profile URL (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.reels(
                    url, num_of_posts, posts_to_not_include, start_date, end_date, timeout
                )

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def reels_trigger(self, url: Union[str, List[str]], **kwargs) -> "ScrapeJob":
        """Trigger Facebook reels scrape (async - manual control)."""
        from ..job import ScrapeJob

        get_caller_function_name()
        url_list = [url] if isinstance(url, str) else url
        payload = [
            {"url": u, **{k: v for k, v in kwargs.items() if v is not None}} for u in url_list
        ]
        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_REELS
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def reels_trigger_sync(self, url: Union[str, List[str]], **kwargs) -> "ScrapeJob":
        """Trigger Facebook reels scrape (sync wrapper)."""
        return asyncio.run(self.reels_trigger(url, **kwargs))

    async def reels_status(self, snapshot_id: str) -> str:
        """Check Facebook reels status (async)."""
        return await self._check_status_async(snapshot_id)

    def reels_status_sync(self, snapshot_id: str) -> str:
        """Check Facebook reels status (sync wrapper)."""
        return asyncio.run(self.reels_status(snapshot_id))

    async def reels_fetch(self, snapshot_id: str) -> Any:
        """Fetch Facebook reels results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def reels_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Facebook reels results (sync wrapper)."""
        return asyncio.run(self.reels_fetch(snapshot_id))

    # ============================================================================
    # CORE SCRAPING LOGIC
    # ============================================================================

    async def _scrape_urls(
        self,
        url: Union[str, List[str]],
        dataset_id: str,
        timeout: int,
        sdk_function: Optional[str] = None,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape URLs using standard async workflow (trigger/poll/fetch).

        Args:
            url: URL(s) to scrape
            dataset_id: Facebook dataset ID
            timeout: Maximum wait time in seconds (for polling)
            sdk_function: SDK function name for monitoring (auto-detected if not provided)

        Returns:
            ScrapeResult(s)
        """
        if sdk_function is None:
            sdk_function = get_caller_function_name()

        is_single = isinstance(url, str)
        url_list = [url] if is_single else url

        payload = [{"url": u} for u in url_list]

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=dataset_id,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            normalize_func=self.normalize_result,
            sdk_function=sdk_function,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]
            return result
        elif not is_single and isinstance(result.data, list):
            from ...models import ScrapeResult

            results = []
            for url_item, data_item in zip(url_list, result.data):
                results.append(
                    ScrapeResult(
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

    async def _scrape_with_params(
        self,
        url: Union[str, List[str]],
        dataset_id: str,
        num_of_posts: Optional[int] = None,
        num_of_comments: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        comments_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
        sdk_function: Optional[str] = None,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Scrape URLs with additional parameters using standard async workflow.

        Args:
            url: URL(s) to scrape
            dataset_id: Facebook dataset ID
            num_of_posts: Number of posts to collect (for posts/reels)
            num_of_comments: Number of comments to collect (for comments)
            posts_to_not_include: Post IDs to exclude
            comments_to_not_include: Comment IDs to exclude
            start_date: Start date filter (MM-DD-YYYY)
            end_date: End date filter (MM-DD-YYYY)
            timeout: Maximum wait time in seconds

        Returns:
            ScrapeResult(s)
        """
        is_single = isinstance(url, str)
        url_list = [url] if is_single else url

        payload = []
        for u in url_list:
            item: Dict[str, Any] = {"url": u}

            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if num_of_comments is not None:
                item["num_of_comments"] = num_of_comments
            if posts_to_not_include:
                item["posts_to_not_include"] = posts_to_not_include
            if comments_to_not_include:
                item["comments_to_not_include"] = comments_to_not_include
            if start_date:
                item["start_date"] = start_date
            if end_date:
                item["end_date"] = end_date

            payload.append(item)

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=dataset_id,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            normalize_func=self.normalize_result,
            sdk_function=sdk_function or "posts_by_profile",
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]
            return result
        elif not is_single and isinstance(result.data, list):
            from ...models import ScrapeResult

            results = []
            url_list = url if isinstance(url, list) else [url]
            for url_item, data_item in zip(url_list, result.data):
                results.append(
                    ScrapeResult(
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
