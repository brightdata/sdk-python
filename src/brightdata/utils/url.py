"""URL utilities."""

from urllib.parse import urlparse


def extract_root_domain(url: str) -> str | None:
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

        netloc = netloc.removeprefix("www.")

        return netloc if netloc else None
    except Exception:
        return None
