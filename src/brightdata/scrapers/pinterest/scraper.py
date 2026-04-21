"""
Pinterest scraper - URL-based collection for posts and profiles.

Supports:
- Posts: collect by URL
- Profiles: collect by URL

For discovery/search operations, see search.py which contains PinterestSearchScraper.

API Specifications:
- client.scrape.pinterest.posts(url, ...)                    # async
- client.scrape.pinterest.posts_sync(url, ...)               # sync
- client.scrape.pinterest.profiles(url, ...)                 # async
- client.scrape.pinterest.profiles_sync(url, ...)            # sync
"""

import asyncio
from typing import List, Any, Union

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, DEFAULT_COST_PER_RECORD


@register("pinterest")
class PinterestScraper(BaseWebScraper):
    """
    Pinterest scraper for URL-based collection.

    Extracts structured data from Pinterest URLs for:
    - Posts (pins)
    - Profiles

    For discovery operations (by keyword, profile URL), use PinterestSearchScraper.

    Example:
        >>> scraper = PinterestScraper(bearer_token="token")
        >>>
        >>> # Collect post data
        >>> result = await scraper.posts(
        ...     url="https://www.pinterest.com/pin/3166662230556591/"
        ... )
        >>>
        >>> # Collect profile data
        >>> result = await scraper.profiles(
        ...     url="https://www.pinterest.com/boredpanda/"
        ... )
    """

    # Dataset IDs
    DATASET_ID = "gd_lk0sjs4d21kdr7cnlv"  # Posts (default)
    DATASET_ID_POSTS = "gd_lk0sjs4d21kdr7cnlv"
    DATASET_ID_PROFILES = "gd_lk0zv93c2m9qdph46z"

    PLATFORM_NAME = "pinterest"
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
        Collect Pinterest post (pin) data by URL (async).

        Args:
            url: Pin URL(s) like https://www.pinterest.com/pin/3166662230556591/
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with post data

        Example:
            >>> result = await scraper.posts(
            ...     url="https://www.pinterest.com/pin/3166662230556591/"
            ... )
            >>> print(result.data)
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_POSTS,
            timeout=timeout,
        )

    def posts_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect Pinterest post data by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts(url, timeout)

        return asyncio.run(_run())

    # --- Posts Trigger/Status/Fetch ---

    async def posts_trigger(
        self,
        url: Union[str, List[str]],
    ) -> ScrapeJob:
        """Trigger Pinterest posts collection (manual control)."""
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
        """Trigger Pinterest posts collection (sync)."""
        return asyncio.run(self.posts_trigger(url))

    async def posts_status(self, snapshot_id: str) -> str:
        """Check Pinterest posts collection status."""
        return await self._check_status_async(snapshot_id)

    def posts_status_sync(self, snapshot_id: str) -> str:
        """Check Pinterest posts collection status (sync)."""
        return asyncio.run(self.posts_status(snapshot_id))

    async def posts_fetch(self, snapshot_id: str) -> Any:
        """Fetch Pinterest posts results."""
        return await self._fetch_results_async(snapshot_id)

    def posts_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Pinterest posts results (sync)."""
        return asyncio.run(self.posts_fetch(snapshot_id))

    # ============================================================================
    # PROFILES - Collect by URL
    # ============================================================================

    async def profiles(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect Pinterest profile data by URL (async).

        Args:
            url: Profile URL(s) like https://www.pinterest.com/boredpanda/
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with profile data

        Example:
            >>> result = await scraper.profiles(
            ...     url="https://www.pinterest.com/boredpanda/"
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
        )

    def profiles_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect Pinterest profile data by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.profiles(url, timeout)

        return asyncio.run(_run())

    # --- Profiles Trigger/Status/Fetch ---

    async def profiles_trigger(
        self,
        url: Union[str, List[str]],
    ) -> ScrapeJob:
        """Trigger Pinterest profiles collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u} for u in url_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_PROFILES
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def profiles_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger Pinterest profiles collection (sync)."""
        return asyncio.run(self.profiles_trigger(url))

    async def profiles_status(self, snapshot_id: str) -> str:
        """Check Pinterest profiles collection status."""
        return await self._check_status_async(snapshot_id)

    def profiles_status_sync(self, snapshot_id: str) -> str:
        """Check Pinterest profiles collection status (sync)."""
        return asyncio.run(self.profiles_status(snapshot_id))

    async def profiles_fetch(self, snapshot_id: str) -> Any:
        """Fetch Pinterest profiles results."""
        return await self._fetch_results_async(snapshot_id)

    def profiles_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Pinterest profiles results (sync)."""
        return asyncio.run(self.profiles_fetch(snapshot_id))

    # ============================================================================
    # CORE SCRAPING LOGIC
    # ============================================================================

    async def _scrape_urls(
        self,
        url: Union[str, List[str]],
        dataset_id: str,
        timeout: int,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape URLs using standard async workflow."""
        is_single = isinstance(url, str)
        url_list = [url] if is_single else url

        payload = [{"url": u} for u in url_list]

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
