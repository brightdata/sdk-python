"""Async HTTP engine for Bright Data API operations."""

import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from ..exceptions import APIError, AuthenticationError, NetworkError, TimeoutError

# Rate limiting support
try:
    from aiolimiter import AsyncLimiter
    HAS_RATE_LIMITER = True
except ImportError:
    HAS_RATE_LIMITER = False


class AsyncEngine:
    """
    Async HTTP engine for all API operations.
    
    Manages aiohttp sessions and provides async HTTP methods for
    communicating with Bright Data APIs.
    """
    
    BASE_URL = "https://api.brightdata.com"
    
    # Default rate limiting: 10 requests per second
    DEFAULT_RATE_LIMIT = 10
    DEFAULT_RATE_PERIOD = 1.0
    
    def __init__(
        self, 
        bearer_token: str, 
        timeout: int = 30,
        rate_limit: Optional[float] = None,
        rate_period: float = 1.0
    ):
        """
        Initialize async engine.
        
        Args:
            bearer_token: Bright Data API bearer token.
            timeout: Request timeout in seconds.
            rate_limit: Maximum requests per rate_period (default: 10). 
                       Set to None to disable rate limiting.
            rate_period: Time period in seconds for rate limit (default: 1.0).
        """
        self.bearer_token = bearer_token
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        if rate_limit is None:
            rate_limit = self.DEFAULT_RATE_LIMIT
        
        if HAS_RATE_LIMITER and rate_limit > 0:
            self._rate_limiter: Optional[AsyncLimiter] = AsyncLimiter(
                max_rate=rate_limit,
                time_period=rate_period
            )
        else:
            self._rate_limiter: Optional[AsyncLimiter] = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self._session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json",
                "User-Agent": "brightdata-sdk/2.0.0",
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None
    
    def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Make an async HTTP request.
        
        Returns a context manager that applies rate limiting and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint (relative to BASE_URL).
            json_data: Optional JSON payload.
            params: Optional query parameters.
            headers: Optional additional headers.
        
        Returns:
            Context manager for aiohttp ClientResponse (use with async with).
        
        Raises:
            RuntimeError: If engine not used as context manager.
            AuthenticationError: If authentication fails.
            APIError: If API request fails.
            NetworkError: If network error occurs.
            TimeoutError: If request times out.
        """
        if not self._session:
            raise RuntimeError("Engine must be used as async context manager")
        
        url = f"{self.BASE_URL}{endpoint}"
        request_headers = dict(self._session.headers)
        if headers:
            request_headers.update(headers)
        
        # Return context manager (rate limiting applied inside)
        return self._make_request(
            method=method,
            url=url,
            json_data=json_data,
            params=params,
            headers=request_headers,
            rate_limiter=self._rate_limiter
        )
    
    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Make POST request. Returns context manager."""
        return self.request("POST", endpoint, json_data=json_data, params=params, headers=headers)
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Make GET request. Returns context manager."""
        return self.request("GET", endpoint, params=params, headers=headers)
    
    def post_to_url(
        self,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ):
        """
        Make POST request to arbitrary URL.
        
        Public method for posting to URLs outside the standard BASE_URL endpoint.
        Used by scrapers and services that need to call external URLs.
        
        Args:
            url: Full URL to post to
            json_data: Optional JSON payload
            params: Optional query parameters
            headers: Optional additional headers
            timeout: Optional timeout override
        
        Returns:
            aiohttp ClientResponse context manager (use with async with)
        
        Raises:
            RuntimeError: If engine not used as context manager
            AuthenticationError: If authentication fails
            APIError: If API request fails
            NetworkError: If network error occurs
            TimeoutError: If request times out
        """
        if not self._session:
            raise RuntimeError("Engine must be used as async context manager")
        
        request_headers = dict(self._session.headers)
        if headers:
            request_headers.update(headers)
        
        # Return context manager that applies rate limiting
        return self._make_request(
            method="POST",
            url=url,
            json_data=json_data,
            params=params,
            headers=request_headers,
            timeout=timeout,
            rate_limiter=self._rate_limiter
        )
    
    def get_from_url(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ):
        """
        Make GET request to arbitrary URL.
        
        Public method for getting from URLs outside the standard BASE_URL endpoint.
        Used by scrapers and services that need to call external URLs.
        
        Args:
            url: Full URL to get from
            params: Optional query parameters
            headers: Optional additional headers
            timeout: Optional timeout override
        
        Returns:
            aiohttp ClientResponse context manager (use with async with)
        
        Raises:
            RuntimeError: If engine not used as context manager
            AuthenticationError: If authentication fails
            APIError: If API request fails
            NetworkError: If network error occurs
            TimeoutError: If request times out
        """
        if not self._session:
            raise RuntimeError("Engine must be used as async context manager")
        
        request_headers = dict(self._session.headers)
        if headers:
            request_headers.update(headers)
        
        # Return context manager that applies rate limiting
        return self._make_request(
            method="GET",
            url=url,
            params=params,
            headers=request_headers,
            timeout=timeout,
            rate_limiter=self._rate_limiter
        )
    
    def _make_request(
        self,
        method: str,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
        rate_limiter: Optional[Any] = None,
    ):
        """
        Internal method to make HTTP request with error handling.
        
        Args:
            method: HTTP method
            url: Full URL
            json_data: Optional JSON payload
            params: Optional query parameters
            headers: Request headers
            timeout: Optional timeout override
            rate_limiter: Optional rate limiter to apply
        
        Returns:
            Context manager for aiohttp ClientResponse
        
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API request fails
            NetworkError: If network error occurs
            TimeoutError: If request times out
        """
        request_timeout = timeout or self.timeout
        
        # Return context manager that handles errors and rate limiting when entered
        class ResponseContextManager:
            def __init__(self, session, method, url, json_data, params, headers, timeout, rate_limiter):
                self._session = session
                self._method = method
                self._url = url
                self._json_data = json_data
                self._params = params
                self._headers = headers
                self._timeout = timeout
                self._rate_limiter = rate_limiter
                self._response = None
            
            async def __aenter__(self):
                # Apply rate limiting if enabled
                if self._rate_limiter:
                    await self._rate_limiter.acquire()
                
                try:
                    self._response = await self._session.request(
                        method=self._method,
                        url=self._url,
                        json=self._json_data,
                        params=self._params,
                        headers=self._headers,
                        timeout=self._timeout,
                    )
                    # Check status codes that should raise exceptions
                    if self._response.status == 401:
                        text = await self._response.text()
                        await self._response.release()
                        raise AuthenticationError(f"Unauthorized (401): {text}")
                    elif self._response.status == 403:
                        text = await self._response.text()
                        await self._response.release()
                        raise AuthenticationError(f"Forbidden (403): {text}")
                    
                    return self._response
                except aiohttp.ClientError as e:
                    raise NetworkError(f"Network error: {str(e)}") from e
                except asyncio.TimeoutError as e:
                    raise TimeoutError(f"Request timeout after {self._timeout.total} seconds") from e
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self._response:
                    self._response.close()
        
        return ResponseContextManager(
            self._session, method, url, json_data, params, headers, request_timeout, rate_limiter
        )
