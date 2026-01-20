"""Input validation utilities."""

import re
from urllib.parse import urlparse
from typing import List
from ..exceptions import ValidationError


def validate_url(url: str) -> None:
    """
    Validate URL format.

    Args:
        url: URL string to validate.

    Raises:
        ValidationError: If URL is invalid.
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")

    try:
        result = urlparse(url)
        if not result.scheme or not result.netloc:
            raise ValidationError(f"Invalid URL format: {url}")
        if result.scheme not in ("http", "https"):
            raise ValidationError(f"URL must use http or https scheme: {url}")
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Invalid URL format: {url}") from e


def validate_url_list(urls: List[str]) -> None:
    """
    Validate list of URLs.

    Args:
        urls: List of URL strings to validate.

    Raises:
        ValidationError: If any URL is invalid or list is empty.
    """
    if not urls:
        raise ValidationError("URL list cannot be empty")

    if not isinstance(urls, list):
        raise ValidationError("URLs must be a list")

    for url in urls:
        validate_url(url)


def validate_zone_name(zone: str) -> None:
    """
    Validate zone name format.

    Args:
        zone: Zone name to validate.

    Raises:
        ValidationError: If zone name is invalid.
    """
    if not zone or not isinstance(zone, str):
        raise ValidationError("Zone name must be a non-empty string")

    if not re.match(r"^[a-zA-Z0-9_-]+$", zone):
        raise ValidationError(f"Invalid zone name format: {zone}")


def validate_country_code(country: str) -> None:
    """
    Validate ISO country code format.

    Args:
        country: Country code to validate (empty string is allowed).

    Raises:
        ValidationError: If country code is invalid.
    """
    if not country:
        return

    if not isinstance(country, str):
        raise ValidationError("Country code must be a string")

    if not re.match(r"^[A-Z]{2}$", country.upper()):
        raise ValidationError(
            f"Invalid country code format: {country}. Must be ISO 3166-1 alpha-2 (e.g., 'US', 'GB')"
        )


def validate_timeout(timeout: int) -> None:
    """
    Validate timeout value.

    Args:
        timeout: Timeout in seconds.

    Raises:
        ValidationError: If timeout is invalid.
    """
    if not isinstance(timeout, int):
        raise ValidationError("Timeout must be an integer")

    if timeout <= 0:
        raise ValidationError(f"Timeout must be positive, got {timeout}")


def validate_max_workers(max_workers: int) -> None:
    """
    Validate max_workers value.

    Args:
        max_workers: Maximum number of workers.

    Raises:
        ValidationError: If max_workers is invalid.
    """
    if not isinstance(max_workers, int):
        raise ValidationError("max_workers must be an integer")

    if max_workers <= 0:
        raise ValidationError(f"max_workers must be positive, got {max_workers}")


def validate_response_format(response_format: str) -> None:
    """
    Validate response format.

    Args:
        response_format: Response format string.

    Raises:
        ValidationError: If response format is invalid.
    """
    valid_formats = ("raw", "json")
    if response_format not in valid_formats:
        raise ValidationError(
            f"Invalid response_format: {response_format}. Must be one of: {valid_formats}"
        )


def validate_http_method(method: str) -> None:
    """
    Validate HTTP method.

    Args:
        method: HTTP method string.

    Raises:
        ValidationError: If HTTP method is invalid.
    """
    valid_methods = ("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS")
    if method.upper() not in valid_methods:
        raise ValidationError(f"Invalid HTTP method: {method}. Must be one of: {valid_methods}")


def validate_instagram_date(date: str) -> None:
    """
    Validate Instagram date format (MM-DD-YYYY).

    Instagram API requires dates in MM-DD-YYYY format, not ISO format.

    Args:
        date: Date string to validate.

    Raises:
        ValidationError: If date format is invalid.

    Example:
        >>> validate_instagram_date("01-15-2025")  # Valid
        >>> validate_instagram_date("2025-01-15")  # Raises ValidationError
    """
    if not date or not isinstance(date, str):
        raise ValidationError("Date must be a non-empty string")

    # Check MM-DD-YYYY format
    if not re.match(r"^\d{2}-\d{2}-\d{4}$", date):
        raise ValidationError(
            f"Invalid date format: {date}. Instagram requires MM-DD-YYYY format (e.g., '01-15-2025')"
        )

    # Validate actual date values
    try:
        month, day, year = date.split("-")
        month_int = int(month)
        day_int = int(day)
        year_int = int(year)

        if not (1 <= month_int <= 12):
            raise ValidationError(f"Invalid month in date: {date}. Month must be 01-12")
        if not (1 <= day_int <= 31):
            raise ValidationError(f"Invalid day in date: {date}. Day must be 01-31")
        if not (1900 <= year_int <= 2100):
            raise ValidationError(f"Invalid year in date: {date}. Year must be 1900-2100")
    except ValueError:
        raise ValidationError(f"Invalid date format: {date}. Instagram requires MM-DD-YYYY format")
