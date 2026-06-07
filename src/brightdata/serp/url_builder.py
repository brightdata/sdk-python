"""URL builder for SERP search engines."""

from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import quote_plus
from ..utils.location import LocationService, LocationFormat


class BaseURLBuilder(ABC):
    """Base class for search engine URL builders."""

    @abstractmethod
    def build(
        self,
        query: str,
        location: Optional[str] = None,
        language: str = "en",
        device: str = "desktop",
        num_results: int = 10,
        **kwargs,
    ) -> str:
        """Build search URL."""
        pass


class GoogleURLBuilder(BaseURLBuilder):
    """URL builder for Google search."""

    def build(
        self,
        query: str,
        location: Optional[str] = None,
        language: str = "en",
        device: str = "desktop",
        num_results: int = 10,
        start: int = 0,
        **kwargs,
    ) -> str:
        """Build Google search URL with Bright Data parsing enabled."""
        encoded_query = quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"

        # Add pagination offset if not first page
        if start > 0:
            url += f"&start={start}"

        url += f"&num={num_results}"

        # Enable Bright Data SERP parsing
        url += "&brd_json=1"

        if language:
            url += f"&hl={language}"

        if location:
            location_code = LocationService.parse_location(location, LocationFormat.GOOGLE)
            if location_code:
                url += f"&gl={location_code}"

        if device == "mobile":
            url += "&mobileaction=1"

        if "safe_search" in kwargs:
            url += f"&safe={'active' if kwargs['safe_search'] else 'off'}"

        if "time_range" in kwargs:
            url += f"&tbs=qdr:{kwargs['time_range']}"

        return url


class BingURLBuilder(BaseURLBuilder):
    """URL builder for Bing search."""

    def build(
        self,
        query: str,
        location: Optional[str] = None,
        language: str = "en",
        device: str = "desktop",
        num_results: int = 10,
        **kwargs,
    ) -> str:
        """Build Bing search URL.

        Parsing is opted in via the BingSERPService.DATA_FORMAT = "parsed_bing"
        payload field, not a URL flag — so this builder only assembles the
        target Bing URL (query, count, market, language).
        """
        encoded_query = quote_plus(query)
        url = f"https://www.bing.com/search?q={encoded_query}"
        url += f"&count={num_results}"

        if location:
            location_code = LocationService.parse_location(location, LocationFormat.BING)
            url += f"&mkt={language}-{location_code}"
        elif language:
            url += f"&setlang={language}"

        return url


class YandexURLBuilder(BaseURLBuilder):
    """URL builder for Yandex search."""

    def build(
        self,
        query: str,
        location: Optional[str] = None,
        language: str = "en",
        device: str = "desktop",
        num_results: int = 10,
        **kwargs,
    ) -> str:
        """Build Yandex search URL.

        Note: Bright Data does NOT provide a parsed JSON format for Yandex
        (brd_json=1 returns HTTP 400 "JSON output is not supported", and there
        is no `parsed_yandex` data_format). Yandex responses come back as raw
        HTML and the normalizer returns them via `raw_html` rather than
        structured organic results.
        """
        encoded_query = quote_plus(query)
        url = f"https://yandex.com/search/?text={encoded_query}"
        url += f"&numdoc={num_results}"

        if location:
            region_code = LocationService.parse_location(location, LocationFormat.YANDEX)
            url += f"&lr={region_code}"

        return url
