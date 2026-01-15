"""Instagram scrapers for URL-based and parameter-based extraction."""

from .scraper import InstagramScraper
from .search import InstagramSearchScraper

__all__ = ["InstagramScraper", "InstagramSearchScraper"]
