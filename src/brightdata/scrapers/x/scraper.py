"""
X (formerly Twitter) scraper - posts and profiles, collect-by-URL and discovery.

Two datasets back this scraper:
- Posts    (gd_lwxkxvnf1cynvib9co): collect by URL, discover by profile url,
           discover by profiles array.
- Profiles (gd_lwxmeb2u1cniijd7t4): collect by URL, discover by user name.

Every method takes an optional ``limit_per_input`` to cap how many records are
collected per input (smaller = faster jobs); leaving it None means no cap.

API surface (mirrors the other scrapers - each verb has async + _sync +
_trigger/_status/_fetch):
- client.scrape.x.posts(url, ...)                                  # posts by URL
- client.scrape.x.posts_by_profile(url, start_date, end_date)      # discover_by=profile_url
- client.scrape.x.posts_by_profiles_array(urls, start_date, end_date)  # discover_by=profiles_array
- client.scrape.x.profiles(url, max_number_of_posts)               # profiles by URL
- client.scrape.x.profiles_by_username(user_name)                  # discover_by=user_name
"""

import asyncio
from typing import List, Any, Union, Optional

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, DEFAULT_COST_PER_RECORD


@register("x")
class XScraper(BaseWebScraper):
    """
    X (Twitter) scraper for posts and profiles.

    Example:
        >>> scraper = XScraper(bearer_token="token")
        >>>
        >>> # Posts by URL
        >>> result = await scraper.posts(
        ...     url="https://x.com/FabrizioRomano/status/1683559267524136962"
        ... )
        >>>
        >>> # Discover posts from a profile, capped + within a date range
        >>> result = await scraper.posts_by_profile(
        ...     url="https://x.com/elonmusk",
        ...     start_date="2023-01-15",
        ...     end_date="2024-03-15",
        ...     limit_per_input=50,
        ... )
        >>>
        >>> # Discover posts from several profiles in one request
        >>> result = await scraper.posts_by_profiles_array(
        ...     urls=["https://x.com/cnn", "https://x.com/BSCNews"],
        ...     limit_per_input=50,
        ... )
        >>>
        >>> # Profile by URL (cap how many posts to pull)
        >>> result = await scraper.profiles(url="https://x.com/elonmusk", max_number_of_posts=100)
        >>>
        >>> # Discover a profile by handle
        >>> result = await scraper.profiles_by_username(user_name="elonmusk")
    """

    # Posts is the default dataset (satisfies BaseWebScraper's DATASET_ID requirement)
    DATASET_ID = "gd_lwxkxvnf1cynvib9co"  # Posts (default)
    DATASET_ID_POSTS = "gd_lwxkxvnf1cynvib9co"
    DATASET_ID_PROFILES = "gd_lwxmeb2u1cniijd7t4"

    PLATFORM_NAME = "x"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = DEFAULT_COST_PER_RECORD

    # ============================================================================
    # POSTS - Collect by URL
    # ============================================================================

    async def posts(
        self,
        url: Union[str, List[str]],
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect X posts by post URL (async).

        Args:
            url: Post URL(s) like https://x.com/<user>/status/<id>
            limit_per_input: Optional cap on records collected per input URL.
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with post data
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
            limit_per_input=limit_per_input,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url
            result.data = result.data[0]
        return result

    def posts_sync(
        self,
        url: Union[str, List[str]],
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect X posts by post URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts(url, limit_per_input=limit_per_input, timeout=timeout)

        return asyncio.run(_run())

    # --- Posts Trigger/Status/Fetch ---

    async def posts_trigger(
        self,
        url: Union[str, List[str]],
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X posts collection by URL (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u} for u in url_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            limit_per_input=limit_per_input,
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def posts_trigger_sync(
        self,
        url: Union[str, List[str]],
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X posts collection by URL (sync)."""
        return asyncio.run(self.posts_trigger(url, limit_per_input=limit_per_input))

    async def posts_status(self, snapshot_id: str) -> str:
        """Check X posts collection status."""
        return await self._check_status_async(snapshot_id)

    def posts_status_sync(self, snapshot_id: str) -> str:
        """Check X posts collection status (sync)."""
        return asyncio.run(self.posts_status(snapshot_id))

    async def posts_fetch(self, snapshot_id: str) -> Any:
        """Fetch X posts results."""
        return await self._fetch_results_async(snapshot_id)

    def posts_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch X posts results (sync)."""
        return asyncio.run(self.posts_fetch(snapshot_id))

    # ============================================================================
    # POSTS - Discover by profile URL
    # ============================================================================

    async def posts_by_profile(
        self,
        url: Union[str, List[str]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover X posts from a profile URL (async).

        Args:
            url: Profile URL(s) like https://x.com/<user>
            start_date: Optional start of the date range (e.g. "2023-01-15" or ISO 8601).
            end_date: Optional end of the date range. The same range applies to all URLs.
            limit_per_input: Optional cap on posts discovered per profile (smaller = faster).
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult with the discovered posts
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        url_list = [url] if isinstance(url, str) else url
        payload = [
            {"url": u, "start_date": start_date or "", "end_date": end_date or ""} for u in url_list
        ]

        sdk_function = get_caller_function_name()
        return await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
            extra_params={"type": "discover_new", "discover_by": "profile_url"},
            limit_per_input=limit_per_input,
        )

    def posts_by_profile_sync(
        self,
        url: Union[str, List[str]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Discover X posts from a profile URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_profile(
                    url,
                    start_date=start_date,
                    end_date=end_date,
                    limit_per_input=limit_per_input,
                    timeout=timeout,
                )

        return asyncio.run(_run())

    # --- Discover-by-profile Trigger/Status/Fetch ---

    async def posts_by_profile_trigger(
        self,
        url: Union[str, List[str]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X posts discovery by profile URL (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [
            {"url": u, "start_date": start_date or "", "end_date": end_date or ""} for u in url_list
        ]

        snapshot_id = await self.api_client.trigger(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            extra_params={"type": "discover_new", "discover_by": "profile_url"},
            limit_per_input=limit_per_input,
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def posts_by_profile_trigger_sync(
        self,
        url: Union[str, List[str]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X posts discovery by profile URL (sync)."""
        return asyncio.run(
            self.posts_by_profile_trigger(
                url, start_date=start_date, end_date=end_date, limit_per_input=limit_per_input
            )
        )

    async def posts_by_profile_status(self, snapshot_id: str) -> str:
        """Check X posts-by-profile discovery status."""
        return await self._check_status_async(snapshot_id)

    def posts_by_profile_status_sync(self, snapshot_id: str) -> str:
        """Check X posts-by-profile discovery status (sync)."""
        return asyncio.run(self.posts_by_profile_status(snapshot_id))

    async def posts_by_profile_fetch(self, snapshot_id: str) -> Any:
        """Fetch X posts-by-profile discovery results."""
        return await self._fetch_results_async(snapshot_id)

    def posts_by_profile_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch X posts-by-profile discovery results (sync)."""
        return asyncio.run(self.posts_by_profile_fetch(snapshot_id))

    # ============================================================================
    # POSTS - Discover by profiles array
    # ============================================================================

    async def posts_by_profiles_array(
        self,
        urls: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover X posts from several profile URLs in a single request (async).

        Unlike posts_by_profile (one input row per URL), this sends one input row
        containing the whole array of profile URLs.

        Args:
            urls: List of profile URLs like https://x.com/<user>
            start_date: Optional start of the date range (applies to all URLs).
            end_date: Optional end of the date range.
            limit_per_input: Optional cap on posts discovered (smaller = faster).
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult with the discovered posts
        """
        validate_url_list(urls)

        payload = [{"urls": list(urls), "start_date": start_date or "", "end_date": end_date or ""}]

        sdk_function = get_caller_function_name()
        return await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
            extra_params={"type": "discover_new", "discover_by": "profiles_array"},
            limit_per_input=limit_per_input,
        )

    def posts_by_profiles_array_sync(
        self,
        urls: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Discover X posts from several profile URLs in one request (sync)."""

        async def _run():
            async with self.engine:
                return await self.posts_by_profiles_array(
                    urls,
                    start_date=start_date,
                    end_date=end_date,
                    limit_per_input=limit_per_input,
                    timeout=timeout,
                )

        return asyncio.run(_run())

    # --- Discover-by-profiles-array Trigger/Status/Fetch ---

    async def posts_by_profiles_array_trigger(
        self,
        urls: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X posts discovery by profiles array (manual control)."""
        validate_url_list(urls)
        payload = [{"urls": list(urls), "start_date": start_date or "", "end_date": end_date or ""}]

        snapshot_id = await self.api_client.trigger(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            extra_params={"type": "discover_new", "discover_by": "profiles_array"},
            limit_per_input=limit_per_input,
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def posts_by_profiles_array_trigger_sync(
        self,
        urls: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X posts discovery by profiles array (sync)."""
        return asyncio.run(
            self.posts_by_profiles_array_trigger(
                urls, start_date=start_date, end_date=end_date, limit_per_input=limit_per_input
            )
        )

    async def posts_by_profiles_array_status(self, snapshot_id: str) -> str:
        """Check X posts-by-profiles-array discovery status."""
        return await self._check_status_async(snapshot_id)

    def posts_by_profiles_array_status_sync(self, snapshot_id: str) -> str:
        """Check X posts-by-profiles-array discovery status (sync)."""
        return asyncio.run(self.posts_by_profiles_array_status(snapshot_id))

    async def posts_by_profiles_array_fetch(self, snapshot_id: str) -> Any:
        """Fetch X posts-by-profiles-array discovery results."""
        return await self._fetch_results_async(snapshot_id)

    def posts_by_profiles_array_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch X posts-by-profiles-array discovery results (sync)."""
        return asyncio.run(self.posts_by_profiles_array_fetch(snapshot_id))

    # ============================================================================
    # PROFILES - Collect by URL
    # ============================================================================

    async def profiles(
        self,
        url: Union[str, List[str]],
        max_number_of_posts: Optional[int] = None,
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect X profile data by profile URL (async).

        Args:
            url: Profile URL(s) like https://x.com/<user>
            max_number_of_posts: Optional cap on how many posts to pull per profile.
            limit_per_input: Optional cap on records collected per input.
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with profile data
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        is_single = isinstance(url, str)
        url_list = [url] if is_single else url
        payload = []
        for u in url_list:
            item: dict = {"url": u}
            if max_number_of_posts is not None:
                item["max_number_of_posts"] = max_number_of_posts
            payload.append(item)

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_PROFILES,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
            limit_per_input=limit_per_input,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url
            result.data = result.data[0]
        return result

    def profiles_sync(
        self,
        url: Union[str, List[str]],
        max_number_of_posts: Optional[int] = None,
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect X profile data by profile URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.profiles(
                    url,
                    max_number_of_posts=max_number_of_posts,
                    limit_per_input=limit_per_input,
                    timeout=timeout,
                )

        return asyncio.run(_run())

    # --- Profiles Trigger/Status/Fetch ---

    async def profiles_trigger(
        self,
        url: Union[str, List[str]],
        max_number_of_posts: Optional[int] = None,
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X profiles collection by URL (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = []
        for u in url_list:
            item: dict = {"url": u}
            if max_number_of_posts is not None:
                item["max_number_of_posts"] = max_number_of_posts
            payload.append(item)

        snapshot_id = await self.api_client.trigger(
            payload=payload,
            dataset_id=self.DATASET_ID_PROFILES,
            limit_per_input=limit_per_input,
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def profiles_trigger_sync(
        self,
        url: Union[str, List[str]],
        max_number_of_posts: Optional[int] = None,
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X profiles collection by URL (sync)."""
        return asyncio.run(
            self.profiles_trigger(
                url, max_number_of_posts=max_number_of_posts, limit_per_input=limit_per_input
            )
        )

    async def profiles_status(self, snapshot_id: str) -> str:
        """Check X profiles collection status."""
        return await self._check_status_async(snapshot_id)

    def profiles_status_sync(self, snapshot_id: str) -> str:
        """Check X profiles collection status (sync)."""
        return asyncio.run(self.profiles_status(snapshot_id))

    async def profiles_fetch(self, snapshot_id: str) -> Any:
        """Fetch X profiles results."""
        return await self._fetch_results_async(snapshot_id)

    def profiles_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch X profiles results (sync)."""
        return asyncio.run(self.profiles_fetch(snapshot_id))

    # ============================================================================
    # PROFILES - Discover by user name
    # ============================================================================

    async def profiles_by_username(
        self,
        user_name: Union[str, List[str]],
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Discover an X profile by handle / user name (async).

        Args:
            user_name: One handle or a list of handles, e.g. "elonmusk" (no URL).
            limit_per_input: Optional cap on records collected per input.
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with profile data
        """
        is_single = isinstance(user_name, str)
        name_list = [user_name] if is_single else user_name
        payload = [{"user_name": n} for n in name_list]

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_PROFILES,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
            extra_params={"type": "discover_new", "discover_by": "user_name"},
            limit_per_input=limit_per_input,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.data = result.data[0]
        return result

    def profiles_by_username_sync(
        self,
        user_name: Union[str, List[str]],
        limit_per_input: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Discover an X profile by handle / user name (sync)."""

        async def _run():
            async with self.engine:
                return await self.profiles_by_username(
                    user_name, limit_per_input=limit_per_input, timeout=timeout
                )

        return asyncio.run(_run())

    # --- Discover-by-username Trigger/Status/Fetch ---

    async def profiles_by_username_trigger(
        self,
        user_name: Union[str, List[str]],
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X profile discovery by user name (manual control)."""
        name_list = [user_name] if isinstance(user_name, str) else user_name
        payload = [{"user_name": n} for n in name_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload,
            dataset_id=self.DATASET_ID_PROFILES,
            extra_params={"type": "discover_new", "discover_by": "user_name"},
            limit_per_input=limit_per_input,
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def profiles_by_username_trigger_sync(
        self,
        user_name: Union[str, List[str]],
        limit_per_input: Optional[int] = None,
    ) -> ScrapeJob:
        """Trigger X profile discovery by user name (sync)."""
        return asyncio.run(
            self.profiles_by_username_trigger(user_name, limit_per_input=limit_per_input)
        )

    async def profiles_by_username_status(self, snapshot_id: str) -> str:
        """Check X profile-by-username discovery status."""
        return await self._check_status_async(snapshot_id)

    def profiles_by_username_status_sync(self, snapshot_id: str) -> str:
        """Check X profile-by-username discovery status (sync)."""
        return asyncio.run(self.profiles_by_username_status(snapshot_id))

    async def profiles_by_username_fetch(self, snapshot_id: str) -> Any:
        """Fetch X profile-by-username discovery results."""
        return await self._fetch_results_async(snapshot_id)

    def profiles_by_username_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch X profile-by-username discovery results (sync)."""
        return asyncio.run(self.profiles_by_username_fetch(snapshot_id))
