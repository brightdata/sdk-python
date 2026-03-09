"""
Reddit scraper - URL-based collection and discovery for posts and comments.

Supports:
- Posts: collect by URL
- Posts: discover by keyword
- Posts: discover by subreddit URL
- Comments: collect by URL

API Specifications:
- client.scrape.reddit.posts(url, ...)                         # async
- client.scrape.reddit.posts_sync(url, ...)                    # sync
- client.scrape.reddit.posts_by_keyword(keyword, ...)          # async
- client.scrape.reddit.posts_by_keyword_sync(keyword, ...)     # sync
- client.scrape.reddit.posts_by_subreddit(url, ...)            # async
- client.scrape.reddit.posts_by_subreddit_sync(url, ...)       # sync
- client.scrape.reddit.comments(url, ...)                      # async
- client.scrape.reddit.comments_sync(url, ...)                 # sync
"""

import asyncio
from typing import List, Any, Optional, Union, Dict

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, DEFAULT_COST_PER_RECORD


@register("reddit")
class RedditScraper(BaseWebScraper):
    """
    Reddit scraper for posts and comments.

    Extracts structured data from Reddit for:
    - Posts (collect by URL)
    - Posts (discover by keyword search)
    - Posts (discover by subreddit URL)
    - Comments (collect by URL)

    Example:
        >>> scraper = RedditScraper(bearer_token="token")
        >>>
        >>> # Collect post data
        >>> result = await scraper.posts(
        ...     url="https://www.reddit.com/r/python/comments/abc123/..."
        ... )
        >>>
        >>> # Discover posts by keyword
        >>> result = await scraper.posts_by_keyword(
        ...     keyword="machine learning",
        ...     sort_by="Top"
        ... )
        >>>
        >>> # Discover posts from subreddit
        >>> result = await scraper.posts_by_subreddit(
        ...     url="https://www.reddit.com/r/datascience/",
        ...     sort_by="Hot"
        ... )
        >>>
        >>> # Collect comments
        >>> result = await scraper.comments(
        ...     url="https://www.reddit.com/r/python/comments/abc123/comment/xyz789/",
        ...     days_back=30
        ... )
    """

    # Dataset IDs
    DATASET_ID = "gd_lvz8ah06191smkebj4"  # Posts (default)
    DATASET_ID_POSTS = "gd_lvz8ah06191smkebj4"
    DATASET_ID_COMMENTS = "gd_lvzdpsdlw09j6t702"

    PLATFORM_NAME = "reddit"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = DEFAULT_COST_PER_RECORD

    # ============================================================================
    # POSTS - Collect by URL
    # ============================================================================

    async def posts(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect Reddit post data by URL (async).

        Args:
            url: Post URL(s) like https://www.reddit.com/r/subreddit/comments/...
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with post data

        Example:
            >>> result = await scraper.posts(
            ...     url="https://www.reddit.com/r/python/comments/abc123/my_post/"
            ... )
            >>> print(result.data)
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
            dataset_id=self.DATASET_ID_POSTS,
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

    def posts_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect Reddit post data by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts(url, timeout)

        return asyncio.run(_run())

    # --- Posts Trigger/Status/Fetch ---

    async def posts_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger Reddit posts collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u} for u in url_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_POSTS
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def posts_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger Reddit posts collection (sync)."""
        return asyncio.run(self.posts_trigger(url))

    async def posts_status(self, snapshot_id: str) -> str:
        """Check Reddit posts collection status."""
        return await self._check_status_async(snapshot_id)

    def posts_status_sync(self, snapshot_id: str) -> str:
        """Check Reddit posts collection status (sync)."""
        return asyncio.run(self.posts_status(snapshot_id))

    async def posts_fetch(self, snapshot_id: str) -> Any:
        """Fetch Reddit posts results."""
        return await self._fetch_results_async(snapshot_id)

    def posts_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Reddit posts results (sync)."""
        return asyncio.run(self.posts_fetch(snapshot_id))

    # ============================================================================
    # POSTS - Discover by Keyword
    # ============================================================================

    async def posts_by_keyword(
        self,
        keyword: Union[str, List[str]],
        date: Optional[Union[str, List[str]]] = None,
        num_of_posts: Optional[Union[int, List[int]]] = None,
        sort_by: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover Reddit posts by keyword search (async).

        Args:
            keyword: Search keyword(s)
            date: Time filter - "All time", "Past year", "Past month", "Past week",
                  "Past 24 hours", "Past hour" (optional)
            num_of_posts: Maximum number of posts to collect (optional)
            sort_by: Sort order - "Hot", "Top", "New", "Rising" (optional)
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult with discovered posts

        Example:
            >>> result = await scraper.posts_by_keyword(
            ...     keyword="machine learning",
            ...     date="Past week",
            ...     sort_by="Top",
            ...     num_of_posts=50
            ... )
        """
        keywords = [keyword] if isinstance(keyword, str) else keyword
        batch_size = len(keywords)
        dates = self._normalize_param(date, batch_size, None)
        nums = self._normalize_param(num_of_posts, batch_size, None)
        sorts = self._normalize_param(sort_by, batch_size, None)

        payload = []
        for i in range(batch_size):
            item: Dict[str, Any] = {"keyword": keywords[i]}
            if dates[i] is not None:
                item["date"] = dates[i]
            if nums[i] is not None:
                item["num_of_posts"] = nums[i]
            if sorts[i] is not None:
                item["sort_by"] = sorts[i]
            payload.append(item)

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
            extra_params={"type": "discover_new", "discover_by": "keyword"},
        )
        return result

    def posts_by_keyword_sync(
        self,
        keyword: Union[str, List[str]],
        date: Optional[Union[str, List[str]]] = None,
        num_of_posts: Optional[Union[int, List[int]]] = None,
        sort_by: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Discover Reddit posts by keyword search (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_keyword(keyword, date, num_of_posts, sort_by, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # POSTS - Discover by Subreddit URL
    # ============================================================================

    async def posts_by_subreddit(
        self,
        url: Union[str, List[str]],
        sort_by: Optional[Union[str, List[str]]] = None,
        sort_by_time: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover Reddit posts from subreddit URL (async).

        Args:
            url: Subreddit URL(s) like https://www.reddit.com/r/datascience/
            sort_by: Sort order - "Hot", "New", "Rising", "Top" (optional)
            sort_by_time: Time filter for sort - "Today", "Past week",
                          "Past month", "Past year", "All Time" (optional)
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult with discovered posts

        Example:
            >>> result = await scraper.posts_by_subreddit(
            ...     url="https://www.reddit.com/r/datascience/",
            ...     sort_by="Rising",
            ...     sort_by_time="All Time"
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        urls = [url] if isinstance(url, str) else url
        batch_size = len(urls)
        sorts = self._normalize_param(sort_by, batch_size, None)
        sort_times = self._normalize_param(sort_by_time, batch_size, None)

        payload = []
        for i in range(batch_size):
            item: Dict[str, Any] = {"url": urls[i]}
            if sorts[i] is not None:
                item["sort_by"] = sorts[i]
            if sort_times[i] is not None:
                item["sort_by_time"] = sort_times[i]
            payload.append(item)

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
            extra_params={"type": "discover_new", "discover_by": "subreddit_url"},
        )
        return result

    def posts_by_subreddit_sync(
        self,
        url: Union[str, List[str]],
        sort_by: Optional[Union[str, List[str]]] = None,
        sort_by_time: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Discover Reddit posts from subreddit URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_subreddit(url, sort_by, sort_by_time, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # COMMENTS - Collect by URL
    # ============================================================================

    async def comments(
        self,
        url: Union[str, List[str]],
        days_back: Optional[int] = None,
        load_all_replies: Optional[bool] = None,
        comment_limit: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect Reddit comments by URL (async).

        Args:
            url: Comment thread or post URL(s)
            days_back: Number of days to look back (optional)
            load_all_replies: Whether to load all nested replies (optional)
            comment_limit: Maximum number of comments to collect (optional)
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with comment data

        Example:
            >>> result = await scraper.comments(
            ...     url="https://www.reddit.com/r/python/comments/abc123/comment/xyz789/",
            ...     days_back=30,
            ...     load_all_replies=True,
            ...     comment_limit=100
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        is_single = isinstance(url, str)
        url_list = [url] if is_single else url

        payload = []
        for u in url_list:
            item: Dict[str, Any] = {"url": u}
            if days_back is not None:
                item["days_back"] = days_back
            if load_all_replies is not None:
                item["load_all_replies"] = load_all_replies
            if comment_limit is not None:
                item["comment_limit"] = comment_limit
            payload.append(item)

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
        days_back: Optional[int] = None,
        load_all_replies: Optional[bool] = None,
        comment_limit: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect Reddit comments by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.comments(url, days_back, load_all_replies, comment_limit, timeout)

        return asyncio.run(_run())

    # --- Comments Trigger/Status/Fetch ---

    async def comments_trigger(
        self,
        url: Union[str, List[str]],
        days_back: Optional[int] = None,
        load_all_replies: Optional[bool] = None,
        comment_limit: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger Reddit comments collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url

        payload = []
        for u in url_list:
            item: Dict[str, Any] = {"url": u}
            if days_back is not None:
                item["days_back"] = days_back
            if load_all_replies is not None:
                item["load_all_replies"] = load_all_replies
            if comment_limit is not None:
                item["comment_limit"] = comment_limit
            payload.append(item)

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_COMMENTS
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def comments_trigger_sync(
        self,
        url: Union[str, List[str]],
        days_back: Optional[int] = None,
        load_all_replies: Optional[bool] = None,
        comment_limit: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger Reddit comments collection (sync)."""
        return asyncio.run(self.comments_trigger(url, days_back, load_all_replies, comment_limit))

    async def comments_status(self, snapshot_id: str) -> str:
        """Check Reddit comments collection status."""
        return await self._check_status_async(snapshot_id)

    def comments_status_sync(self, snapshot_id: str) -> str:
        """Check Reddit comments collection status (sync)."""
        return asyncio.run(self.comments_status(snapshot_id))

    async def comments_fetch(self, snapshot_id: str) -> Any:
        """Fetch Reddit comments results."""
        return await self._fetch_results_async(snapshot_id)

    def comments_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Reddit comments results (sync)."""
        return asyncio.run(self.comments_fetch(snapshot_id))

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
