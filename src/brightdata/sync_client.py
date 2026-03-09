"""
Synchronous client adapter for Bright Data SDK.

Provides sync interface using persistent event loop for optimal performance.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

from .client import BrightDataClient
from .browser.service import BrowserService
from .models import ScrapeResult, SearchResult
from .types import AccountInfo


class SyncBrightDataClient:
    """
    Synchronous adapter for BrightDataClient.

    Uses a persistent event loop for all operations, providing better
    performance than repeated asyncio.run() calls.

    WARNING: This client is NOT thread-safe. For multi-threaded usage,
    create a separate SyncBrightDataClient per thread.

    Example:
        >>> with SyncBrightDataClient(token="...") as client:
        ...     zones = client.list_zones()
        ...     result = client.scrape.amazon.products(url)
    """

    def __init__(
        self,
        token: Optional[str] = None,
        timeout: int = 30,
        web_unlocker_zone: Optional[str] = None,
        serp_zone: Optional[str] = None,
        browser_username: Optional[str] = None,
        browser_password: Optional[str] = None,
        browser_host: Optional[str] = None,
        browser_port: Optional[int] = None,
        auto_create_zones: bool = True,
        validate_token: bool = False,
        rate_limit: Optional[float] = None,
        rate_period: float = 1.0,
    ):
        """
        Initialize sync client.

        Args:
            token: Bright Data API token (or set BRIGHTDATA_API_TOKEN env var)
            timeout: Default request timeout in seconds
            web_unlocker_zone: Zone name for Web Unlocker API
            serp_zone: Zone name for SERP API
            browser_username: Browser API username (or set BRIGHTDATA_BROWSERAPI_USERNAME env var)
            browser_password: Browser API password (or set BRIGHTDATA_BROWSERAPI_PASSWORD env var)
            browser_host: Browser API host (default: "brd.superproxy.io")
            browser_port: Browser API port (default: 9222)
            auto_create_zones: Automatically create required zones if missing
            validate_token: Validate token on initialization
            rate_limit: Rate limit (requests per period)
            rate_period: Rate limit period in seconds
        """
        # Check if we're inside an async context
        loop_running = True
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop_running = False

        if loop_running:
            raise RuntimeError(
                "SyncBrightDataClient cannot be used inside an async context. "
                "Use BrightDataClient with async/await instead."
            )

        self._async_client = BrightDataClient(
            token=token,
            timeout=timeout,
            web_unlocker_zone=web_unlocker_zone,
            serp_zone=serp_zone,
            browser_username=browser_username,
            browser_password=browser_password,
            browser_host=browser_host,
            browser_port=browser_port,
            auto_create_zones=auto_create_zones,
            validate_token=False,  # Will validate during __enter__
            rate_limit=rate_limit,
            rate_period=rate_period,
        )
        self._validate_token = validate_token
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._scrape: Optional["SyncScrapeService"] = None
        self._search: Optional["SyncSearchService"] = None
        self._crawler: Optional["SyncCrawlerService"] = None
        self._scraper_studio: Optional["SyncScraperStudioService"] = None

    def __enter__(self):
        """Initialize persistent event loop and async client."""
        # Create persistent loop
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # Initialize async client
        self._loop.run_until_complete(self._async_client.__aenter__())

        # Validate token if requested
        if self._validate_token:
            is_valid = self._loop.run_until_complete(self._async_client.test_connection())
            if not is_valid:
                self.__exit__(None, None, None)
                from .exceptions import AuthenticationError

                raise AuthenticationError("Token validation failed. Token appears to be invalid.")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async client and event loop."""
        if self._loop is None:
            return

        try:
            # Cleanup async client
            self._loop.run_until_complete(self._async_client.__aexit__(exc_type, exc_val, exc_tb))

            # Give the event loop a moment to process any remaining callbacks
            # This helps prevent "Unclosed client session" warnings
            self._loop.run_until_complete(asyncio.sleep(0.05))

            # Cancel any remaining tasks
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()

            # Let cancellations propagate
            if pending:
                self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            logger.debug("Error during SyncBrightDataClient cleanup", exc_info=True)
        finally:
            # Close the loop
            try:
                self._loop.close()
            except Exception:
                logger.debug("Error closing event loop", exc_info=True)
            self._loop = None

    def _run(self, coro):
        """Run coroutine in persistent loop."""
        if self._loop is None:
            raise RuntimeError(
                "SyncBrightDataClient not initialized. "
                "Use: with SyncBrightDataClient() as client: ..."
            )
        return self._loop.run_until_complete(coro)

    # ========================================
    # Utility Methods
    # ========================================

    def list_zones(self) -> List[Dict[str, Any]]:
        """List all active zones."""
        return self._run(self._async_client.list_zones())

    def delete_zone(self, zone_name: str) -> None:
        """Delete a zone."""
        return self._run(self._async_client.delete_zone(zone_name))

    def get_account_info(self, refresh: bool = False) -> AccountInfo:
        """Get account information."""
        return self._run(self._async_client.get_account_info(refresh=refresh))

    def test_connection(self) -> bool:
        """Test API connection."""
        return self._run(self._async_client.test_connection())

    def scrape_url(self, url, **kwargs):
        """Scrape URL using Web Unlocker."""
        return self._run(self._async_client.scrape_url(url, **kwargs))

    # ========================================
    # Service Properties
    # ========================================

    @property
    def browser(self) -> BrowserService:
        """Access Browser API service (builds CDP WebSocket URLs)."""
        return self._async_client.browser

    @property
    def scrape(self) -> "SyncScrapeService":
        """Access scraping services (sync)."""
        if self._scrape is None:
            self._scrape = SyncScrapeService(self._async_client.scrape, self._loop)
        return self._scrape

    @property
    def search(self) -> "SyncSearchService":
        """Access search services (sync)."""
        if self._search is None:
            self._search = SyncSearchService(self._async_client.search, self._loop)
        return self._search

    @property
    def crawler(self) -> "SyncCrawlerService":
        """Access crawler services (sync)."""
        if self._crawler is None:
            self._crawler = SyncCrawlerService(self._async_client.crawler, self._loop)
        return self._crawler

    @property
    def scraper_studio(self) -> "SyncScraperStudioService":
        """Access Scraper Studio services (sync)."""
        if self._scraper_studio is None:
            self._scraper_studio = SyncScraperStudioService(
                self._async_client.scraper_studio, self._loop
            )
        return self._scraper_studio

    @property
    def token(self) -> str:
        """Get API token."""
        return self._async_client.token

    def __repr__(self) -> str:
        """String representation."""
        token_preview = f"{self.token[:10]}...{self.token[-5:]}" if self.token else "None"
        status = "Initialized" if self._loop else "Not initialized"
        return f"<SyncBrightDataClient token={token_preview} status='{status}'>"


# ============================================================================
# SYNC SCRAPE SERVICE
# ============================================================================


class SyncScrapeService:
    """Sync wrapper for ScrapeService."""

    def __init__(self, async_service, loop):
        self._async = async_service
        self._loop = loop
        self._amazon = None
        self._linkedin = None
        self._instagram = None
        self._facebook = None
        self._chatgpt = None

    @property
    def amazon(self) -> "SyncAmazonScraper":
        if self._amazon is None:
            self._amazon = SyncAmazonScraper(self._async.amazon, self._loop)
        return self._amazon

    @property
    def linkedin(self) -> "SyncLinkedInScraper":
        if self._linkedin is None:
            self._linkedin = SyncLinkedInScraper(self._async.linkedin, self._loop)
        return self._linkedin

    @property
    def instagram(self) -> "SyncInstagramScraper":
        if self._instagram is None:
            self._instagram = SyncInstagramScraper(self._async.instagram, self._loop)
        return self._instagram

    @property
    def facebook(self) -> "SyncFacebookScraper":
        if self._facebook is None:
            self._facebook = SyncFacebookScraper(self._async.facebook, self._loop)
        return self._facebook

    @property
    def chatgpt(self) -> "SyncChatGPTScraper":
        if self._chatgpt is None:
            self._chatgpt = SyncChatGPTScraper(self._async.chatgpt, self._loop)
        return self._chatgpt


class SyncAmazonScraper:
    """Sync wrapper for AmazonScraper - COMPLETE with all methods."""

    def __init__(self, async_scraper, loop):
        self._async = async_scraper
        self._loop = loop

    # Products
    def products(self, url, **kwargs) -> ScrapeResult:
        """Scrape Amazon product details."""
        return self._loop.run_until_complete(self._async.products(url, **kwargs))

    def products_trigger(self, url, **kwargs):
        """Trigger Amazon products scrape."""
        return self._loop.run_until_complete(self._async.products_trigger(url, **kwargs))

    def products_status(self, snapshot_id):
        """Check Amazon products scrape status."""
        return self._loop.run_until_complete(self._async.products_status(snapshot_id))

    def products_fetch(self, snapshot_id):
        """Fetch Amazon products scrape results."""
        return self._loop.run_until_complete(self._async.products_fetch(snapshot_id))

    # Reviews
    def reviews(self, url, **kwargs) -> ScrapeResult:
        """Scrape Amazon reviews."""
        return self._loop.run_until_complete(self._async.reviews(url, **kwargs))

    def reviews_trigger(self, url, **kwargs):
        """Trigger Amazon reviews scrape."""
        return self._loop.run_until_complete(self._async.reviews_trigger(url, **kwargs))

    def reviews_status(self, snapshot_id):
        """Check Amazon reviews scrape status."""
        return self._loop.run_until_complete(self._async.reviews_status(snapshot_id))

    def reviews_fetch(self, snapshot_id):
        """Fetch Amazon reviews scrape results."""
        return self._loop.run_until_complete(self._async.reviews_fetch(snapshot_id))

    # Sellers
    def sellers(self, url, **kwargs) -> ScrapeResult:
        """Scrape Amazon sellers."""
        return self._loop.run_until_complete(self._async.sellers(url, **kwargs))

    def sellers_trigger(self, url, **kwargs):
        """Trigger Amazon sellers scrape."""
        return self._loop.run_until_complete(self._async.sellers_trigger(url, **kwargs))

    def sellers_status(self, snapshot_id):
        """Check Amazon sellers scrape status."""
        return self._loop.run_until_complete(self._async.sellers_status(snapshot_id))

    def sellers_fetch(self, snapshot_id):
        """Fetch Amazon sellers scrape results."""
        return self._loop.run_until_complete(self._async.sellers_fetch(snapshot_id))


class SyncLinkedInScraper:
    """Sync wrapper for LinkedInScraper - COMPLETE with all methods."""

    def __init__(self, async_scraper, loop):
        self._async = async_scraper
        self._loop = loop

    # Posts - Call async methods (posts) not sync wrappers (posts_sync)
    # because sync wrappers use asyncio.run() which conflicts with our persistent loop
    def posts(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts(url, **kwargs))

    def posts_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts_trigger(url, **kwargs))

    def posts_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_status(snapshot_id))

    def posts_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_fetch(snapshot_id))

    # Jobs
    def jobs(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.jobs(url, **kwargs))

    def jobs_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.jobs_trigger(url, **kwargs))

    def jobs_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.jobs_status(snapshot_id))

    def jobs_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.jobs_fetch(snapshot_id))

    # Profiles
    def profiles(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.profiles(url, **kwargs))

    def profiles_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.profiles_trigger(url, **kwargs))

    def profiles_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.profiles_status(snapshot_id))

    def profiles_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.profiles_fetch(snapshot_id))

    # Companies
    def companies(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.companies(url, **kwargs))

    def companies_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.companies_trigger(url, **kwargs))

    def companies_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.companies_status(snapshot_id))

    def companies_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.companies_fetch(snapshot_id))


class SyncInstagramScraper:
    """Sync wrapper for InstagramScraper - COMPLETE with all methods."""

    def __init__(self, async_scraper, loop):
        self._async = async_scraper
        self._loop = loop

    # Profiles - NOTE: Must call async methods (not _sync wrappers) because they use asyncio.run()
    def profiles(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.profiles(url, **kwargs))

    def profiles_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.profiles_trigger(url, **kwargs))

    def profiles_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.profiles_status(snapshot_id))

    def profiles_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.profiles_fetch(snapshot_id))

    # Posts
    def posts(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts(url, **kwargs))

    def posts_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts_trigger(url, **kwargs))

    def posts_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_status(snapshot_id))

    def posts_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_fetch(snapshot_id))

    # Comments
    def comments(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.comments(url, **kwargs))

    def comments_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.comments_trigger(url, **kwargs))

    def comments_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.comments_status(snapshot_id))

    def comments_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.comments_fetch(snapshot_id))

    # Reels
    def reels(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.reels(url, **kwargs))

    def reels_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.reels_trigger(url, **kwargs))

    def reels_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.reels_status(snapshot_id))

    def reels_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.reels_fetch(snapshot_id))


class SyncFacebookScraper:
    """Sync wrapper for FacebookScraper - COMPLETE with all methods."""

    def __init__(self, async_scraper, loop):
        self._async = async_scraper
        self._loop = loop

    # Posts by profile - NOTE: Must call async methods (not _sync wrappers) because they use asyncio.run()
    def posts_by_profile(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts_by_profile(url, **kwargs))

    def posts_by_profile_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts_by_profile_trigger(url, **kwargs))

    def posts_by_profile_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_by_profile_status(snapshot_id))

    def posts_by_profile_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_by_profile_fetch(snapshot_id))

    # Posts by group
    def posts_by_group(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts_by_group(url, **kwargs))

    def posts_by_group_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts_by_group_trigger(url, **kwargs))

    def posts_by_group_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_by_group_status(snapshot_id))

    def posts_by_group_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_by_group_fetch(snapshot_id))

    # Posts by URL
    def posts_by_url(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts_by_url(url, **kwargs))

    def posts_by_url_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts_by_url_trigger(url, **kwargs))

    def posts_by_url_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_by_url_status(snapshot_id))

    def posts_by_url_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.posts_by_url_fetch(snapshot_id))

    # Comments
    def comments(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.comments(url, **kwargs))

    def comments_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.comments_trigger(url, **kwargs))

    def comments_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.comments_status(snapshot_id))

    def comments_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.comments_fetch(snapshot_id))

    # Reels
    def reels(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.reels(url, **kwargs))

    def reels_trigger(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.reels_trigger(url, **kwargs))

    def reels_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.reels_status(snapshot_id))

    def reels_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.reels_fetch(snapshot_id))


class SyncChatGPTScraper:
    """Sync wrapper for ChatGPTScraper - COMPLETE with all methods."""

    def __init__(self, async_scraper, loop):
        self._async = async_scraper
        self._loop = loop

    # Prompt - Call async methods (prompt) not sync wrappers (prompt_sync)
    # because sync wrappers use asyncio.run() which conflicts with our persistent loop
    def prompt(self, prompt_text, **kwargs):
        return self._loop.run_until_complete(self._async.prompt(prompt_text, **kwargs))

    def prompt_trigger(self, prompt_text, **kwargs):
        return self._loop.run_until_complete(self._async.prompt_trigger(prompt_text, **kwargs))

    def prompt_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.prompt_status(snapshot_id))

    def prompt_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.prompt_fetch(snapshot_id))

    # Prompts (batch)
    def prompts(self, prompts, **kwargs):
        return self._loop.run_until_complete(self._async.prompts(prompts, **kwargs))

    def prompts_trigger(self, prompts, **kwargs):
        return self._loop.run_until_complete(self._async.prompts_trigger(prompts, **kwargs))

    def prompts_status(self, snapshot_id):
        return self._loop.run_until_complete(self._async.prompts_status(snapshot_id))

    def prompts_fetch(self, snapshot_id):
        return self._loop.run_until_complete(self._async.prompts_fetch(snapshot_id))


# ============================================================================
# SYNC SEARCH SERVICE
# ============================================================================


class SyncSearchService:
    """Sync wrapper for SearchService - COMPLETE."""

    def __init__(self, async_service, loop):
        self._async = async_service
        self._loop = loop
        self._amazon = None
        self._linkedin = None
        self._instagram = None

    def google(self, query, **kwargs) -> SearchResult:
        """Search Google."""
        return self._loop.run_until_complete(self._async.google(query, **kwargs))

    def bing(self, query, **kwargs) -> SearchResult:
        """Search Bing."""
        return self._loop.run_until_complete(self._async.bing(query, **kwargs))

    def yandex(self, query, **kwargs) -> SearchResult:
        """Search Yandex."""
        return self._loop.run_until_complete(self._async.yandex(query, **kwargs))

    @property
    def amazon(self) -> "SyncAmazonSearchScraper":
        """Amazon search service."""
        if self._amazon is None:
            self._amazon = SyncAmazonSearchScraper(self._async.amazon, self._loop)
        return self._amazon

    @property
    def linkedin(self) -> "SyncLinkedInSearchScraper":
        """LinkedIn search service."""
        if self._linkedin is None:
            self._linkedin = SyncLinkedInSearchScraper(self._async.linkedin, self._loop)
        return self._linkedin

    @property
    def instagram(self) -> "SyncInstagramSearchScraper":
        """Instagram search service."""
        if self._instagram is None:
            self._instagram = SyncInstagramSearchScraper(self._async.instagram, self._loop)
        return self._instagram

    @property
    def chatGPT(self) -> "SyncChatGPTSearchService":
        """ChatGPT search service."""
        return SyncChatGPTSearchService(self._async.chatGPT, self._loop)


class SyncAmazonSearchScraper:
    """Sync wrapper for AmazonSearchScraper."""

    def __init__(self, async_scraper, loop):
        self._async = async_scraper
        self._loop = loop

    def products(self, keyword=None, **kwargs):
        return self._loop.run_until_complete(self._async.products(keyword=keyword, **kwargs))


class SyncLinkedInSearchScraper:
    """Sync wrapper for LinkedInSearchScraper."""

    def __init__(self, async_scraper, loop):
        self._async = async_scraper
        self._loop = loop

    def posts(self, profile_url, **kwargs):
        return self._loop.run_until_complete(self._async.posts(profile_url, **kwargs))

    def profiles(self, **kwargs):
        return self._loop.run_until_complete(self._async.profiles(**kwargs))

    def jobs(self, **kwargs):
        return self._loop.run_until_complete(self._async.jobs(**kwargs))


class SyncInstagramSearchScraper:
    """Sync wrapper for InstagramSearchScraper."""

    def __init__(self, async_scraper, loop):
        self._async = async_scraper
        self._loop = loop

    def posts(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.posts(url, **kwargs))

    def reels(self, url, **kwargs):
        return self._loop.run_until_complete(self._async.reels(url, **kwargs))


class SyncChatGPTSearchService:
    """Sync wrapper for ChatGPTSearchService."""

    def __init__(self, async_service, loop):
        self._async = async_service
        self._loop = loop

    def chatGPT(self, prompt, **kwargs):
        """Send prompt(s) to ChatGPT via search service."""
        return self._loop.run_until_complete(self._async.chatGPT(prompt, **kwargs))


# ============================================================================
# SYNC CRAWLER SERVICE
# ============================================================================


class SyncCrawlerService:
    """Sync wrapper for CrawlerService."""

    def __init__(self, async_service, loop):
        self._async = async_service
        self._loop = loop

    def crawl(self, url, **kwargs):
        """Crawl a URL."""
        return self._loop.run_until_complete(self._async.crawl(url, **kwargs))

    def scrape(self, url, **kwargs):
        """Scrape a URL."""
        return self._loop.run_until_complete(self._async.scrape(url, **kwargs))


# ============================================================================
# SYNC SCRAPER STUDIO SERVICE
# ============================================================================


class SyncScraperStudioService:
    """Sync wrapper for ScraperStudioService."""

    def __init__(self, async_service, loop):
        self._async = async_service
        self._loop = loop

    def run(self, collector, input, timeout=180, poll_interval=10):
        """Trigger scrape and wait for results."""
        return self._loop.run_until_complete(
            self._async.run(collector, input, timeout=timeout, poll_interval=poll_interval)
        )

    def trigger(self, collector, input):
        """Trigger scrape, return job object."""
        return self._loop.run_until_complete(self._async.trigger(collector, input))

    def status(self, job_id):
        """Check job status."""
        return self._loop.run_until_complete(self._async.status(job_id))

    def fetch(self, response_id):
        """Fetch results."""
        return self._loop.run_until_complete(self._async.fetch(response_id))
