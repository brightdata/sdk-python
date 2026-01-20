"""Bright Data Python SDK - Modern async-first SDK for Bright Data APIs."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("brightdata-sdk")
except PackageNotFoundError:
    # Package not installed (development mode without pip install -e)
    __version__ = "0.0.0.dev"

# Export main client (async)
from .client import BrightDataClient

# Export sync client adapter
from .sync_client import SyncBrightDataClient

# Export result models
from .models import (
    BaseResult,
    ScrapeResult,
    SearchResult,
    CrawlResult,
    Result,
)

# Export job model for manual trigger/poll/fetch
from .scrapers.job import ScrapeJob

# Export payload models (dataclasses)
from .payloads import (
    # Base
    BasePayload,
    URLPayload,
    # Amazon
    AmazonProductPayload,
    AmazonReviewPayload,
    AmazonSellerPayload,
    # LinkedIn
    LinkedInProfilePayload,
    LinkedInJobPayload,
    LinkedInCompanyPayload,
    LinkedInPostPayload,
    LinkedInProfileSearchPayload,
    LinkedInJobSearchPayload,
    LinkedInPostSearchPayload,
    # ChatGPT
    ChatGPTPromptPayload,
    # Facebook
    FacebookPostsProfilePayload,
    FacebookPostsGroupPayload,
    FacebookPostPayload,
    FacebookCommentsPayload,
    FacebookReelsPayload,
    # Instagram
    InstagramProfilePayload,
    InstagramPostPayload,
    InstagramCommentPayload,
    InstagramReelPayload,
    InstagramPostsDiscoverPayload,
    InstagramReelsDiscoverPayload,
)

# Export exceptions
from .exceptions import (
    BrightDataError,
    ValidationError,
    AuthenticationError,
    APIError,
    TimeoutError,
    ZoneError,
    NetworkError,
    SSLError,
)

# Export services for advanced usage
from .api.web_unlocker import WebUnlockerService
from .core.zone_manager import ZoneManager

__all__ = [
    "__version__",
    # Main client (async)
    "BrightDataClient",
    # Sync client adapter
    "SyncBrightDataClient",
    # Result models
    "BaseResult",
    "ScrapeResult",
    "SearchResult",
    "CrawlResult",
    "Result",
    # Job model for manual control
    "ScrapeJob",
    # Payload models (dataclasses)
    "BasePayload",
    "URLPayload",
    "AmazonProductPayload",
    "AmazonReviewPayload",
    "AmazonSellerPayload",
    "LinkedInProfilePayload",
    "LinkedInJobPayload",
    "LinkedInCompanyPayload",
    "LinkedInPostPayload",
    "LinkedInProfileSearchPayload",
    "LinkedInJobSearchPayload",
    "LinkedInPostSearchPayload",
    "ChatGPTPromptPayload",
    "FacebookPostsProfilePayload",
    "FacebookPostsGroupPayload",
    "FacebookPostPayload",
    "FacebookCommentsPayload",
    "FacebookReelsPayload",
    "InstagramProfilePayload",
    "InstagramPostPayload",
    "InstagramCommentPayload",
    "InstagramReelPayload",
    "InstagramPostsDiscoverPayload",
    "InstagramReelsDiscoverPayload",
    # Exceptions
    "BrightDataError",
    "ValidationError",
    "AuthenticationError",
    "APIError",
    "TimeoutError",
    "ZoneError",
    "NetworkError",
    "SSLError",
    # Services
    "WebUnlockerService",
    "ZoneManager",
]
