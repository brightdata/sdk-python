"""
Instagram parameter-based discovery scraper.

Supports:
- Profile discovery by username
- Posts discovery from profile with filters
- Reels discovery from profile with filters
"""

import asyncio
import os
from typing import List, Dict, Any, Optional, Union

from ..api_client import DatasetAPIClient
from ..workflow import WorkflowExecutor
from ...core.engine import AsyncEngine
from ...models import ScrapeResult
from ...exceptions import ValidationError
from ...constants import (
    COST_PER_RECORD_INSTAGRAM,
    DEFAULT_TIMEOUT_SHORT,
    DEFAULT_POLL_INTERVAL,
)
from ...utils.validation import validate_url_list, validate_instagram_date
from ...utils.function_detection import get_caller_function_name


class InstagramSearchScraper:
    """
    Instagram scraper for parameter-based content discovery.

    Unlike InstagramScraper (URL-based), this class discovers content
    using parameters like username, date ranges, and filters.

    Example:
        >>> scraper = InstagramSearchScraper(bearer_token="...")
        >>> result = await scraper.profiles("nasa")  # Find by username
        >>> result = await scraper.posts(
        ...     url="https://instagram.com/nasa",
        ...     num_of_posts=10,
        ...     start_date="01-01-2025"
        ... )
    """

    # Dataset IDs
    DATASET_ID_PROFILES = "gd_l1vikfch901nx3by4"
    DATASET_ID_POSTS = "gd_lk5ns7kz21pck8jpis"
    DATASET_ID_REELS = "gd_lyclm20il4r5helnj"

    # Platform configuration
    PLATFORM_NAME = "instagram"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_SHORT
    COST_PER_RECORD = COST_PER_RECORD_INSTAGRAM

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        engine: Optional[AsyncEngine] = None,
    ):
        """
        Initialize Instagram search scraper.

        Args:
            bearer_token: Bright Data API token. If None, loads from environment.
            engine: Optional AsyncEngine instance for connection reuse.
        """
        self.bearer_token = bearer_token or os.getenv("BRIGHTDATA_API_TOKEN")
        if not self.bearer_token:
            raise ValidationError(
                "Bearer token required for Instagram search. "
                "Provide bearer_token parameter or set BRIGHTDATA_API_TOKEN environment variable."
            )

        # Reuse engine if provided, otherwise create new
        self.engine = engine if engine is not None else AsyncEngine(self.bearer_token)
        self.api_client = DatasetAPIClient(self.engine)
        self.workflow_executor = WorkflowExecutor(
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    # ============================================================================
    # CONTEXT MANAGER SUPPORT
    # ============================================================================

    async def __aenter__(self):
        """Async context manager entry."""
        await self.engine.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.engine.__aexit__(exc_type, exc_val, exc_tb)

    # ============================================================================
    # INTERNAL HELPERS
    # ============================================================================

    async def _execute_discovery(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        discover_by: str,
        timeout: int,
    ) -> ScrapeResult:
        """
        Execute discovery operation with extra query parameters.

        Args:
            payload: Request payload
            dataset_id: Bright Data dataset identifier
            discover_by: Discovery type (user_name, url, url_all_reels)
            timeout: Maximum seconds to wait

        Returns:
            ScrapeResult with discovered data
        """
        sdk_function = get_caller_function_name()

        # Build extra params for discovery endpoints
        extra_params = {
            "type": "discover_new",
            "discover_by": discover_by,
        }

        # Use workflow_executor.execute() with extra_params support
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
    # PROFILES DISCOVERY (by username)
    # ============================================================================

    async def profiles(
        self,
        user_name: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Discover Instagram profiles by username (exact match).

        Args:
            user_name: Username or list of usernames (without @)
                       Example: "nasa" or ["nasa", "spacex"]
            timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult with profile data

            Response data fields:
                - account (str): Username/handle
                - id (str): Numeric user ID
                - full_name (str): Display name
                - profile_name (str): Profile display name
                - profile_url (str): URL to profile
                - profile_image_link (str): Profile picture URL
                - followers (int): Follower count
                - following (int): Following count
                - posts_count (int): Number of posts
                - highlights_count (int): Number of highlights
                - is_verified (bool): Verification status
                - is_private (bool): Whether account is private
                - is_business_account (bool): Business account flag
                - is_professional_account (bool): Professional account flag
                - biography (str): Bio text
                - bio_hashtags (list): Hashtags in bio
                - category_name (str): Account category
                - external_url (str): Link in bio
                - avg_engagement (float): Average engagement rate
                - posts (list): Recent posts data
                - highlights (list): Highlights data
                - related_accounts (list): Similar accounts

        Example:
            >>> result = await scraper.profiles("nasa")
            >>> print(result.data["followers"])  # 97896265
            >>> print(result.data["biography"])  # Bio text
        """
        # Normalize to list
        user_names = [user_name] if isinstance(user_name, str) else user_name

        # Build payload - IMPORTANT: field is "user_name" with underscore
        payload = [{"user_name": name} for name in user_names]

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_PROFILES,
            discover_by="user_name",
            timeout=timeout,
        )

    def profiles_sync(
        self,
        user_name: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """Synchronous version of profiles()."""

        async def _run():
            async with self.engine:
                return await self.profiles(user_name, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # POSTS DISCOVERY (by profile URL + filters)
    # ============================================================================

    async def posts(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        post_type: Optional[str] = None,
        posts_to_not_include: Optional[List[str]] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Discover posts from Instagram profile with optional filters.

        Args:
            url: Profile URL or list of profile URLs
                 Example: "https://www.instagram.com/nasa/"
            num_of_posts: Maximum number of posts to return
            start_date: Filter posts on or after this date (format: MM-DD-YYYY)
            end_date: Filter posts on or before this date (format: MM-DD-YYYY)
            post_type: Filter by type - "Post" or "Reel"
            posts_to_not_include: List of post IDs to exclude
            timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult with discovered posts (list in result.data)

            Response data fields (per post):
                - post_id (str): Unique post identifier
                - shortcode (str): URL shortcode
                - content_type (str): "Image", "Video", or "Carousel"
                - description (str): Post caption text
                - date_posted (str): ISO timestamp of posting
                - likes (int): Number of likes
                - num_comments (int): Number of comments
                - user_posted (str): Username who posted
                - photos (list): List of photo URLs
                - thumbnail (str): Thumbnail image URL
                - is_paid_partnership (bool): Whether post is sponsored

        Example:
            >>> result = await scraper.posts(
            ...     url="https://instagram.com/nasa",
            ...     num_of_posts=10,
            ...     start_date="01-01-2025",
            ...     post_type="Post"
            ... )
            >>> for post in result.data:
            ...     print(post["description"])
        """
        # Normalize URL to list
        urls = [url] if isinstance(url, str) else url

        # Validate URLs
        validate_url_list(urls)

        # Validate dates if provided
        if start_date:
            validate_instagram_date(start_date)
        if end_date:
            validate_instagram_date(end_date)

        # Build payload - omit None values (don't send empty strings)
        payload = []
        for u in urls:
            item: Dict[str, Any] = {"url": u}

            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if start_date:
                item["start_date"] = start_date
            if end_date:
                item["end_date"] = end_date
            if post_type:
                item["post_type"] = post_type
            if posts_to_not_include:
                item["posts_to_not_include"] = posts_to_not_include

            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            discover_by="url",
            timeout=timeout,
        )

    def posts_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        post_type: Optional[str] = None,
        posts_to_not_include: Optional[List[str]] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """Synchronous version of posts()."""

        async def _run():
            async with self.engine:
                return await self.posts(
                    url,
                    num_of_posts,
                    start_date,
                    end_date,
                    post_type,
                    posts_to_not_include,
                    timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # REELS DISCOVERY (by profile URL)
    # ============================================================================

    async def reels(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Discover reels from Instagram profile.

        Args:
            url: Profile URL or list of profile URLs
            num_of_posts: Maximum number of reels to return
            start_date: Filter reels on or after this date (format: MM-DD-YYYY)
            end_date: Filter reels on or before this date (format: MM-DD-YYYY)
            timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult with discovered reels (list in result.data)

            Response data fields (per reel):
                - post_id (str): Unique reel identifier
                - shortcode (str): URL shortcode
                - product_type (str): Content type ("clips")
                - description (str): Reel caption text
                - date_posted (str): ISO timestamp of posting
                - likes (int): Number of likes
                - views (int): Number of views
                - video_play_count (int): Number of video plays
                - num_comments (int): Number of comments
                - length (float): Video duration in seconds
                - video_url (str): Direct URL to video file
                - thumbnail (str): Thumbnail image URL
                - user_posted (str): Username who posted

        Example:
            >>> result = await scraper.reels(
            ...     url="https://instagram.com/nasa",
            ...     num_of_posts=5
            ... )
            >>> for reel in result.data:
            ...     print(f"{reel['views']} views")
        """
        # Normalize and validate
        urls = [url] if isinstance(url, str) else url
        validate_url_list(urls)

        if start_date:
            validate_instagram_date(start_date)
        if end_date:
            validate_instagram_date(end_date)

        # Build payload
        payload = []
        for u in urls:
            item: Dict[str, Any] = {"url": u}
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if start_date:
                item["start_date"] = start_date
            if end_date:
                item["end_date"] = end_date
            payload.append(item)

        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_REELS,
            discover_by="url",
            timeout=timeout,
        )

    def reels_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """Synchronous version of reels()."""

        async def _run():
            async with self.engine:
                return await self.reels(url, num_of_posts, start_date, end_date, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # REELS ALL DISCOVERY (by profile URL - all reels)
    # ============================================================================

    async def reels_all(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Discover ALL reels from Instagram profile.

        This differs from reels() by using discover_by=url_all_reels,
        which may return more comprehensive results including archived reels.

        Args:
            url: Profile URL or list of profile URLs
            num_of_posts: Maximum number of reels to return
            start_date: Filter reels on or after this date (format: MM-DD-YYYY)
            end_date: Filter reels on or before this date (format: MM-DD-YYYY)
            timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult with discovered reels (list in result.data)

            Response data fields (per reel):
                - post_id (str): Unique reel identifier
                - shortcode (str): URL shortcode
                - product_type (str): Content type ("clips")
                - description (str): Reel caption text
                - date_posted (str): ISO timestamp of posting
                - likes (int): Number of likes
                - views (int): Number of views
                - video_play_count (int): Number of video plays
                - num_comments (int): Number of comments
                - length (float): Video duration in seconds
                - video_url (str): Direct URL to video file
                - thumbnail (str): Thumbnail image URL
                - user_posted (str): Username who posted

        Example:
            >>> result = await scraper.reels_all(
            ...     url="https://instagram.com/nasa",
            ...     num_of_posts=20
            ... )
        """
        # Normalize and validate
        urls = [url] if isinstance(url, str) else url
        validate_url_list(urls)

        if start_date:
            validate_instagram_date(start_date)
        if end_date:
            validate_instagram_date(end_date)

        # Build payload
        payload = []
        for u in urls:
            item: Dict[str, Any] = {"url": u}
            if num_of_posts is not None:
                item["num_of_posts"] = num_of_posts
            if start_date:
                item["start_date"] = start_date
            if end_date:
                item["end_date"] = end_date
            payload.append(item)

        # Key difference: discover_by=url_all_reels
        return await self._execute_discovery(
            payload=payload,
            dataset_id=self.DATASET_ID_REELS,
            discover_by="url_all_reels",
            timeout=timeout,
        )

    def reels_all_sync(
        self,
        url: Union[str, List[str]],
        num_of_posts: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """Synchronous version of reels_all()."""

        async def _run():
            async with self.engine:
                return await self.reels_all(url, num_of_posts, start_date, end_date, timeout)

        return asyncio.run(_run())
