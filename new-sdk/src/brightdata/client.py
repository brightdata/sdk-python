"""
Main Bright Data SDK client - Single entry point for all services.

Philosophy:
- Client is the single source of truth for configuration
- Authentication should "just work" with minimal setup
- Fail fast and clearly when credentials are missing/invalid
- Follow principle of least surprise - common patterns from other SDKs
"""

import os
import asyncio
from typing import Optional, Dict, Any, Union, List
from datetime import datetime, timezone

from .core.engine import AsyncEngine
from .api.web_unlocker import WebUnlockerService
from .models import ScrapeResult, SearchResult
from .types import AccountInfo, URLParam, OptionalURLParam
from .exceptions import (
    ValidationError,
    AuthenticationError,
    APIError,
    BrightDataError
)


class BrightDataClient:
    """
    Main entry point for Bright Data SDK.
    
    Single, unified interface for all BrightData services including scraping,
    search, and crawling capabilities. Handles authentication, configuration,
    and provides hierarchical access to specialized services.
    
    Examples:
        >>> # Simple instantiation - auto-loads from environment
        >>> client = BrightDataClient()
        >>> 
        >>> # Explicit token
        >>> client = BrightDataClient(token="your_api_token")
        >>> 
        >>> # Service access (planned)
        >>> client.scrape.amazon.products(...)
        >>> client.search.linkedin.jobs(...)
        >>> client.crawler.discover(...)
        >>> 
        >>> # Connection verification
        >>> is_valid = await client.test_connection()
        >>> info = await client.get_account_info()
    """
    
    # Default configuration
    DEFAULT_TIMEOUT = 30
    DEFAULT_WEB_UNLOCKER_ZONE = "sdk_unlocker"
    DEFAULT_SERP_ZONE = "sdk_serp"
    DEFAULT_BROWSER_ZONE = "sdk_browser"
    
    # Environment variable names (multiple options for token)
    TOKEN_ENV_VARS = [
        "BRIGHTDATA_API_TOKEN",
        "BRIGHTDATA_API_KEY",
        "BRIGHTDATA_TOKEN",
        "BD_API_TOKEN",
    ]
    
    def __init__(
        self,
        token: Optional[str] = None,
        customer_id: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        web_unlocker_zone: Optional[str] = None,
        serp_zone: Optional[str] = None,
        browser_zone: Optional[str] = None,
        auto_create_zones: bool = False,
        validate_token: bool = False,
    ):
        """
        Initialize Bright Data client.
        
        Authentication happens automatically from environment variables if not provided.
        Supports multiple environment variable names for flexibility.
        
        Args:
            token: API token. If None, loads from environment variables in order:
                   BRIGHTDATA_API_TOKEN, BRIGHTDATA_API_KEY, BRIGHTDATA_TOKEN, BD_API_TOKEN
            customer_id: Customer ID (optional, can also be set via BRIGHTDATA_CUSTOMER_ID)
            timeout: Default timeout in seconds for all requests (default: 30)
            web_unlocker_zone: Zone name for web unlocker (default: "sdk_unlocker")
            serp_zone: Zone name for SERP API (default: "sdk_serp")
            browser_zone: Zone name for browser API (default: "sdk_browser")
            auto_create_zones: Automatically create zones if they don't exist (default: False)
            validate_token: Validate token by testing connection on init (default: False)
        
        Raises:
            ValidationError: If token is not provided and not found in environment
            AuthenticationError: If validate_token=True and token is invalid
        
        Example:
            >>> # Auto-load from environment
            >>> client = BrightDataClient()
            >>> 
            >>> # Explicit configuration
            >>> client = BrightDataClient(
            ...     token="your_token",
            ...     timeout=60,
            ...     validate_token=True
            ... )
        """
        # Token management - try multiple environment variables
        self.token = self._load_token(token)
        
        # Customer ID (optional)
        self.customer_id = customer_id or os.getenv("BRIGHTDATA_CUSTOMER_ID")
        
        # Configuration
        self.timeout = timeout
        self.web_unlocker_zone = web_unlocker_zone or self.DEFAULT_WEB_UNLOCKER_ZONE
        self.serp_zone = serp_zone or self.DEFAULT_SERP_ZONE
        self.browser_zone = browser_zone or self.DEFAULT_BROWSER_ZONE
        self.auto_create_zones = auto_create_zones
        
        # Initialize core engine
        self.engine = AsyncEngine(self.token, timeout=timeout)
        
        # Service instances (lazy initialization)
        self._scrape_service: Optional['ScrapeService'] = None
        self._search_service: Optional['SearchService'] = None
        self._crawler_service: Optional['CrawlerService'] = None
        self._web_unlocker_service: Optional[WebUnlockerService] = None
    
        # Connection state
        self._is_connected = False
        self._account_info: Optional[Dict[str, Any]] = None
        
        # Validate token if requested
        if validate_token:
            self._validate_token_sync()
    
    def _load_token(self, token: Optional[str]) -> str:
        """
        Load token from parameter or environment variables.
        
        Tries multiple environment variable names for maximum compatibility.
        Fails fast with clear error message if no token found.
        
        Args:
            token: Explicit token (takes precedence)
        
        Returns:
            Valid token string
        
        Raises:
            ValidationError: If no token found
        """
        if token:
            if not isinstance(token, str) or len(token.strip()) < 10:
                raise ValidationError(
                    f"Invalid token format. Token must be a string with at least 10 characters. "
                    f"Got: {type(token).__name__} with length {len(str(token))}"
                )
            return token.strip()
        
        # Try loading from environment variables
        for env_var in self.TOKEN_ENV_VARS:
            env_token = os.getenv(env_var)
            if env_token:
                return env_token.strip()
        
        # No token found - fail fast with helpful message
        env_vars_str = ", ".join(self.TOKEN_ENV_VARS)
        raise ValidationError(
            f"API token required but not found.\n\n"
            f"Provide token in one of these ways:\n"
            f"  1. Pass as parameter: BrightDataClient(token='your_token')\n"
            f"  2. Set environment variable: {env_vars_str}\n\n"
            f"Get your API token from: https://brightdata.com/cp/api_keys"
        )
    
    def _validate_token_sync(self) -> None:
        """
        Validate token synchronously during initialization.
        
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            is_valid = asyncio.run(self.test_connection())
            if not is_valid:
                raise AuthenticationError(
                    f"Token validation failed. Token appears to be invalid.\n"
                    f"Check your token at: https://brightdata.com/cp/api_keys"
                )
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(
                f"Failed to validate token: {str(e)}\n"
                f"Check your token at: https://brightdata.com/cp/api_keys"
            )
    
    # ============================================================================
    # SERVICE PROPERTIES (Hierarchical Access)
    # ============================================================================
    
    @property
    def scrape(self) -> 'ScrapeService':
        """
        Access scraping services.
        
        Provides hierarchical access to specialized scrapers:
        - client.scrape.amazon.products(...)
        - client.scrape.linkedin.profiles(...)
        - client.scrape.generic.url(...)
        
        Returns:
            ScrapeService instance for accessing scrapers
        
        Example:
            >>> result = client.scrape.amazon.products(
            ...     url="https://amazon.com/dp/B0123456"
            ... )
        """
        if self._scrape_service is None:
            self._scrape_service = ScrapeService(self)
        return self._scrape_service
    
    @property
    def search(self) -> 'SearchService':
        """
        Access search services (SERP API).
        
        Provides access to search engine result scrapers:
        - client.search.google(query="...")
        - client.search.bing(query="...")
        - client.search.linkedin.jobs(...)
        
        Returns:
            SearchService instance for search operations
        
        Example:
            >>> results = client.search.google(
            ...     query="python scraping",
            ...     num_results=10
            ... )
        """
        if self._search_service is None:
            self._search_service = SearchService(self)
        return self._search_service
    
    @property
    def crawler(self) -> 'CrawlerService':
        """
        Access web crawling services.
        
        Provides access to domain crawling capabilities:
        - client.crawler.discover(url="...")
        - client.crawler.sitemap(url="...")
        
        Returns:
            CrawlerService instance for crawling operations
        
        Example:
            >>> result = client.crawler.discover(
            ...     url="https://example.com",
            ...     depth=3
            ... )
        """
        if self._crawler_service is None:
            self._crawler_service = CrawlerService(self)
        return self._crawler_service
    
    # ============================================================================
    # CONNECTION MANAGEMENT
    # ============================================================================
    
    async def test_connection(self) -> bool:
        """
        Test API connection and token validity.
        
        Makes a lightweight API call to verify:
        - Token is valid
        - API is reachable
        - Account is active
        
        Returns:
            True if connection successful, False otherwise (never raises exceptions)
        
        Note:
            This method never raises exceptions - it returns False for any errors
            (invalid token, network issues, etc.). This makes it safe for testing
            connectivity without exception handling.
        
        Example:
            >>> is_valid = await client.test_connection()
            >>> if is_valid:
            ...     print("✅ Connected successfully!")
            >>> else:
            ...     print("❌ Connection failed")
        """
        try:
            async with self.engine:
                # Try to get zones list - lightweight API call
                # Use direct session request to read response within context
                async with self.engine._session.get(
                    f"{self.engine.BASE_URL}/zone/get_active_zones",
                    headers=self.engine._session.headers
                ) as response:
                    if response.status == 200:
                        self._is_connected = True
                        return True
                    else:
                        # Any non-200 status means connection test failed
                        self._is_connected = False
                        return False
        
        except Exception as e:
            # Never raise exceptions from test_connection - always return False
            self._is_connected = False
            return False
    
    async def get_account_info(self) -> AccountInfo:
        """
        Get account information including usage, limits, and quotas.
        
        Retrieves:
        - Account status
        - Active zones
        - Usage statistics
        - Credit balance
        - Rate limits
        
        Returns:
            Dictionary with account information
        
        Raises:
            AuthenticationError: If token is invalid
            APIError: If API request fails
        
        Example:
            >>> info = await client.get_account_info()
            >>> print(f"Active zones: {len(info['zones'])}")
            >>> print(f"Credit balance: ${info['balance']}")
        """
        if self._account_info is not None:
            return self._account_info
        
        try:
            async with self.engine:
                # Get zones - read response within context
                async with self.engine._session.get(
                    f"{self.engine.BASE_URL}/zone/get_active_zones",
                    headers=self.engine._session.headers
                ) as zones_response:
                    if zones_response.status == 200:
                        zones = await zones_response.json()
                        
                        account_info = {
                            "customer_id": self.customer_id,
                            "zones": zones or [],
                            "zone_count": len(zones or []),
                            "token_valid": True,
                            "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        }
                        
                        self._account_info = account_info
                        return account_info
                    
                    elif zones_response.status in (401, 403):
                        error_text = await zones_response.text()
                        raise AuthenticationError(
                            f"Invalid token (HTTP {zones_response.status}): {error_text}"
                        )
                    else:
                        error_text = await zones_response.text()
                        raise APIError(
                            f"Failed to get account info (HTTP {zones_response.status}): {error_text}",
                            status_code=zones_response.status
                        )
        
        except (AuthenticationError, APIError):
            raise
        except Exception as e:
            raise APIError(f"Unexpected error getting account info: {str(e)}")
    
    def get_account_info_sync(self) -> AccountInfo:
        """Synchronous version of get_account_info()."""
        return asyncio.run(self.get_account_info())
    
    def test_connection_sync(self) -> bool:
        """Synchronous version of test_connection()."""
        try:
            return asyncio.run(self.test_connection())
        except Exception:
            return False
    
    # ============================================================================
    # LEGACY COMPATIBILITY (Flat API - for backward compatibility)
    # ============================================================================
    
    async def scrape_url_async(
        self,
        url: Union[str, List[str]],
        zone: Optional[str] = None,
        country: str = "",
        response_format: str = "raw",
        method: str = "GET",
        timeout: Optional[int] = None,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Direct scraping method (flat API).
        
        For backward compatibility. Prefer using hierarchical API:
        client.scrape.generic.url(...) for new code.
        """
        async with self.engine:
            if self._web_unlocker_service is None:
                self._web_unlocker_service = WebUnlockerService(self.engine)
            
            zone = zone or self.web_unlocker_zone
            return await self._web_unlocker_service.scrape_async(
                url=url,
                zone=zone,
                country=country,
                response_format=response_format,
                method=method,
                timeout=timeout,
            )
    
    def scrape_url(self, *args, **kwargs) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Synchronous version of scrape_url_async()."""
        return asyncio.run(self.scrape_url_async(*args, **kwargs))
    
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
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        token_preview = f"{self.token[:10]}...{self.token[-5:]}" if self.token else "None"
        status = "✓ Connected" if self._is_connected else "⚠ Not tested"
        return f"<BrightDataClient token={token_preview} status='{status}'>"


# ============================================================================
# SERVICE NAMESPACE CLASSES
# ============================================================================

class ScrapeService:
    """
    Scraping service namespace.
    
    Provides hierarchical access to specialized scrapers and generic scraping.
    """
    
    def __init__(self, client: BrightDataClient):
        """Initialize scrape service with client reference."""
        self._client = client
        self._amazon = None
        self._linkedin = None
        self._chatgpt = None
        self._generic = None
    
    @property
    def amazon(self):
        """
        Access Amazon scraper.
        
        Returns:
            AmazonScraper instance for Amazon product scraping and search
        
        Example:
            >>> # URL-based scraping
            >>> result = client.scrape.amazon.scrape("https://amazon.com/dp/B123")
            >>> 
            >>> # Keyword-based search
            >>> result = client.scrape.amazon.products(keyword="laptop")
        """
        if self._amazon is None:
            from .scrapers.amazon import AmazonScraper
            self._amazon = AmazonScraper(bearer_token=self._client.token)
        return self._amazon
    
    @property
    def linkedin(self):
        """
        Access LinkedIn scraper.
        
        Returns:
            LinkedInScraper instance for LinkedIn data extraction
        
        Example:
            >>> # URL-based scraping
            >>> result = client.scrape.linkedin.scrape("https://linkedin.com/in/johndoe")
            >>> 
            >>> # Search for jobs
            >>> result = client.scrape.linkedin.jobs(keyword="python", location="NYC")
            >>> 
            >>> # Search for profiles
            >>> result = client.scrape.linkedin.profiles(keyword="data scientist")
            >>> 
            >>> # Search for companies
            >>> result = client.scrape.linkedin.companies(keyword="tech startup")
        """
        if self._linkedin is None:
            from .scrapers.linkedin import LinkedInScraper
            self._linkedin = LinkedInScraper(bearer_token=self._client.token)
        return self._linkedin
    
    @property
    def chatgpt(self):
        """
        Access ChatGPT scraper.
        
        Returns:
            ChatGPTScraper instance for ChatGPT interactions
        
        Example:
            >>> # Single prompt
            >>> result = client.scrape.chatgpt.prompt("Explain async programming")
            >>> 
            >>> # Multiple prompts
            >>> result = client.scrape.chatgpt.prompts([
            ...     "What is Python?",
            ...     "What is JavaScript?"
            ... ])
        """
        if self._chatgpt is None:
            from .scrapers.chatgpt import ChatGPTScraper
            self._chatgpt = ChatGPTScraper(bearer_token=self._client.token)
        return self._chatgpt
    
    @property
    def generic(self):
        """Access generic web scraper (Web Unlocker)."""
        if self._generic is None:
            self._generic = GenericScraper(self._client)
        return self._generic


class GenericScraper:
    """Generic web scraper using Web Unlocker API."""
    
    def __init__(self, client: BrightDataClient):
        """Initialize generic scraper."""
        self._client = client
    
    async def url_async(
        self,
        url: Union[str, List[str]],
        country: str = "",
        response_format: str = "raw",
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape URL(s) asynchronously."""
        return await self._client.scrape_url_async(
            url=url,
            country=country,
            response_format=response_format,
        )
    
    def url(self, *args, **kwargs) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape URL(s) synchronously."""
        return asyncio.run(self.url_async(*args, **kwargs))


class SearchService:
    """
    Search service namespace (SERP API).
    
    Provides access to search engine result scrapers with normalized
    data across different search engines.
    
    Example:
        >>> # Google search
        >>> result = client.search.google(
        ...     query="python tutorial",
        ...     location="United States"
        ... )
        >>> 
        >>> # Access results
        >>> for item in result.data:
        ...     print(item['title'], item['url'])
    """
    
    def __init__(self, client: BrightDataClient):
        """Initialize search service with client reference."""
        self._client = client
        self._google_service: Optional['GoogleSERPService'] = None
        self._bing_service: Optional['BingSERPService'] = None
        self._yandex_service: Optional['YandexSERPService'] = None
        self._linkedin_search: Optional['LinkedInSearchService'] = None
        self._chatgpt_search: Optional['ChatGPTSearchService'] = None
    
    async def google_async(
        self,
        query: Union[str, List[str]],
        location: Optional[str] = None,
        language: str = "en",
        device: str = "desktop",
        num_results: int = 10,
        zone: Optional[str] = None,
        **kwargs
    ) -> Union['SearchResult', List['SearchResult']]:
        """
        Search Google asynchronously.
        
        Args:
            query: Search query or list of queries
            location: Geographic location (e.g., "United States", "New York")
            language: Language code (e.g., "en", "es", "fr")
            device: Device type ("desktop", "mobile", "tablet")
            num_results: Number of results to return (default: 10)
            zone: SERP zone (uses client default if not provided)
            **kwargs: Additional Google-specific parameters
        
        Returns:
            SearchResult with normalized Google search data
        
        Example:
            >>> result = await client.search.google_async(
            ...     query="python tutorial",
            ...     location="United States",
            ...     num_results=20
            ... )
        """
        from ..api.serp import GoogleSERPService
        
        if self._google_service is None:
            self._google_service = GoogleSERPService(self._client.engine)
        
        zone = zone or self._client.serp_zone
        return await self._google_service.search_async(
            query=query,
            zone=zone,
            location=location,
            language=language,
            device=device,
            num_results=num_results,
            **kwargs
        )
    
    def google(
        self,
        query: Union[str, List[str]],
        **kwargs
    ) -> Union['SearchResult', List['SearchResult']]:
        """
        Search Google synchronously.
        
        See google_async() for full documentation.
        
        Example:
            >>> result = client.search.google(
            ...     query="python tutorial",
            ...     location="United States"
            ... )
        """
        return asyncio.run(self.google_async(query, **kwargs))
    
    async def bing_async(
        self,
        query: Union[str, List[str]],
        location: Optional[str] = None,
        language: str = "en",
        num_results: int = 10,
        zone: Optional[str] = None,
        **kwargs
    ) -> Union['SearchResult', List['SearchResult']]:
        """Search Bing asynchronously."""
        from ..api.serp import BingSERPService
        
        if self._bing_service is None:
            self._bing_service = BingSERPService(self._client.engine)
        
        zone = zone or self._client.serp_zone
        return await self._bing_service.search_async(
            query=query,
            zone=zone,
            location=location,
            language=language,
            num_results=num_results,
            **kwargs
        )
    
    def bing(self, query: Union[str, List[str]], **kwargs):
        """Search Bing synchronously."""
        return asyncio.run(self.bing_async(query, **kwargs))
    
    async def yandex_async(
        self,
        query: Union[str, List[str]],
        location: Optional[str] = None,
        language: str = "ru",
        num_results: int = 10,
        zone: Optional[str] = None,
        **kwargs
    ) -> Union['SearchResult', List['SearchResult']]:
        """Search Yandex asynchronously."""
        from ..api.serp import YandexSERPService
        
        if self._yandex_service is None:
            self._yandex_service = YandexSERPService(self._client.engine)
        
        zone = zone or self._client.serp_zone
        return await self._yandex_service.search_async(
            query=query,
            zone=zone,
            location=location,
            language=language,
            num_results=num_results,
            **kwargs
        )
    
    def yandex(self, query: Union[str, List[str]], **kwargs):
        """Search Yandex synchronously."""
        return asyncio.run(self.yandex_async(query, **kwargs))
    
    @property
    def linkedin(self):
        """
        Access LinkedIn search service for parameter-based discovery.
        
        Returns:
            LinkedInSearchService for discovering posts, profiles, and jobs
        
        Example:
            >>> # Discover posts from profile
            >>> result = client.search.linkedin.posts(
            ...     profile_url="https://linkedin.com/in/johndoe",
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31"
            ... )
            >>> 
            >>> # Find profiles by name
            >>> result = client.search.linkedin.profiles(
            ...     firstName="John",
            ...     lastName="Doe"
            ... )
            >>> 
            >>> # Find jobs by criteria
            >>> result = client.search.linkedin.jobs(
            ...     keyword="python developer",
            ...     location="New York",
            ...     remote=True
            ... )
        """
        if self._linkedin_search is None:
            from .scrapers.linkedin.search import LinkedInSearchService
            self._linkedin_search = LinkedInSearchService(bearer_token=self._client.token)
        return self._linkedin_search
    
    @property
    def chatGPT(self):
        """
        Access ChatGPT search service for prompt-based discovery.
        
        Returns:
            ChatGPTSearchService for sending prompts to ChatGPT
        
        Example:
            >>> # Single prompt
            >>> result = client.search.chatGPT(
            ...     prompt="Explain Python async programming",
            ...     country="us",
            ...     webSearch=True
            ... )
            >>> 
            >>> # Batch prompts
            >>> result = client.search.chatGPT(
            ...     prompt=["What is Python?", "What is JavaScript?"],
            ...     country=["us", "us"],
            ...     webSearch=[False, True]
            ... )
        """
        if self._chatgpt_search is None:
            from .scrapers.chatgpt.search import ChatGPTSearchService
            self._chatgpt_search = ChatGPTSearchService(bearer_token=self._client.token)
        return self._chatgpt_search


class CrawlerService:
    """
    Web crawler service namespace.
    
    Provides access to domain crawling and discovery.
    """
    
    def __init__(self, client: BrightDataClient):
        """Initialize crawler service with client reference."""
        self._client = client
    
    async def discover(
        self,
        url: str,
        depth: int = 3,
        filter_pattern: str = "",
        exclude_pattern: str = "",
    ) -> Dict[str, Any]:
        """
        Discover and crawl website (to be implemented).
        
        Args:
            url: Starting URL
            depth: Maximum crawl depth
            filter_pattern: URL pattern to include
            exclude_pattern: URL pattern to exclude
        
        Returns:
            Crawl results with discovered pages
        """
        raise NotImplementedError("Crawler will be implemented in Crawl API module")
    
    async def sitemap(self, url: str) -> List[str]:
        """Extract sitemap URLs (to be implemented)."""
        raise NotImplementedError("Sitemap extraction will be implemented in Crawl API module")


# ============================================================================
# CONVENIENCE ALIASES
# ============================================================================

# Alias for backward compatibility
BrightData = BrightDataClient
