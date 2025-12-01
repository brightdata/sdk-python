"""Specialized platform scrapers."""

from .base import BaseWebScraper
from .registry import register, get_scraper_for, get_registered_platforms, is_platform_supported
from .job import ScrapeJob

# Import scrapers to trigger registration
try:
    from .amazon.scraper import AmazonScraper
except ImportError:
    AmazonScraper = None

try:
    from .linkedin.scraper import LinkedInScraper
except ImportError:
    LinkedInScraper = None

try:
    from .chatgpt.scraper import ChatGPTScraper
except ImportError:
    ChatGPTScraper = None

try:
    from .facebook.scraper import FacebookScraper
except ImportError:
    FacebookScraper = None

try:
    from .instagram.scraper import InstagramScraper
except ImportError:
    InstagramScraper = None

try:
    from .instagram.search import InstagramSearchScraper
except ImportError:
    InstagramSearchScraper = None


__all__ = [
    "BaseWebScraper",
    "ScrapeJob",
    "register",
    "get_scraper_for",
    "get_registered_platforms",
    "is_platform_supported",
    "AmazonScraper",
    "LinkedInScraper",
    "ChatGPTScraper",
    "FacebookScraper",
    "InstagramScraper",
    "InstagramSearchScraper",
]
