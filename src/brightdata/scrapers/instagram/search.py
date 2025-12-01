"""
Instagram Search Scraper - Discovery/parameter-based operations.

Implements:
- client.search.instagram.posts() - Discover posts by profile URL with filters
- client.search.instagram.reels() - Discover reels by profile or search URL with filters
"""

import asyncio
from typing import Union, List, Optional, Dict, Any

from ...core.engine import AsyncEngine
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, COST_PER_RECORD_INSTAGRAM
from ..api_client import DatasetAPIClient
from ..workflow import WorkflowExecutor


class InstagramSearchScraper:
    """
    Instagram Search Scraper for parameter-based discovery.

    Provides discovery methods that search Instagram by parameters
    rather than extracting from specific URLs. This is a parallel component
    to InstagramScraper, both doing Instagram data extraction but with
    different approaches (parameter-based vs URL-based).

    Example:
        >>> scraper = InstagramSearchScraper(bearer_token="token")
        >>> result = scraper.posts(
        ...     url="https://instagram.com/username",
        ...     num_of_posts=10,
        ...     post_type="reel"
        ... )
    """

    # Dataset IDs for discovery endpoints
    DATASET_ID_POSTS_DISCOVER = "gd_lk5ns7kz21pck8jpis"  # Posts discover by URL
    DATASET_ID_REELS_DISCOVER = "gd_lyclm20il4r5helnj"  # Reels discover by URL

    def __init__(self, bearer_token: str, engine: Optional[AsyncEngine] = None):
        """
        Initialize Instagram search scraper.

        Args:
            bearer_token: Bright Data API token
            engine: Optional AsyncEngine instance. If not provided, creates a new one.
                    Allows dependency injection for testing and flexibility.
        """
        self.bearer_token = bearer_token
        self.engine = engine if engine is not None else AsyncEngine(bearer_token)
        self.api_client = DatasetAPIClient(self.engine)
        self.workflow_executor = WorkflowExecutor(
            api_client=self.api_client,
            platform_name="instagram",
            cost_per_record=COST_PER_RECORD_INSTAGRAM,
        )

    # ============================================================================
    # POSTS DISCOVERY (by profile URL with filters)
    # ============================================================================

    async def posts_async(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        post_type: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Discover recent Instagram posts from a public profile (async).

        Discovers posts from Instagram profiles, reels, or search URLs with
        filtering options by date range, exclusion of specific posts, and post type.

        Args:
            url: Instagram profile, reel, or search URL (required)
            num_of_posts: Number of recent posts to collect (optional, no limit if omitted)
            posts_to_not_include: Array of post IDs to exclude from results
            start_date: Start date for filtering posts in MM-DD-YYYY format
            end_date: End date for filtering posts in MM-DD-YYYY format
            post_type: Type of posts to collect (e.g., "post", "reel")
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with discovered posts

        Example:
            >>> result = await scraper.posts_async(
            ...     url="https://instagram.com/username",
            ...     num_of_posts=10,
            ...     start_date="01-01-2024",
            ...     end_date="12-31-2024",
            ...     post_type="reel"
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._discover_with_params(
            url=url,
            dataset_id=self.DATASET_ID_POSTS_DISCOVER,
            num_of_posts=num_of_posts,
            posts_to_not_include=posts_to_not_include,
            start_date=start_date,
            end_date=end_date,
            post_type=post_type,
            timeout=timeout,
        )

    def posts(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        post_type: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Discover recent Instagram posts from a public profile (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.posts_async(
                    url,
                    num_of_posts,
                    posts_to_not_include,
                    start_date,
                    end_date,
                    post_type,
                    timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # REELS DISCOVERY (by profile or search URL with filters)
    # ============================================================================

    async def reels_async(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Discover Instagram Reels from profile or search URL (async).

        Discovers Instagram Reels videos from a profile URL or direct search URL
        with filtering options by date range and exclusion of specific posts.

        Args:
            url: Instagram profile or direct search URL (required)
            num_of_posts: Number of recent reels to collect (optional, no limit if omitted)
            posts_to_not_include: Array of post IDs to exclude from results
            start_date: Start date for filtering reels in MM-DD-YYYY format
            end_date: End date for filtering reels in MM-DD-YYYY format
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with discovered reels

        Example:
            >>> result = await scraper.reels_async(
            ...     url="https://instagram.com/username",
            ...     num_of_posts=50,
            ...     start_date="01-01-2024",
            ...     end_date="12-31-2024",
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._discover_with_params(
            url=url,
            dataset_id=self.DATASET_ID_REELS_DISCOVER,
            num_of_posts=num_of_posts,
            posts_to_not_include=posts_to_not_include,
            start_date=start_date,
            end_date=end_date,
            timeout=timeout,
            sdk_function="reels",
        )

    def reels(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Discover Instagram Reels from profile or search URL (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.reels_async(
                    url, num_of_posts, posts_to_not_include, start_date, end_date, timeout
                )

        return asyncio.run(_run())

    # ============================================================================
    # CORE DISCOVERY LOGIC
    # ============================================================================

    async def _discover_with_params(
        self,
        url: Union[str, List[str]],
        dataset_id: str,
        num_of_posts: Optional[int] = None,
        posts_to_not_include: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        post_type: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
        sdk_function: Optional[str] = None,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Discover content with additional parameters using standard async workflow.

        Args:
            url: URL(s) to discover from
            dataset_id: Instagram dataset ID
            num_of_posts: Number of posts to collect
            posts_to_not_include: Post IDs to exclude
            start_date: Start date filter (MM-DD-YYYY)
            end_date: End date filter (MM-DD-YYYY)
            post_type: Type of posts to collect (for posts discovery only)
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
            if posts_to_not_include:
                item["posts_to_not_include"] = posts_to_not_include
            if start_date:
                item["start_date"] = start_date
            if end_date:
                item["end_date"] = end_date
            if post_type:
                item["post_type"] = post_type

            payload.append(item)

        if sdk_function is None:
            sdk_function = get_caller_function_name()

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=dataset_id,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            normalize_func=None,
            sdk_function=sdk_function,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]

        return result
