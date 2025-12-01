"""Async HTTP engine for Bright Data API operations."""

import asyncio
import aiohttp
import ssl
import warnings
from typing import Optional, Dict, Any
from ..exceptions import AuthenticationError, NetworkError, TimeoutError, SSLError
from ..constants import HTTP_UNAUTHORIZED, HTTP_FORBIDDEN
from ..utils.ssl_helpers import is_ssl_certificate_error, get_ssl_error_message

# Rate limiting support
try:
    from aiolimiter import AsyncLimiter

    HAS_RATE_LIMITER = True
except ImportError:
    HAS_RATE_LIMITER = False

# Suppress aiohttp ResourceWarnings for unclosed sessions
# We properly manage session lifecycle in context managers, but Python's
# resource tracking may still emit warnings during rapid create/destroy cycles
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<aiohttp")
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket")


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
        rate_period: float = 1.0,
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

        # Store rate limit config (create limiter per event loop in __aenter__)
        if rate_limit is None:
            rate_limit = self.DEFAULT_RATE_LIMIT

        self._rate_limit = rate_limit
        self._rate_period = rate_period
        self._rate_limiter: Optional[AsyncLimiter] = None

    async def __aenter__(self):
        """Context manager entry - idempotent (safe to call multiple times)."""
        # If session already exists, don't create a new one
        # This handles nested context manager usage
        if self._session is not None:
            return self

        # Create connector with force_close=True to ensure proper cleanup
        # This helps prevent "Unclosed connector" warnings
        connector = aiohttp.TCPConnector(
            limit=100, limit_per_host=30, force_close=True  # Force close connections on exit
        )

        # Create session with the connector
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json",
                "User-Agent": "brightdata-sdk/2.0.0",
            },
        )

        # Create rate limiter for this event loop (avoids reuse across loops)
        if HAS_RATE_LIMITER and self._rate_limit > 0:
            self._rate_limiter = AsyncLimiter(
                max_rate=self._rate_limit, time_period=self._rate_period
            )
        else:
            self._rate_limiter = None

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures proper cleanup of resources."""
        if self._session:
            # Store reference before clearing
            session = self._session
            self._session = None

            # Close the session - this will also close the connector
            await session.close()

            # Wait for underlying connections to close
            # This is necessary to prevent "Unclosed client session" warnings
            await asyncio.sleep(0.1)

        # Clear rate limiter
        self._rate_limiter = None

    def __del__(self):
        """Cleanup on garbage collection."""
        # If session wasn't properly closed (shouldn't happen with proper usage),
        # try to clean up to avoid warnings
        if hasattr(self, "_session") and self._session:
            try:
                if not self._session.closed:
                    # Can't use async here, so just close the connector directly
                    if hasattr(self._session, "_connector") and self._session._connector:
                        self._session._connector.close()
            except Exception:
                # Silently ignore any errors during __del__
                pass

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
            rate_limiter=self._rate_limiter,
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

    def delete(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Make DELETE request. Returns context manager."""
        return self.request("DELETE", endpoint, json_data=json_data, params=params, headers=headers)

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
            rate_limiter=self._rate_limiter,
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
            rate_limiter=self._rate_limiter,
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
            def __init__(
                self, session, method, url, json_data, params, headers, timeout, rate_limiter
            ):
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
                    if self._response.status == HTTP_UNAUTHORIZED:
                        text = await self._response.text()
                        await self._response.release()
                        raise AuthenticationError(f"Unauthorized ({HTTP_UNAUTHORIZED}): {text}")
                    elif self._response.status == HTTP_FORBIDDEN:
                        text = await self._response.text()
                        await self._response.release()
                        raise AuthenticationError(f"Forbidden ({HTTP_FORBIDDEN}): {text}")

                    return self._response
                except (aiohttp.ClientError, ssl.SSLError, OSError) as e:
                    # Check for SSL certificate errors first
                    # aiohttp wraps SSL errors in ClientConnectorError or ClientSSLError
                    # OSError can also be raised for SSL issues
                    if is_ssl_certificate_error(e):
                        error_message = get_ssl_error_message(e)
                        raise SSLError(error_message) from e
                    # Other network errors
                    raise NetworkError(f"Network error: {str(e)}") from e
                except asyncio.TimeoutError as e:
                    raise TimeoutError(
                        f"Request timeout after {self._timeout.total} seconds"
                    ) from e

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self._response:
                    self._response.close()

        return ResponseContextManager(
            self._session, method, url, json_data, params, headers, request_timeout, rate_limiter
        )
