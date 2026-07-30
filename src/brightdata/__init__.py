"""Bright Data Python SDK - Modern async-first SDK for Bright Data APIs."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("brightdata-sdk")
except PackageNotFoundError:
    # Package not installed (development mode without pip install -e)
    __version__ = "0.0.0.dev"

# Export main client (async)
from .browser.service import BrowserService
from .client import BrightDataClient
from .core.zone_manager import ZoneManager

# Export Discover API models
from .discover.models import DiscoverJob, DiscoverResult, DiscoverSnapshot

# Export exceptions
from .exceptions import (
    APIError,
    AuthenticationError,
    BrightDataError,
    NetworkError,
    SSLError,
    ValidationError,
    ZoneError,
)

# Export result models
from .models import (
    BaseResult,
    CrawlResult,
    Result,
    ScrapeResult,
    SearchResult,
)

# Export payload models (dataclasses)
from .payloads import (
    # Amazon
    AmazonProductPayload,
    AmazonReviewPayload,
    AmazonSellerPayload,
    # Base
    BasePayload,
    # ChatGPT
    ChatGPTPromptPayload,
    FacebookCommentsPayload,
    FacebookPostPayload,
    FacebookPostsGroupPayload,
    # Facebook
    FacebookPostsProfilePayload,
    FacebookReelsPayload,
    InstagramCommentPayload,
    InstagramPostPayload,
    InstagramPostsDiscoverPayload,
    # Instagram
    InstagramProfilePayload,
    InstagramReelPayload,
    InstagramReelsDiscoverPayload,
    LinkedInCompanyPayload,
    LinkedInJobPayload,
    LinkedInJobSearchPayload,
    LinkedInPostPayload,
    LinkedInPostSearchPayload,
    # LinkedIn
    LinkedInProfilePayload,
    LinkedInProfileSearchPayload,
    URLPayload,
)

# Export Scraper Studio models
from .scraper_studio.models import JobStatus, ScraperStudioJob
from .scraper_studio.service import ScraperStudioService

# Export job model for manual trigger/poll/fetch
from .scrapers.job import ScrapeJob

# Export sync client adapter
from .sync_client import SyncBrightDataClient

# Export services for advanced usage
from .web_unlocker.service import WebUnlockerService

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
    "ZoneError",
    "NetworkError",
    "SSLError",
    # Scraper Studio
    "ScraperStudioJob",
    "JobStatus",
    "ScraperStudioService",
    # Discover API
    "DiscoverResult",
    "DiscoverJob",
    "DiscoverSnapshot",
    # Services
    "WebUnlockerService",
    "BrowserService",
    "ZoneManager",
]
