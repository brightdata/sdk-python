"""
Instagram Scraper - URL-based extraction for profiles, posts, comments, and reels.

This module contains the InstagramScraper class which provides URL-based extraction
for Instagram profiles, posts, comments, and reels. All methods use the standard
async workflow (trigger/poll/fetch).

API Specifications:
- client.scrape.instagram.profiles(url, timeout=240)
- client.scrape.instagram.posts(url, timeout=240)
- client.scrape.instagram.comments(url, timeout=240)
- client.scrape.instagram.reels(url, timeout=240)

All methods accept:
- url: str | list (required) - Single URL or list of URLs
- timeout: int (default: 240) - Maximum wait time in seconds for polling

For discovery/search operations, see search.py which contains InstagramSearchScraper.
"""

import asyncio
from typing import Union, List, Optional, Any

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, COST_PER_RECORD_INSTAGRAM


@register("instagram")
class InstagramScraper(BaseWebScraper):
    """
    Instagram scraper for URL-based extraction.

    Extracts structured data from Instagram URLs for:
    - Profiles (by profile URL)
    - Posts (by post URL)
    - Comments (by post URL)
    - Reels (by reel URL)

    Example:
        >>> scraper = InstagramScraper(bearer_token="token")
        >>>
        >>> # Async usage
        >>> result = await scraper.profiles(
        ...     url="https://instagram.com/username",
        ...     timeout=240
        ... )
        >>>
        >>> # Sync usage
        >>> result = scraper.profiles_sync(
        ...     url="https://instagram.com/username",
        ...     timeout=240
        ... )
    """

    # Instagram dataset IDs
    DATASET_ID = "gd_l1vikfch901nx3by4"  # Default: Profiles
    DATASET_ID_PROFILES = "gd_l1vikfch901nx3by4"  # Profiles by URL
    DATASET_ID_POSTS = "gd_lk5ns7kz21pck8jpis"  # Posts by URL
    DATASET_ID_COMMENTS = "gd_ltppn085pokosxh13"  # Comments by Post URL
    DATASET_ID_REELS = "gd_lyclm20il4r5helnj"  # Reels by URL

    PLATFORM_NAME = "instagram"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = COST_PER_RECORD_INSTAGRAM

    # ============================================================================
    # PROFILES API - By URL
    # ============================================================================

    async def profiles(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect profile details from Instagram profile URL (async).

        Collects comprehensive data about an Instagram profile including business
        and engagement information, posts, and user details.

        Args:
            url: Instagram profile URL or list of URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with profile data

        Example:
            >>> result = await scraper.profiles(
            ...     url="https://instagram.com/username",
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_PROFILES,
            timeout=timeout,
            sdk_function="profiles",
        )

    def profiles_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect profile details from Instagram profile URL (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.profiles(url, timeout)

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def profiles_trigger(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Instagram profiles scrape (async - manual control)."""

        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_PROFILES,
            sdk_function=sdk_function or "profiles_trigger",
        )

    def profiles_trigger_sync(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Instagram profiles scrape (sync wrapper)."""
        return asyncio.run(self.profiles_trigger(url))

    async def profiles_status(self, snapshot_id: str) -> str:
        """Check Instagram profiles status (async)."""
        return await self._check_status_async(snapshot_id)

    def profiles_status_sync(self, snapshot_id: str) -> str:
        """Check Instagram profiles status (sync wrapper)."""
        return asyncio.run(self.profiles_status(snapshot_id))

    async def profiles_fetch(self, snapshot_id: str) -> Any:
        """Fetch Instagram profiles results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def profiles_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Instagram profiles results (sync wrapper)."""
        return asyncio.run(self.profiles_fetch(snapshot_id))

    # ============================================================================
    # POSTS API - By URL
    # ============================================================================

    async def posts(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect detailed data from Instagram post URLs (async).

        Collects comprehensive data from Instagram posts including post details,
        page/profile details, and attachments/media.

        Args:
            url: Instagram post URL or list of URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with post data

        Example:
            >>> result = await scraper.posts(
            ...     url="https://instagram.com/p/ABC123",
            ...     timeout=240
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
            sdk_function="posts",
        )

    def posts_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect detailed data from Instagram post URLs (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.posts(url, timeout)

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def posts_trigger(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Instagram posts scrape (async - manual control)."""

        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url, dataset_id=self.DATASET_ID_POSTS, sdk_function=sdk_function or "posts_trigger"
        )

    def posts_trigger_sync(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Instagram posts scrape (sync wrapper)."""
        return asyncio.run(self.posts_trigger(url))

    async def posts_status(self, snapshot_id: str) -> str:
        """Check Instagram posts status (async)."""
        return await self._check_status_async(snapshot_id)

    def posts_status_sync(self, snapshot_id: str) -> str:
        """Check Instagram posts status (sync wrapper)."""
        return asyncio.run(self.posts_status(snapshot_id))

    async def posts_fetch(self, snapshot_id: str) -> Any:
        """Fetch Instagram posts results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def posts_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Instagram posts results (sync wrapper)."""
        return asyncio.run(self.posts_fetch(snapshot_id))

    # ============================================================================
    # COMMENTS API - By Post URL
    # ============================================================================

    async def comments(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect comments from Instagram post URL (async).

        Collects the latest comments from a specific Instagram post (up to 10 comments
        with associated metadata).

        Args:
            url: Instagram post URL or list of URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with comment data

        Example:
            >>> result = await scraper.comments(
            ...     url="https://instagram.com/p/ABC123",
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_COMMENTS,
            timeout=timeout,
            sdk_function="comments",
        )

    def comments_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect comments from Instagram post URL (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.comments(url, timeout)

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def comments_trigger(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Instagram comments scrape (async - manual control)."""

        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_COMMENTS,
            sdk_function=sdk_function or "comments_trigger",
        )

    def comments_trigger_sync(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Instagram comments scrape (sync wrapper)."""
        return asyncio.run(self.comments_trigger(url))

    async def comments_status(self, snapshot_id: str) -> str:
        """Check Instagram comments status (async)."""
        return await self._check_status_async(snapshot_id)

    def comments_status_sync(self, snapshot_id: str) -> str:
        """Check Instagram comments status (sync wrapper)."""
        return asyncio.run(self.comments_status(snapshot_id))

    async def comments_fetch(self, snapshot_id: str) -> Any:
        """Fetch Instagram comments results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def comments_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Instagram comments results (sync wrapper)."""
        return asyncio.run(self.comments_fetch(snapshot_id))

    # ============================================================================
    # REELS API - By URL
    # ============================================================================

    async def reels(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect detailed data from Instagram reel URLs (async).

        Collects detailed data about Instagram reels from public profiles including
        reel details, page/profile details, and attachments/media.

        Args:
            url: Instagram reel URL or list of URLs (required)
            timeout: Maximum wait time in seconds for polling (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with reel data

        Example:
            >>> result = await scraper.reels(
            ...     url="https://instagram.com/reel/ABC123",
            ...     timeout=240
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_REELS,
            timeout=timeout,
            sdk_function="reels",
        )

    def reels_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect detailed data from Instagram reel URLs (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.reels(url, timeout)

        return asyncio.run(_run())

    # --- Trigger Interface (Manual Control) ---

    async def reels_trigger(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Instagram reels scrape (async - manual control)."""

        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url, dataset_id=self.DATASET_ID_REELS, sdk_function=sdk_function or "reels_trigger"
        )

    def reels_trigger_sync(self, url: Union[str, List[str]]) -> "ScrapeJob":
        """Trigger Instagram reels scrape (sync wrapper)."""
        return asyncio.run(self.reels_trigger(url))

    async def reels_status(self, snapshot_id: str) -> str:
        """Check Instagram reels status (async)."""
        return await self._check_status_async(snapshot_id)

    def reels_status_sync(self, snapshot_id: str) -> str:
        """Check Instagram reels status (sync wrapper)."""
        return asyncio.run(self.reels_status(snapshot_id))

    async def reels_fetch(self, snapshot_id: str) -> Any:
        """Fetch Instagram reels results (async)."""
        return await self._fetch_results_async(snapshot_id)

    def reels_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Instagram reels results (sync wrapper)."""
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
            dataset_id: Instagram dataset ID
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
