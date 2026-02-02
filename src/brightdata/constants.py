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

# Platform-specific costs (when different from default)
COST_PER_RECORD_LINKEDIN: float = 0.002
"""Cost per record for LinkedIn scrapers."""

COST_PER_RECORD_FACEBOOK: float = 0.002
"""Cost per record for Facebook scrapers."""

COST_PER_RECORD_INSTAGRAM: float = 0.002
"""Cost per record for Instagram scrapers."""

COST_PER_RECORD_CHATGPT: float = 0.005
"""Cost per record for ChatGPT scrapers (higher due to AI processing)."""

COST_PER_RECORD_PERPLEXITY: float = 0.005
"""Cost per record for Perplexity scrapers (higher due to AI processing)."""

COST_PER_RECORD_TIKTOK: float = 0.002
"""Cost per record for TikTok scrapers."""

COST_PER_RECORD_YOUTUBE: float = 0.002
"""Cost per record for YouTube scrapers."""

# HTTP Status Codes
HTTP_OK: int = 200
"""HTTP 200 OK - Request succeeded."""

HTTP_CREATED: int = 201
"""HTTP 201 Created - Resource created successfully."""

HTTP_BAD_REQUEST: int = 400
"""HTTP 400 Bad Request - Invalid request parameters."""

HTTP_UNAUTHORIZED: int = 401
"""HTTP 401 Unauthorized - Authentication required or failed."""

HTTP_FORBIDDEN: int = 403
"""HTTP 403 Forbidden - Access denied."""

HTTP_CONFLICT: int = 409
"""HTTP 409 Conflict - Resource conflict (e.g., duplicate)."""

HTTP_INTERNAL_SERVER_ERROR: int = 500
"""HTTP 500 Internal Server Error - Server error."""
