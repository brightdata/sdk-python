"""
YouTube scraper - URL-based collection for videos, channels, and comments.

Supports:
- Videos: collect by URL
- Channels/Profiles: collect by URL
- Comments: collect by URL

For discovery/search operations, see search.py which contains YouTubeSearchScraper.

API Specifications:
- client.scrape.youtube.videos(url, ...)                     # async
- client.scrape.youtube.videos_sync(url, ...)                # sync
- client.scrape.youtube.channels(url, ...)                   # async
- client.scrape.youtube.channels_sync(url, ...)              # sync
- client.scrape.youtube.comments(url, ...)                   # async
- client.scrape.youtube.comments_sync(url, ...)              # sync
"""

import asyncio
from typing import List, Any, Optional, Union

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, COST_PER_RECORD_YOUTUBE


@register("youtube")
class YouTubeScraper(BaseWebScraper):
    """
    YouTube scraper for URL-based collection.

    Extracts structured data from YouTube URLs for:
    - Videos (with optional transcription)
    - Channels/Profiles
    - Comments

    For discovery operations (by keyword, hashtag, etc.), use YouTubeSearchScraper.

    Example:
        >>> scraper = YouTubeScraper(bearer_token="token")
        >>>
        >>> # Collect video data
        >>> result = await scraper.videos(
        ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ... )
        >>>
        >>> # Collect channel data
        >>> result = await scraper.channels(
        ...     url="https://www.youtube.com/@MrBeast/about"
        ... )
        >>>
        >>> # Collect comments
        >>> result = await scraper.comments(
        ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ...     num_of_comments=100
        ... )
    """

    # Dataset IDs
    DATASET_ID = "gd_lk56epmy2i5g7lzu0k"  # Videos (default)
    DATASET_ID_VIDEOS = "gd_lk56epmy2i5g7lzu0k"
    DATASET_ID_CHANNELS = "gd_lk538t2k2p1k3oos71"
    DATASET_ID_COMMENTS = "gd_lk9q0ew71spt1mxywf"

    PLATFORM_NAME = "youtube"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = COST_PER_RECORD_YOUTUBE

    # ============================================================================
    # VIDEOS - Collect by URL
    # ============================================================================

    async def videos(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
        transcription_language: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect YouTube video data by URL (async).

        Args:
            url: Video URL(s) like https://www.youtube.com/watch?v=VIDEO_ID
            country: Country code for request context (optional)
            transcription_language: Language name for video transcription (optional).
                Use full language names like "English", "German", "Spanish", etc.
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with video data

        Example:
            >>> result = await scraper.videos(
            ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            ...     transcription_language="English"
            ... )
            >>> print(result.data["title"])
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        is_single = isinstance(url, str)
        url_list = [url] if is_single else url

        payload = []
        for u in url_list:
            item = {"url": u, "country": country or ""}
            if transcription_language:
                item["transcription_language"] = transcription_language
            payload.append(item)

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID_VIDEOS,
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

    def videos_sync(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
        transcription_language: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect YouTube video data by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.videos(url, country, transcription_language, timeout)

        return asyncio.run(_run())

    # --- Videos Trigger/Status/Fetch ---

    async def videos_trigger(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
        transcription_language: Optional[str] = None,
    ) -> ScrapeJob:
        """Trigger YouTube videos collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url

        payload = []
        for u in url_list:
            item = {"url": u, "country": country or ""}
            if transcription_language:
                item["transcription_language"] = transcription_language
            payload.append(item)

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_VIDEOS
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def videos_trigger_sync(
        self,
        url: Union[str, List[str]],
        country: Optional[str] = None,
        transcription_language: Optional[str] = None,
    ) -> ScrapeJob:
        """Trigger YouTube videos collection (sync)."""
        return asyncio.run(self.videos_trigger(url, country, transcription_language))

    async def videos_status(self, snapshot_id: str) -> str:
        """Check YouTube videos collection status."""
        return await self._check_status_async(snapshot_id)

    def videos_status_sync(self, snapshot_id: str) -> str:
        """Check YouTube videos collection status (sync)."""
        return asyncio.run(self.videos_status(snapshot_id))

    async def videos_fetch(self, snapshot_id: str) -> Any:
        """Fetch YouTube videos results."""
        return await self._fetch_results_async(snapshot_id)

    def videos_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch YouTube videos results (sync)."""
        return asyncio.run(self.videos_fetch(snapshot_id))

    # ============================================================================
    # CHANNELS/PROFILES - Collect by URL
    # ============================================================================

    async def channels(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect YouTube channel/profile data by URL (async).

        Args:
            url: Channel URL(s) like https://www.youtube.com/@ChannelName/about
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with channel data

        Example:
            >>> result = await scraper.channels(
            ...     url="https://www.youtube.com/@MrBeast/about"
            ... )
            >>> print(result.data["subscribers"])
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
            dataset_id=self.DATASET_ID_CHANNELS,
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

    def channels_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect YouTube channel data by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.channels(url, timeout)

        return asyncio.run(_run())

    # --- Channels Trigger/Status/Fetch ---

    async def channels_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger YouTube channels collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u} for u in url_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload, dataset_id=self.DATASET_ID_CHANNELS
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def channels_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger YouTube channels collection (sync)."""
        return asyncio.run(self.channels_trigger(url))

    async def channels_status(self, snapshot_id: str) -> str:
        """Check YouTube channels collection status."""
        return await self._check_status_async(snapshot_id)

    def channels_status_sync(self, snapshot_id: str) -> str:
        """Check YouTube channels collection status (sync)."""
        return asyncio.run(self.channels_status(snapshot_id))

    async def channels_fetch(self, snapshot_id: str) -> Any:
        """Fetch YouTube channels results."""
        return await self._fetch_results_async(snapshot_id)

    def channels_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch YouTube channels results (sync)."""
        return asyncio.run(self.channels_fetch(snapshot_id))

    # ============================================================================
    # COMMENTS - Collect by URL
    # ============================================================================

    async def comments(
        self,
        url: Union[str, List[str]],
        num_of_comments: Optional[int] = None,
        load_replies: Optional[bool] = None,
        sort_by: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect YouTube comments from video URL(s) (async).

        Args:
            url: Video URL(s) to collect comments from
            num_of_comments: Maximum number of comments to collect
            load_replies: Whether to load replies to comments
            sort_by: Sort order - "Newest first" or "Top comments"
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with comments

        Example:
            >>> result = await scraper.comments(
            ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            ...     num_of_comments=100,
            ...     sort_by="Newest first"
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
            item = {"url": u}
            if num_of_comments is not None:
                item["num_of_comments"] = num_of_comments
            if load_replies is not None:
                item["load_replies"] = load_replies
            if sort_by:
                item["sort_by"] = sort_by
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
        num_of_comments: Optional[int] = None,
        load_replies: Optional[bool] = None,
        sort_by: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect YouTube comments (sync)."""

        async def _run():
            async with self.engine:
                return await self.comments(url, num_of_comments, load_replies, sort_by, timeout)

        return asyncio.run(_run())

    # --- Comments Trigger/Status/Fetch ---

    async def comments_trigger(
        self,
        url: Union[str, List[str]],
        num_of_comments: Optional[int] = None,
        load_replies: Optional[bool] = None,
        sort_by: Optional[str] = None,
    ) -> ScrapeJob:
        """Trigger YouTube comments collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url

        payload = []
        for u in url_list:
            item = {"url": u}
            if num_of_comments is not None:
                item["num_of_comments"] = num_of_comments
            if load_replies is not None:
                item["load_replies"] = load_replies
            if sort_by:
                item["sort_by"] = sort_by
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
        num_of_comments: Optional[int] = None,
        load_replies: Optional[bool] = None,
        sort_by: Optional[str] = None,
    ) -> ScrapeJob:
        """Trigger YouTube comments collection (sync)."""
        return asyncio.run(self.comments_trigger(url, num_of_comments, load_replies, sort_by))

    async def comments_status(self, snapshot_id: str) -> str:
        """Check YouTube comments collection status."""
        return await self._check_status_async(snapshot_id)

    def comments_status_sync(self, snapshot_id: str) -> str:
        """Check YouTube comments collection status (sync)."""
        return asyncio.run(self.comments_status(snapshot_id))

    async def comments_fetch(self, snapshot_id: str) -> Any:
        """Fetch YouTube comments results."""
        return await self._fetch_results_async(snapshot_id)

    def comments_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch YouTube comments results (sync)."""
        return asyncio.run(self.comments_fetch(snapshot_id))
