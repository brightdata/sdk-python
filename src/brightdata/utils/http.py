"""HTTP header helpers shared by the engine and the datasets layer."""

from __future__ import annotations

from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any, Dict, Optional


def diagnostic_response_headers(headers: Any) -> Dict[str, str]:
    """Keep documented diagnostics without retaining unrelated response headers."""
    if not headers:
        return {}
    allowed = {"retry-after", "x-debug-trace", "x-debug-trace-page"}
    return {
        name.lower(): value
        for name, value in headers.items()
        if isinstance(name, str) and name.lower() in allowed and isinstance(value, str)
    }


def parse_retry_after(headers: Any) -> Optional[float]:
    """
    Parse a Retry-After header into seconds.

    Supports both documented forms: delta-seconds ("30") and an HTTP-date
    ("Wed, 21 Oct 2015 07:28:00 GMT"). Returns None when the header is absent
    or unparseable — callers treat that as "the server did not say".
    """
    if not headers:
        return None
    try:
        value = headers.get("Retry-After")
    except AttributeError:
        return None
    if not value:
        return None

    value = str(value).strip()
    try:
        return max(0.0, float(value))
    except ValueError:
        pass

    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def status_phrase(status: int) -> str:
    """
    Human-readable phrase for an HTTP status.

    HTTPStatus(...) raises ValueError on non-standard codes, and those are real
    in the wild (Cloudflare uses 520-526), so fall back rather than raise.
    """
    try:
        return HTTPStatus(status).phrase
    except ValueError:
        return "HTTP error"
