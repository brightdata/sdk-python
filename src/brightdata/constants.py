"""Shared constants for Bright Data SDK."""

# Polling configuration
DEFAULT_POLL_INTERVAL: int = 10
"""Default interval in seconds between status checks during polling."""

DEFAULT_POLL_TIMEOUT: int = 600
"""Default maximum time in seconds to wait for polling to complete."""

# Timeout defaults for different platforms
DEFAULT_TIMEOUT_SHORT: int = 180
"""Default timeout for platforms that typically respond quickly (e.g., LinkedIn, ChatGPT search)."""

DEFAULT_TIMEOUT_MEDIUM: int = 240
"""Default timeout for platforms that may take longer (e.g., Amazon, Facebook, Instagram)."""

DEFAULT_TIMEOUT_LONG: int = 120
"""Default timeout for platforms with faster response times (e.g., ChatGPT scraper)."""

# Base scraper defaults
DEFAULT_MIN_POLL_TIMEOUT: int = 180
"""Default minimum poll timeout for base scrapers."""

DEFAULT_COST_PER_RECORD: float = 0.001
"""Default cost per record for base scrapers."""
