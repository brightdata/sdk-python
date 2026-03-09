"""URL utilities."""

from urllib.parse import urlparse
from typing import Optional


def extract_root_domain(url: str) -> Optional[str]:
    """
    Extract root domain from URL.

    Args:
        url: URL string.

    Returns:
        Root domain (e.g., "example.com") or None if extraction fails.
    """
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc

        if ":" in netloc:
            netloc = netloc.split(":")[0]

        if netloc.startswith("www."):
            netloc = netloc[4:]

        return netloc if netloc else None
    except Exception:
        return None
