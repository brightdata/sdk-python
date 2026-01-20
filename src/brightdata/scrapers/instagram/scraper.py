"""
Instagram URL-based scraper for extracting data from Instagram URLs.

Supports:
- Profile extraction from profile URLs
- Post extraction from post URLs
- Reel extraction from reel URLs
- Comment extraction from post/reel URLs
"""

import asyncio
from typing import List, Any, Union

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...constants import (
    COST_PER_RECORD_INSTAGRAM,
    DEFAULT_TIMEOUT_SHORT,
    DEFAULT_POLL_INTERVAL,
)
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name


@register("instagram")
class InstagramScraper(BaseWebScraper):
    """
    Instagram scraper for URL-based data extraction.

    Extracts structured data from Instagram URLs including profiles,
    posts, reels, and comments.

    Example:
        >>> async with InstagramScraper(bearer_token="...") as scraper:
        ...     result = await scraper.profiles("https://instagram.com/nasa")
        ...     print(result.data)
    """

    # Dataset IDs for different content types
    DATASET_ID = "gd_l1vikfch901nx3by4"  # Profiles (default)
    DATASET_ID_POSTS = "gd_lk5ns7kz21pck8jpis"
    DATASET_ID_REELS = "gd_lyclm20il4r5helnj"
    DATASET_ID_COMMENTS = "gd_ltppn085pokosxh13"

    # Platform configuration
    PLATFORM_NAME = "instagram"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_SHORT  # 180s
    COST_PER_RECORD = COST_PER_RECORD_INSTAGRAM  # 0.002

    # ============================================================================
    # INTERNAL HELPERS
    # ============================================================================

    async def _scrape_urls(
        self,
        url: Union[str, List[str]],
        dataset_id: str,
        timeout: int,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Internal method to scrape URLs with specified dataset.

        Args:
            url: Single URL or list of URLs to scrape
            dataset_id: Bright Data dataset identifier for this content type
            timeout: Maximum seconds to wait for results

        Returns:
            ScrapeResult for single URL, List[ScrapeResult] for multiple URLs
        """
        # Normalize input
        is_single = isinstance(url, str)
        url_list = [url] if is_single else url

        # Validate
        if is_single:
            validate_url(url)
        else:
            validate_url_list(url_list)

        # Build simple payload
        payload = [{"url": u} for u in url_list]

        # Get SDK function name for tracking
        sdk_function = get_caller_function_name()

        # Execute workflow
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=dataset_id,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
        )

        # Transform result based on input type
        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            # Single URL: unwrap single item
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]
            return result
        elif not is_single and isinstance(result.data, list):
            # Multiple URLs: create individual ScrapeResult for each
            results = []
            for url_item, data_item in zip(url_list, result.data):
                individual_result = ScrapeResult(
                    success=True,
                    data=data_item,
                    url=url_item,
                    error=None,
                    platform=result.platform,
                    method=result.method,
                    trigger_sent_at=result.trigger_sent_at,
                    snapshot_id_received_at=result.snapshot_id_received_at,
                    snapshot_polled_at=result.snapshot_polled_at,
                    data_fetched_at=result.data_fetched_at,
                    snapshot_id=result.snapshot_id,
                    cost=result.cost / len(result.data) if result.cost else None,
                )
                results.append(individual_result)
            return results

        return result

    # ============================================================================
    # PROFILES (URL-based extraction)
    # ============================================================================

    async def profiles(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Extract profile data from Instagram profile URLs.

        Args:
            url: Profile URL or list of profile URLs
                 Example: "https://www.instagram.com/nasa/"
            timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult for single URL, List[ScrapeResult] for multiple URLs

        Example:
            >>> result = await scraper.profiles("https://instagram.com/nasa")
            >>> print(result.data["followers"])
        """
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID,
            timeout=timeout,
        )

    def profiles_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Synchronous version of profiles(). See profiles() for documentation."""

        async def _run():
            async with self.engine:
                return await self.profiles(url, timeout)

        return asyncio.run(_run())

    async def profiles_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """
        Trigger profile extraction job without waiting for results.

        Args:
            url: Profile URL or list of profile URLs

        Returns:
            ScrapeJob for status checking and result fetching

        Example:
            >>> job = await scraper.profiles_trigger("https://instagram.com/nasa")
            >>> status = await job.status()
            >>> if status == "ready":
            ...     data = await job.fetch()
        """
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID,
            sdk_function=sdk_function,
        )

    def profiles_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Synchronous version of profiles_trigger()."""

        async def _run():
            async with self.engine:
                return await self.profiles_trigger(url)

        return asyncio.run(_run())

    async def profiles_status(self, snapshot_id: str) -> str:
        """Check status of a profiles extraction job."""
        return await self._check_status_async(snapshot_id)

    def profiles_status_sync(self, snapshot_id: str) -> str:
        """Synchronous version of profiles_status()."""

        async def _run():
            async with self.engine:
                return await self.profiles_status(snapshot_id)

        return asyncio.run(_run())

    async def profiles_fetch(self, snapshot_id: str) -> Any:
        """Fetch results of a completed profiles extraction job."""
        return await self._fetch_results_async(snapshot_id)

    def profiles_fetch_sync(self, snapshot_id: str) -> Any:
        """Synchronous version of profiles_fetch()."""

        async def _run():
            async with self.engine:
                return await self.profiles_fetch(snapshot_id)

        return asyncio.run(_run())

    # ============================================================================
    # POSTS (URL-based extraction)
    # ============================================================================

    async def posts(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Extract post data from Instagram post URLs.

        Args:
            url: Post URL or list of post URLs
                 Example: "https://www.instagram.com/p/Cuf4s0MNqNr"
            timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult for single URL, List[ScrapeResult] for multiple URLs

            Response data fields:
                - post_id (str): Unique post identifier
                - shortcode (str): URL shortcode (e.g., "DTGAZJQkg5k")
                - content_type (str): "Image", "Video", or "Carousel"
                - description (str): Post caption text
                - date_posted (str): ISO timestamp of posting
                - likes (int): Number of likes
                - num_comments (int): Number of comments
                - user_posted (str): Username who posted
                - user_posted_id (str): User's numeric ID
                - profile_url (str): URL to user's profile
                - followers (int): User's follower count
                - is_verified (bool): Whether user is verified
                - photos (list): List of photo URLs
                - thumbnail (str): Thumbnail image URL
                - post_content (list): Detailed content items with type, url, alt_text
                - latest_comments (list): Recent comments with user, text, likes
                - is_paid_partnership (bool): Whether post is sponsored

        Example:
            >>> result = await scraper.posts("https://instagram.com/p/ABC123/")
            >>> print(result.data["description"])  # Caption
            >>> print(result.data["likes"])  # Like count
        """
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_POSTS,
            timeout=timeout,
        )

    def posts_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Synchronous version of posts()."""

        async def _run():
            async with self.engine:
                return await self.posts(url, timeout)

        return asyncio.run(_run())

    async def posts_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger post extraction job without waiting for results."""
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_POSTS,
            sdk_function=sdk_function,
        )

    def posts_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Synchronous version of posts_trigger()."""

        async def _run():
            async with self.engine:
                return await self.posts_trigger(url)

        return asyncio.run(_run())

    async def posts_status(self, snapshot_id: str) -> str:
        """Check status of a posts extraction job."""
        return await self._check_status_async(snapshot_id)

    def posts_status_sync(self, snapshot_id: str) -> str:
        """Synchronous version of posts_status()."""

        async def _run():
            async with self.engine:
                return await self.posts_status(snapshot_id)

        return asyncio.run(_run())

    async def posts_fetch(self, snapshot_id: str) -> Any:
        """Fetch results of a completed posts extraction job."""
        return await self._fetch_results_async(snapshot_id)

    def posts_fetch_sync(self, snapshot_id: str) -> Any:
        """Synchronous version of posts_fetch()."""

        async def _run():
            async with self.engine:
                return await self.posts_fetch(snapshot_id)

        return asyncio.run(_run())

    # ============================================================================
    # REELS (URL-based extraction)
    # ============================================================================

    async def reels(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Extract reel data from Instagram reel URLs.

        Args:
            url: Reel URL or list of reel URLs
                 Example: "https://www.instagram.com/reel/C5Rdyj_q7YN/"
            timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult for single URL, List[ScrapeResult] for multiple URLs

            Response data fields:
                - post_id (str): Unique reel identifier
                - shortcode (str): URL shortcode (e.g., "DTQygzxD6QC")
                - product_type (str): Content type, typically "clips" for reels
                - description (str): Reel caption text
                - hashtags (list): Hashtags used in caption
                - date_posted (str): ISO timestamp of posting
                - likes (int): Number of likes
                - views (int): Number of views
                - video_play_count (int): Number of video plays
                - num_comments (int): Number of comments
                - length (float): Video duration in seconds
                - video_url (str): Direct URL to video file
                - audio_url (str): Direct URL to audio track
                - thumbnail (str): Thumbnail image URL
                - user_posted (str): Username who posted
                - user_profile_url (str): URL to user's profile
                - followers (int): User's follower count
                - is_verified (bool): Whether user is verified
                - top_comments (list): Top comments on the reel
                - tagged_users (list): Users tagged in the reel
                - is_paid_partnership (bool): Whether reel is sponsored

        Example:
            >>> result = await scraper.reels("https://instagram.com/reel/XYZ789/")
            >>> print(result.data["views"])  # View count
            >>> print(result.data["video_url"])  # Download URL
        """
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_REELS,
            timeout=timeout,
        )

    def reels_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Synchronous version of reels()."""

        async def _run():
            async with self.engine:
                return await self.reels(url, timeout)

        return asyncio.run(_run())

    async def reels_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger reel extraction job without waiting for results."""
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_REELS,
            sdk_function=sdk_function,
        )

    def reels_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Synchronous version of reels_trigger()."""

        async def _run():
            async with self.engine:
                return await self.reels_trigger(url)

        return asyncio.run(_run())

    async def reels_status(self, snapshot_id: str) -> str:
        """Check status of a reels extraction job."""
        return await self._check_status_async(snapshot_id)

    def reels_status_sync(self, snapshot_id: str) -> str:
        """Synchronous version of reels_status()."""

        async def _run():
            async with self.engine:
                return await self.reels_status(snapshot_id)

        return asyncio.run(_run())

    async def reels_fetch(self, snapshot_id: str) -> Any:
        """Fetch results of a completed reels extraction job."""
        return await self._fetch_results_async(snapshot_id)

    def reels_fetch_sync(self, snapshot_id: str) -> Any:
        """Synchronous version of reels_fetch()."""

        async def _run():
            async with self.engine:
                return await self.reels_fetch(snapshot_id)

        return asyncio.run(_run())

    # ============================================================================
    # COMMENTS (URL-based extraction)
    # ============================================================================

    async def comments(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Extract comments from Instagram post or reel URLs.

        Args:
            url: Post/reel URL or list of URLs
                 Example: "https://www.instagram.com/p/CesFC7JLyFl/"
            timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult for single URL, List[ScrapeResult] for multiple URLs

            Note: Returns a LIST of comment objects in result.data

            Response data fields (per comment):
                - comment_id (str): Unique comment identifier
                - post_id (str): ID of the post/reel commented on
                - post_url (str): URL of the post/reel
                - post_user (str): Username of post author
                - comment_user (str): Username who wrote the comment
                - comment_user_url (str): URL to commenter's profile
                - comment (str): The comment text
                - comment_date (str): ISO timestamp of comment
                - likes_number (int): Number of likes on comment
                - replies_number (int): Number of replies to comment

        Example:
            >>> result = await scraper.comments("https://instagram.com/p/ABC123/")
            >>> for comment in result.data:
            ...     print(f"{comment['comment_user']}: {comment['comment']}")
        """
        return await self._scrape_urls(
            url=url,
            dataset_id=self.DATASET_ID_COMMENTS,
            timeout=timeout,
        )

    def comments_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Synchronous version of comments()."""

        async def _run():
            async with self.engine:
                return await self.comments(url, timeout)

        return asyncio.run(_run())

    async def comments_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger comment extraction job without waiting for results."""
        sdk_function = get_caller_function_name()
        return await self._trigger_scrape_async(
            urls=url,
            dataset_id=self.DATASET_ID_COMMENTS,
            sdk_function=sdk_function,
        )

    def comments_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Synchronous version of comments_trigger()."""

        async def _run():
            async with self.engine:
                return await self.comments_trigger(url)

        return asyncio.run(_run())

    async def comments_status(self, snapshot_id: str) -> str:
        """Check status of a comments extraction job."""
        return await self._check_status_async(snapshot_id)

    def comments_status_sync(self, snapshot_id: str) -> str:
        """Synchronous version of comments_status()."""

        async def _run():
            async with self.engine:
                return await self.comments_status(snapshot_id)

        return asyncio.run(_run())

    async def comments_fetch(self, snapshot_id: str) -> Any:
        """Fetch results of a completed comments extraction job."""
        return await self._fetch_results_async(snapshot_id)

    def comments_fetch_sync(self, snapshot_id: str) -> Any:
        """Synchronous version of comments_fetch()."""

        async def _run():
            async with self.engine:
                return await self.comments_fetch(snapshot_id)

        return asyncio.run(_run())
