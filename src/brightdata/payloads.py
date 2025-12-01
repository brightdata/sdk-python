"""
Dataclass-based payload definitions for all Bright Data SDK operations.

This module replaces the TypedDict definitions in types.py with dataclasses
for consistency with the result models and to provide:
- Runtime validation
- Default values
- Better IDE support
- Methods and properties
- Consistent developer experience

All payload classes can be converted to dict via asdict() when needed for API calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import re
from urllib.parse import urlparse


# ============================================================================
# BASE PAYLOAD CLASSES
# ============================================================================


@dataclass
class BasePayload:
    """Base class for all payloads with common validation."""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert payload to dictionary for API calls.

        Excludes None values to avoid sending unnecessary parameters.

        Returns:
            Dictionary representation suitable for API requests.
        """
        return {k: v for k, v in asdict(self).items() if v is not None}

    def validate(self) -> None:
        """
        Validate payload fields.

        Override in subclasses for custom validation logic.

        Raises:
            ValueError: If validation fails.
        """
        pass


@dataclass
class URLPayload(BasePayload):
    """Base payload for URL-based operations."""

    url: str

    def __post_init__(self):
        """Validate URL format."""
        if not isinstance(self.url, str):
            raise TypeError(f"url must be string, got {type(self.url).__name__}")

        if not self.url.strip():
            raise ValueError("url cannot be empty")

        if not self.url.startswith(("http://", "https://")):
            raise ValueError(f"url must be valid HTTP/HTTPS URL, got: {self.url}")

        self.url = self.url.strip()

    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        parsed = urlparse(self.url)
        return parsed.netloc

    @property
    def is_secure(self) -> bool:
        """Check if URL uses HTTPS."""
        return self.url.startswith("https://")


# ============================================================================
# AMAZON PAYLOADS
# ============================================================================


@dataclass
class AmazonProductPayload(URLPayload):
    """
    Amazon product scrape payload.

    Attributes:
        url: Amazon product URL (required)
        reviews_count: Number of reviews to fetch (default: None)
        images_count: Number of images to fetch (default: None)

    Example:
        >>> payload = AmazonProductPayload(
        ...     url="https://amazon.com/dp/B0CRMZHDG8",
        ...     reviews_count=50
        ... )
        >>> print(payload.asin)  # "B0CRMZHDG8"
    """

    reviews_count: Optional[int] = None
    images_count: Optional[int] = None

    def __post_init__(self):
        """Validate Amazon-specific fields."""
        super().__post_init__()

        if "amazon.com" not in self.url.lower():
            raise ValueError(f"url must be an Amazon URL, got: {self.url}")

        if self.reviews_count is not None and self.reviews_count < 0:
            raise ValueError(f"reviews_count must be non-negative, got {self.reviews_count}")

        if self.images_count is not None and self.images_count < 0:
            raise ValueError(f"images_count must be non-negative, got {self.images_count}")

    @property
    def asin(self) -> Optional[str]:
        """Extract ASIN (Amazon Standard Identification Number) from URL."""
        match = re.search(r"/dp/([A-Z0-9]{10})", self.url)
        return match.group(1) if match else None

    @property
    def is_product_url(self) -> bool:
        """Check if URL is a product detail page."""
        return "/dp/" in self.url or "/gp/product/" in self.url


@dataclass
class AmazonReviewPayload(URLPayload):
    """
    Amazon review scrape payload.

    Attributes:
        url: Amazon product URL (required)
        pastDays: Number of past days to fetch reviews from (optional)
        keyWord: Filter reviews by keyword (optional)
        numOfReviews: Number of reviews to fetch (optional)

    Example:
        >>> payload = AmazonReviewPayload(
        ...     url="https://amazon.com/dp/B123",
        ...     pastDays=30,
        ...     keyWord="quality",
        ...     numOfReviews=100
        ... )
    """

    pastDays: Optional[int] = None
    keyWord: Optional[str] = None
    numOfReviews: Optional[int] = None

    def __post_init__(self):
        """Validate Amazon review fields."""
        super().__post_init__()

        if "amazon.com" not in self.url.lower():
            raise ValueError(f"url must be an Amazon URL, got: {self.url}")

        if self.pastDays is not None and self.pastDays < 0:
            raise ValueError(f"pastDays must be non-negative, got {self.pastDays}")

        if self.numOfReviews is not None and self.numOfReviews < 0:
            raise ValueError(f"numOfReviews must be non-negative, got {self.numOfReviews}")


@dataclass
class AmazonSellerPayload(URLPayload):
    """
    Amazon seller scrape payload.

    Attributes:
        url: Amazon seller URL (required)

    Example:
        >>> payload = AmazonSellerPayload(
        ...     url="https://amazon.com/sp?seller=AXXXXXXXXXXX"
        ... )
    """

    def __post_init__(self):
        """Validate Amazon seller URL."""
        super().__post_init__()

        if "amazon.com" not in self.url.lower():
            raise ValueError(f"url must be an Amazon URL, got: {self.url}")


# ============================================================================
# LINKEDIN PAYLOADS
# ============================================================================


@dataclass
class LinkedInProfilePayload(URLPayload):
    """
    LinkedIn profile scrape payload.

    Attributes:
        url: LinkedIn profile URL (required)

    Example:
        >>> payload = LinkedInProfilePayload(
        ...     url="https://linkedin.com/in/johndoe"
        ... )
    """

    def __post_init__(self):
        """Validate LinkedIn URL."""
        super().__post_init__()

        if "linkedin.com" not in self.url.lower():
            raise ValueError(f"url must be a LinkedIn URL, got: {self.url}")


@dataclass
class LinkedInJobPayload(URLPayload):
    """
    LinkedIn job scrape payload.

    Attributes:
        url: LinkedIn job URL (required)

    Example:
        >>> payload = LinkedInJobPayload(
        ...     url="https://linkedin.com/jobs/view/123456789"
        ... )
    """

    def __post_init__(self):
        """Validate LinkedIn job URL."""
        super().__post_init__()

        if "linkedin.com" not in self.url.lower():
            raise ValueError(f"url must be a LinkedIn URL, got: {self.url}")


@dataclass
class LinkedInCompanyPayload(URLPayload):
    """
    LinkedIn company scrape payload.

    Attributes:
        url: LinkedIn company URL (required)

    Example:
        >>> payload = LinkedInCompanyPayload(
        ...     url="https://linkedin.com/company/brightdata"
        ... )
    """

    def __post_init__(self):
        """Validate LinkedIn company URL."""
        super().__post_init__()

        if "linkedin.com" not in self.url.lower():
            raise ValueError(f"url must be a LinkedIn URL, got: {self.url}")


@dataclass
class LinkedInPostPayload(URLPayload):
    """
    LinkedIn post scrape payload.

    Attributes:
        url: LinkedIn post URL (required)

    Example:
        >>> payload = LinkedInPostPayload(
        ...     url="https://linkedin.com/posts/activity-123456789"
        ... )
    """

    def __post_init__(self):
        """Validate LinkedIn post URL."""
        super().__post_init__()

        if "linkedin.com" not in self.url.lower():
            raise ValueError(f"url must be a LinkedIn URL, got: {self.url}")


@dataclass
class LinkedInProfileSearchPayload(BasePayload):
    """
    LinkedIn profile search payload.

    Attributes:
        firstName: First name to search (required)
        lastName: Last name to search (optional)
        title: Job title filter (optional)
        company: Company name filter (optional)
        location: Location filter (optional)
        max_results: Maximum results to return (optional)

    Example:
        >>> payload = LinkedInProfileSearchPayload(
        ...     firstName="John",
        ...     lastName="Doe",
        ...     company="Google"
        ... )
    """

    firstName: str
    lastName: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    max_results: Optional[int] = None

    def __post_init__(self):
        """Validate profile search fields."""
        if not self.firstName or not self.firstName.strip():
            raise ValueError("firstName is required")

        self.firstName = self.firstName.strip()

        if self.lastName:
            self.lastName = self.lastName.strip()

        if self.max_results is not None and self.max_results < 1:
            raise ValueError(f"max_results must be positive, got {self.max_results}")


@dataclass
class LinkedInJobSearchPayload(BasePayload):
    """
    LinkedIn job search payload.

    Attributes:
        url: LinkedIn job search URL (optional)
        keyword: Job keyword(s) (optional)
        location: Location filter (optional)
        country: Country code - 2-letter format (optional)
        timeRange: Time range filter (optional)
        jobType: Job type filter (e.g., "full-time", "contract") (optional)
        experienceLevel: Experience level (e.g., "entry", "mid", "senior") (optional)
        remote: Remote jobs only (optional)
        company: Company name filter (optional)
        locationRadius: Location radius filter (optional)

    Example:
        >>> payload = LinkedInJobSearchPayload(
        ...     keyword="python developer",
        ...     location="New York",
        ...     remote=True,
        ...     experienceLevel="mid"
        ... )
    """

    url: Optional[str] = None
    keyword: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    timeRange: Optional[str] = None
    jobType: Optional[str] = None
    experienceLevel: Optional[str] = None
    remote: Optional[bool] = None
    company: Optional[str] = None
    locationRadius: Optional[str] = None

    def __post_init__(self):
        """Validate job search fields."""
        # At least one search criteria required
        if not any([self.url, self.keyword, self.location, self.country, self.company]):
            raise ValueError(
                "At least one search parameter required "
                "(url, keyword, location, country, or company)"
            )

        # Validate country code format
        if self.country and len(self.country) != 2:
            raise ValueError(f"country must be 2-letter code, got: {self.country}")

    @property
    def is_remote_search(self) -> bool:
        """Check if searching for remote jobs."""
        if self.remote:
            return True
        if self.keyword and "remote" in self.keyword.lower():
            return True
        return False


@dataclass
class LinkedInPostSearchPayload(URLPayload):
    """
    LinkedIn post search payload.

    Attributes:
        profile_url: LinkedIn profile URL (required)
        start_date: Start date in yyyy-mm-dd format (optional)
        end_date: End date in yyyy-mm-dd format (optional)

    Example:
        >>> payload = LinkedInPostSearchPayload(
        ...     profile_url="https://linkedin.com/in/johndoe",
        ...     start_date="2025-01-01",
        ...     end_date="2025-12-31"
        ... )
    """

    start_date: Optional[str] = None
    end_date: Optional[str] = None

    def __post_init__(self):
        """Validate post search fields."""
        super().__post_init__()

        if "linkedin.com" not in self.url.lower():
            raise ValueError(f"profile_url must be a LinkedIn URL, got: {self.url}")

        # Validate date format if provided
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if self.start_date and not re.match(date_pattern, self.start_date):
            raise ValueError(f"start_date must be in yyyy-mm-dd format, got: {self.start_date}")

        if self.end_date and not re.match(date_pattern, self.end_date):
            raise ValueError(f"end_date must be in yyyy-mm-dd format, got: {self.end_date}")


# ============================================================================
# CHATGPT PAYLOADS
# ============================================================================


@dataclass
class ChatGPTPromptPayload(BasePayload):
    """
    ChatGPT prompt payload.

    Attributes:
        prompt: Prompt text to send to ChatGPT (required)
        country: Country code in 2-letter format (default: "US")
        web_search: Enable web search capability (default: False)
        additional_prompt: Secondary prompt for continued conversation (optional)

    Example:
        >>> payload = ChatGPTPromptPayload(
        ...     prompt="Explain Python async programming",
        ...     country="US",
        ...     web_search=True
        ... )
    """

    prompt: str
    country: str = "US"
    web_search: bool = False
    additional_prompt: Optional[str] = None

    def __post_init__(self):
        """Validate ChatGPT prompt fields."""
        if not self.prompt or not self.prompt.strip():
            raise ValueError("prompt is required")

        self.prompt = self.prompt.strip()

        # Validate country code
        if self.country and len(self.country) != 2:
            raise ValueError(f"country must be 2-letter code, got: {self.country}")

        self.country = self.country.upper()

        # Validate prompt length (reasonable limit)
        if len(self.prompt) > 10000:
            raise ValueError(f"prompt too long ({len(self.prompt)} chars), max 10000")

    @property
    def uses_web_search(self) -> bool:
        """Check if web search is enabled."""
        return self.web_search


# ============================================================================
# FACEBOOK PAYLOADS
# ============================================================================


@dataclass
class FacebookPostsProfilePayload(URLPayload):
    """
    Facebook posts by profile URL payload.

    Attributes:
        url: Facebook profile URL (required)
        num_of_posts: Number of posts to collect (optional)
        posts_to_not_include: Array of post IDs to exclude (optional)
        start_date: Start date in MM-DD-YYYY format (optional)
        end_date: End date in MM-DD-YYYY format (optional)

    Example:
        >>> payload = FacebookPostsProfilePayload(
        ...     url="https://facebook.com/profile",
        ...     num_of_posts=10,
        ...     start_date="01-01-2025"
        ... )
    """

    num_of_posts: Optional[int] = None
    posts_to_not_include: Optional[List[str]] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    def __post_init__(self):
        """Validate Facebook posts payload."""
        super().__post_init__()

        if "facebook.com" not in self.url.lower():
            raise ValueError(f"url must be a Facebook URL, got: {self.url}")

        if self.num_of_posts is not None and self.num_of_posts < 1:
            raise ValueError(f"num_of_posts must be positive, got {self.num_of_posts}")

        # Validate date format
        date_pattern = r"^\d{2}-\d{2}-\d{4}$"
        if self.start_date and not re.match(date_pattern, self.start_date):
            raise ValueError(f"start_date must be in MM-DD-YYYY format, got: {self.start_date}")

        if self.end_date and not re.match(date_pattern, self.end_date):
            raise ValueError(f"end_date must be in MM-DD-YYYY format, got: {self.end_date}")


@dataclass
class FacebookPostsGroupPayload(URLPayload):
    """
    Facebook posts by group URL payload.

    Attributes:
        url: Facebook group URL (required)
        num_of_posts: Number of posts to collect (optional)
        posts_to_not_include: Array of post IDs to exclude (optional)
        start_date: Start date in MM-DD-YYYY format (optional)
        end_date: End date in MM-DD-YYYY format (optional)

    Example:
        >>> payload = FacebookPostsGroupPayload(
        ...     url="https://facebook.com/groups/example",
        ...     num_of_posts=20
        ... )
    """

    num_of_posts: Optional[int] = None
    posts_to_not_include: Optional[List[str]] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    def __post_init__(self):
        """Validate Facebook group payload."""
        super().__post_init__()

        if "facebook.com" not in self.url.lower():
            raise ValueError(f"url must be a Facebook URL, got: {self.url}")

        if "/groups/" not in self.url.lower():
            raise ValueError(f"url must be a Facebook group URL, got: {self.url}")

        if self.num_of_posts is not None and self.num_of_posts < 1:
            raise ValueError(f"num_of_posts must be positive, got {self.num_of_posts}")


@dataclass
class FacebookPostPayload(URLPayload):
    """
    Facebook post by URL payload.

    Attributes:
        url: Facebook post URL (required)

    Example:
        >>> payload = FacebookPostPayload(
        ...     url="https://facebook.com/post/123456"
        ... )
    """

    def __post_init__(self):
        """Validate Facebook post URL."""
        super().__post_init__()

        if "facebook.com" not in self.url.lower():
            raise ValueError(f"url must be a Facebook URL, got: {self.url}")


@dataclass
class FacebookCommentsPayload(URLPayload):
    """
    Facebook comments by post URL payload.

    Attributes:
        url: Facebook post URL (required)
        num_of_comments: Number of comments to collect (optional)
        comments_to_not_include: Array of comment IDs to exclude (optional)
        start_date: Start date in MM-DD-YYYY format (optional)
        end_date: End date in MM-DD-YYYY format (optional)

    Example:
        >>> payload = FacebookCommentsPayload(
        ...     url="https://facebook.com/post/123456",
        ...     num_of_comments=100
        ... )
    """

    num_of_comments: Optional[int] = None
    comments_to_not_include: Optional[List[str]] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    def __post_init__(self):
        """Validate Facebook comments payload."""
        super().__post_init__()

        if "facebook.com" not in self.url.lower():
            raise ValueError(f"url must be a Facebook URL, got: {self.url}")

        if self.num_of_comments is not None and self.num_of_comments < 1:
            raise ValueError(f"num_of_comments must be positive, got {self.num_of_comments}")


@dataclass
class FacebookReelsPayload(URLPayload):
    """
    Facebook reels by profile URL payload.

    Attributes:
        url: Facebook profile URL (required)
        num_of_posts: Number of reels to collect (optional)
        posts_to_not_include: Array of reel IDs to exclude (optional)
        start_date: Start date filter (optional)
        end_date: End date filter (optional)

    Example:
        >>> payload = FacebookReelsPayload(
        ...     url="https://facebook.com/profile",
        ...     num_of_posts=50
        ... )
    """

    num_of_posts: Optional[int] = None
    posts_to_not_include: Optional[List[str]] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    def __post_init__(self):
        """Validate Facebook reels payload."""
        super().__post_init__()

        if "facebook.com" not in self.url.lower():
            raise ValueError(f"url must be a Facebook URL, got: {self.url}")

        if self.num_of_posts is not None and self.num_of_posts < 1:
            raise ValueError(f"num_of_posts must be positive, got {self.num_of_posts}")


# ============================================================================
# INSTAGRAM PAYLOADS
# ============================================================================


@dataclass
class InstagramProfilePayload(URLPayload):
    """
    Instagram profile by URL payload.

    Attributes:
        url: Instagram profile URL (required)

    Example:
        >>> payload = InstagramProfilePayload(
        ...     url="https://instagram.com/username"
        ... )
    """

    def __post_init__(self):
        """Validate Instagram URL."""
        super().__post_init__()

        if "instagram.com" not in self.url.lower():
            raise ValueError(f"url must be an Instagram URL, got: {self.url}")


@dataclass
class InstagramPostPayload(URLPayload):
    """
    Instagram post by URL payload.

    Attributes:
        url: Instagram post URL (required)

    Example:
        >>> payload = InstagramPostPayload(
        ...     url="https://instagram.com/p/ABC123"
        ... )
    """

    def __post_init__(self):
        """Validate Instagram post URL."""
        super().__post_init__()

        if "instagram.com" not in self.url.lower():
            raise ValueError(f"url must be an Instagram URL, got: {self.url}")

    @property
    def is_post(self) -> bool:
        """Check if URL is a post."""
        return "/p/" in self.url


@dataclass
class InstagramCommentPayload(URLPayload):
    """
    Instagram comments by post URL payload.

    Attributes:
        url: Instagram post URL (required)

    Example:
        >>> payload = InstagramCommentPayload(
        ...     url="https://instagram.com/p/ABC123"
        ... )
    """

    def __post_init__(self):
        """Validate Instagram comment URL."""
        super().__post_init__()

        if "instagram.com" not in self.url.lower():
            raise ValueError(f"url must be an Instagram URL, got: {self.url}")


@dataclass
class InstagramReelPayload(URLPayload):
    """
    Instagram reel by URL payload.

    Attributes:
        url: Instagram reel URL (required)

    Example:
        >>> payload = InstagramReelPayload(
        ...     url="https://instagram.com/reel/ABC123"
        ... )
    """

    def __post_init__(self):
        """Validate Instagram reel URL."""
        super().__post_init__()

        if "instagram.com" not in self.url.lower():
            raise ValueError(f"url must be an Instagram URL, got: {self.url}")

    @property
    def is_reel(self) -> bool:
        """Check if URL is a reel."""
        return "/reel/" in self.url


@dataclass
class InstagramPostsDiscoverPayload(URLPayload):
    """
    Instagram posts discovery by URL payload.

    Attributes:
        url: Instagram profile, reel, or search URL (required)
        num_of_posts: Number of posts to collect (optional)
        posts_to_not_include: Array of post IDs to exclude (optional)
        start_date: Start date in MM-DD-YYYY format (optional)
        end_date: End date in MM-DD-YYYY format (optional)
        post_type: Type of posts to collect (e.g., "post", "reel") (optional)

    Example:
        >>> payload = InstagramPostsDiscoverPayload(
        ...     url="https://instagram.com/username",
        ...     num_of_posts=10,
        ...     post_type="reel"
        ... )
    """

    num_of_posts: Optional[int] = None
    posts_to_not_include: Optional[List[str]] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    post_type: Optional[str] = None

    def __post_init__(self):
        """Validate Instagram posts discovery payload."""
        super().__post_init__()

        if "instagram.com" not in self.url.lower():
            raise ValueError(f"url must be an Instagram URL, got: {self.url}")

        if self.num_of_posts is not None and self.num_of_posts < 1:
            raise ValueError(f"num_of_posts must be positive, got {self.num_of_posts}")


@dataclass
class InstagramReelsDiscoverPayload(URLPayload):
    """
    Instagram reels discovery by URL payload.

    Attributes:
        url: Instagram profile or direct search URL (required)
        num_of_posts: Number of reels to collect (optional)
        posts_to_not_include: Array of post IDs to exclude (optional)
        start_date: Start date in MM-DD-YYYY format (optional)
        end_date: End date in MM-DD-YYYY format (optional)

    Example:
        >>> payload = InstagramReelsDiscoverPayload(
        ...     url="https://instagram.com/username",
        ...     num_of_posts=50
        ... )
    """

    num_of_posts: Optional[int] = None
    posts_to_not_include: Optional[List[str]] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    def __post_init__(self):
        """Validate Instagram reels discovery payload."""
        super().__post_init__()

        if "instagram.com" not in self.url.lower():
            raise ValueError(f"url must be an Instagram URL, got: {self.url}")

        if self.num_of_posts is not None and self.num_of_posts < 1:
            raise ValueError(f"num_of_posts must be positive, got {self.num_of_posts}")


# ============================================================================
# DATASET API PAYLOADS
# ============================================================================


@dataclass
class DatasetTriggerPayload(BasePayload):
    """
    Generic dataset trigger payload.

    This is a flexible payload for triggering any dataset collection.

    Attributes:
        url: URL to scrape (optional)
        keyword: Search keyword (optional)
        location: Location filter (optional)
        country: Country filter (optional)
        max_results: Maximum results (optional)

    Example:
        >>> payload = DatasetTriggerPayload(
        ...     url="https://example.com",
        ...     max_results=100
        ... )
    """

    url: Optional[str] = None
    keyword: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    max_results: Optional[int] = None

    def __post_init__(self):
        """Validate dataset trigger fields."""
        if self.max_results is not None and self.max_results < 1:
            raise ValueError(f"max_results must be positive, got {self.max_results}")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Base classes
    "BasePayload",
    "URLPayload",
    # Amazon
    "AmazonProductPayload",
    "AmazonReviewPayload",
    "AmazonSellerPayload",
    # LinkedIn
    "LinkedInProfilePayload",
    "LinkedInJobPayload",
    "LinkedInCompanyPayload",
    "LinkedInPostPayload",
    "LinkedInProfileSearchPayload",
    "LinkedInJobSearchPayload",
    "LinkedInPostSearchPayload",
    # ChatGPT
    "ChatGPTPromptPayload",
    # Facebook
    "FacebookPostsProfilePayload",
    "FacebookPostsGroupPayload",
    "FacebookPostPayload",
    "FacebookCommentsPayload",
    "FacebookReelsPayload",
    # Instagram
    "InstagramProfilePayload",
    "InstagramPostPayload",
    "InstagramCommentPayload",
    "InstagramReelPayload",
    "InstagramPostsDiscoverPayload",
    "InstagramReelsDiscoverPayload",
    # Dataset
    "DatasetTriggerPayload",
]
