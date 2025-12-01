"""Location parsing utilities for SERP services."""

from typing import Dict
from enum import Enum


class LocationFormat(Enum):
    """Location code format for different search engines."""

    GOOGLE = "google"  # Lowercase 2-letter codes
    BING = "bing"  # Uppercase 2-letter codes
    YANDEX = "yandex"  # Numeric region IDs


class LocationService:
    """Unified location parsing service for all SERP engines."""

    # Common country mappings
    COUNTRY_MAP: Dict[str, str] = {
        "united states": "us",
        "usa": "us",
        "united kingdom": "gb",
        "uk": "gb",
        "canada": "ca",
        "australia": "au",
        "germany": "de",
        "france": "fr",
        "spain": "es",
        "italy": "it",
        "japan": "jp",
        "china": "cn",
        "india": "in",
        "brazil": "br",
        "russia": "ru",
        "ukraine": "ua",
        "belarus": "by",
        "poland": "pl",
        "netherlands": "nl",
        "sweden": "se",
        "norway": "no",
        "denmark": "dk",
        "finland": "fi",
        "mexico": "mx",
        "argentina": "ar",
        "south korea": "kr",
        "singapore": "sg",
        "new zealand": "nz",
        "south africa": "za",
    }

    # Yandex-specific numeric region IDs
    YANDEX_REGION_MAP: Dict[str, str] = {
        "russia": "225",
        "ukraine": "187",
        "belarus": "149",
        "kazakhstan": "159",
        "turkey": "983",
    }

    @classmethod
    def parse_location(cls, location: str, format: LocationFormat = LocationFormat.GOOGLE) -> str:
        """
        Parse location string to engine-specific code.

        Args:
            location: Location name or code
            format: Target format (GOOGLE, BING, or YANDEX)

        Returns:
            Location code in the requested format
        """
        if not location:
            return cls._get_default(format)

        location_lower = location.lower().strip()

        # Check if already a 2-letter country code
        if len(location_lower) == 2 and format != LocationFormat.YANDEX:
            code = location_lower
        else:
            # Look up in country mapping
            code = cls.COUNTRY_MAP.get(location_lower, cls._get_default(format))

        # Format according to engine requirements
        if format == LocationFormat.GOOGLE:
            return code.lower()
        elif format == LocationFormat.BING:
            return code.upper()
        elif format == LocationFormat.YANDEX:
            # Yandex uses numeric region IDs
            return cls.YANDEX_REGION_MAP.get(location_lower, "225")
        else:
            return code

    @classmethod
    def _get_default(cls, format: LocationFormat) -> str:
        """Get default location code for format."""
        if format == LocationFormat.GOOGLE:
            return "us"
        elif format == LocationFormat.BING:
            return "US"
        elif format == LocationFormat.YANDEX:
            return "225"
        else:
            return "us"
