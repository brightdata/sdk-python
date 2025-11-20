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

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .core.engine import AsyncEngine
from .api.web_unlocker import WebUnlockerService
from .api.scrape_service import ScrapeService, GenericScraper
from .api.search_service import SearchService
from .api.crawler_service import CrawlerService
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
    
    # Environment variable name for API token
    TOKEN_ENV_VAR = "BRIGHTDATA_API_TOKEN"
    
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
        rate_limit: Optional[float] = None,
        rate_period: float = 1.0,
    ):
        """
        Initialize Bright Data client.
        
        Authentication happens automatically from environment variables if not provided.
        Supports loading from .env files (requires python-dotenv package).
        
        Args:
            token: API token. If None, loads from BRIGHTDATA_API_TOKEN environment variable
                  (supports .env files via python-dotenv)
            customer_id: Customer ID (optional, can also be set via BRIGHTDATA_CUSTOMER_ID)
            timeout: Default timeout in seconds for all requests (default: 30)
            web_unlocker_zone: Zone name for web unlocker (default: "sdk_unlocker")
            serp_zone: Zone name for SERP API (default: "sdk_serp")
            browser_zone: Zone name for browser API (default: "sdk_browser")
            auto_create_zones: Automatically create zones if they don't exist (default: False)
            validate_token: Validate token by testing connection on init (default: False)
            rate_limit: Maximum requests per rate_period (default: 10). Set to None to disable.
            rate_period: Time period in seconds for rate limit (default: 1.0)
        
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
        self.token = self._load_token(token)
        self.customer_id = customer_id or os.getenv("BRIGHTDATA_CUSTOMER_ID")
        self.timeout = timeout
        self.web_unlocker_zone = web_unlocker_zone or self.DEFAULT_WEB_UNLOCKER_ZONE
        self.serp_zone = serp_zone or self.DEFAULT_SERP_ZONE
        self.browser_zone = browser_zone or self.DEFAULT_BROWSER_ZONE
        self.auto_create_zones = auto_create_zones
        
        self.engine = AsyncEngine(
            self.token, 
            timeout=timeout,
            rate_limit=rate_limit,
            rate_period=rate_period
        )
        
        self._scrape_service: Optional[ScrapeService] = None
        self._search_service: Optional[SearchService] = None
        self._crawler_service: Optional[CrawlerService] = None
        self._web_unlocker_service: Optional[WebUnlockerService] = None
        self._is_connected = False
        self._account_info: Optional[Dict[str, Any]] = None
        
        if validate_token:
            self._validate_token_sync()
    
    def _load_token(self, token: Optional[str]) -> str:
        """
        Load token from parameter or environment variable.
        
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
        
        # Try loading from environment variable
        env_token = os.getenv(self.TOKEN_ENV_VAR)
        if env_token:
            return env_token.strip()
        
        # No token found - fail fast with helpful message
        raise ValidationError(
            f"API token required but not found.\n\n"
            f"Provide token in one of these ways:\n"
            f"  1. Pass as parameter: BrightDataClient(token='your_token')\n"
            f"  2. Set environment variable: {self.TOKEN_ENV_VAR}\n\n"
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
    
    
    @property
    def scrape(self) -> ScrapeService:
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
    def search(self) -> SearchService:
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
    def crawler(self) -> CrawlerService:
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
            ...     print("Connected successfully!")
            >>> else:
            ...     print("Connection failed")
        """
        try:
            async with self.engine:
                async with self.engine.get_from_url(
                    f"{self.engine.BASE_URL}/zone/get_active_zones"
                ) as response:
                    if response.status == 200:
                        self._is_connected = True
                        return True
                    else:
                        self._is_connected = False
                        return False
        
        except Exception:
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
                async with await self.engine.get_from_url(
                    f"{self.engine.BASE_URL}/zone/get_active_zones"
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
        status = "Connected" if self._is_connected else "Not tested"
        return f"<BrightDataClient token={token_preview} status='{status}'>"


BrightData = BrightDataClient
