"""
Registry pattern for auto-discovery of platform scrapers.

Philosophy:
- Build for future intelligent routing
- Scrapers self-register via decorator
- URL-based auto-routing for future use
- Extensible for adding new platforms
"""

import importlib
import logging
import pkgutil
from functools import lru_cache
from typing import Dict, Type, Optional, List
import tldextract

# Configure logger for registry operations
logger = logging.getLogger(__name__)


# Global registry mapping domain → scraper class
_SCRAPER_REGISTRY: Dict[str, Type] = {}


def register(domain: str):
    """
    Decorator to register a scraper for a domain.

    Scrapers register themselves using this decorator, enabling
    auto-discovery and intelligent routing.

    Args:
        domain: Second-level domain (e.g., "amazon", "linkedin", "instagram")

    Returns:
        Decorator function that registers the class

    Example:
        >>> @register("amazon")
        >>> class AmazonScraper(BaseWebScraper):
        ...     DATASET_ID = "gd_l7q7dkf244hwxbl93"
        ...     PLATFORM_NAME = "Amazon"
        ...
        ...     async def products_async(self, keyword: str):
        ...         # Search implementation
        ...         pass
        >>>
        >>> # Later, auto-discovery works:
        >>> scraper_class = get_scraper_for("https://www.amazon.com/dp/B123")
        >>> # Returns AmazonScraper class
    """

    def decorator(cls: Type) -> Type:
        _SCRAPER_REGISTRY[domain.lower()] = cls
        return cls

    return decorator


@lru_cache(maxsize=1)
def _import_all_scrapers():
    """
    Import all scraper modules to trigger @register decorators.

    This function runs exactly once (cached) and imports all scraper
    modules in the scrapers package, which causes their @register
    decorators to execute and populate the registry.

    Note:
        Uses pkgutil.walk_packages to discover all modules recursively.
        Only imports modules ending with '.scraper' or containing '.scraper.'
        to avoid unnecessary imports.
    """
    import brightdata.scrapers as pkg

    for mod_info in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        module_name = mod_info.name

        # Only import scraper modules (optimization)
        if module_name.endswith(".scraper") or ".scraper." in module_name:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                # Log import errors but continue (module might be optional)
                logger.warning(
                    f"Failed to import scraper module '{module_name}': {e}. "
                    f"This may be expected if the module is optional or incomplete."
                )
            except Exception as e:
                # Log unexpected errors but continue to avoid breaking registry
                logger.error(
                    f"Unexpected error importing scraper module '{module_name}': {e}", exc_info=True
                )


def get_scraper_for(url: str) -> Optional[Type]:
    """
    Get scraper class for a URL based on domain.

    Auto-discovers and returns the appropriate scraper class for the
    given URL's domain. Returns None if no scraper registered for domain.

    Args:
        url: URL to find scraper for (e.g., "https://www.amazon.com/dp/B123")

    Returns:
        Scraper class if found, None otherwise

    Example:
        >>> # Get scraper for Amazon URL
        >>> ScraperClass = get_scraper_for("https://amazon.com/dp/B123")
        >>> if ScraperClass:
        ...     scraper = ScraperClass(bearer_token="token")
        ...     result = scraper.scrape("https://amazon.com/dp/B123")
        >>> else:
        ...     print("No specialized scraper for this domain")

    Note:
        This enables future intelligent routing:
        - Auto-detect platform from URL
        - Route to specialized scraper automatically
        - Fallback to generic scraper if no match
    """
    # Ensure all scrapers are imported and registered
    _import_all_scrapers()

    # Extract domain from URL
    extracted = tldextract.extract(url)
    domain = extracted.domain.lower()  # e.g., "amazon", "linkedin"

    # Look up in registry
    return _SCRAPER_REGISTRY.get(domain)


def get_registered_platforms() -> List[str]:
    """
    Get list of all registered platform domains.

    Returns:
        List of registered domain names

    Example:
        >>> platforms = get_registered_platforms()
        >>> print(platforms)
        ['amazon', 'linkedin', 'instagram', 'chatgpt']
    """
    _import_all_scrapers()
    return sorted(_SCRAPER_REGISTRY.keys())


def is_platform_supported(url: str) -> bool:
    """
    Check if URL's platform has a registered scraper.

    Args:
        url: URL to check

    Returns:
        True if platform has registered scraper, False otherwise

    Example:
        >>> is_platform_supported("https://amazon.com/dp/B123")
        True
        >>> is_platform_supported("https://unknown-site.com/page")
        False
    """
    return get_scraper_for(url) is not None


# For backward compatibility and explicit access
def get_registry() -> Dict[str, Type]:
    """
    Get the complete scraper registry.

    Returns:
        Dictionary mapping domain → scraper class

    Note:
        This is mainly for debugging and testing. Use get_scraper_for()
        for normal operation.
    """
    _import_all_scrapers()
    return _SCRAPER_REGISTRY.copy()
