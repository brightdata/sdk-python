"""Exception hierarchy for Bright Data SDK."""

from __future__ import annotations


class BrightDataError(Exception):
    """Base exception for all Bright Data errors."""

    def __init__(self, message: str, *args, **kwargs):
        super().__init__(message, *args)
        self.message = message


class ValidationError(BrightDataError):
    """Input validation failed."""

    pass


class AuthenticationError(BrightDataError):
    """Authentication or authorization failed."""

    pass


class APIError(BrightDataError):
    """API request failed."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_text: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(message, *args, **kwargs)
        self.status_code = status_code
        self.response_text = response_text


class TimeoutError(BrightDataError):
    """Operation timed out."""

    pass


class ZoneError(BrightDataError):
    """Zone operation failed."""

    pass


class NetworkError(BrightDataError):
    """Network connectivity issue."""

    pass


class SSLError(BrightDataError):
    """
    SSL certificate verification error.

    Common on macOS where Python doesn't have access to system certificates.
    """

    pass
