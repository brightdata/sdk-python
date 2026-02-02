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

try:
    from .perplexity.scraper import PerplexityScraper
except ImportError:
    PerplexityScraper = None

try:
    from .tiktok.scraper import TikTokScraper
except ImportError:
    TikTokScraper = None

try:
    from .tiktok.search import TikTokSearchScraper
except ImportError:
    TikTokSearchScraper = None

try:
    from .youtube.scraper import YouTubeScraper
except ImportError:
    YouTubeScraper = None

try:
    from .youtube.search import YouTubeSearchScraper
except ImportError:
    YouTubeSearchScraper = None


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
    "PerplexityScraper",
    "TikTokScraper",
    "TikTokSearchScraper",
    "YouTubeScraper",
    "YouTubeSearchScraper",
]
