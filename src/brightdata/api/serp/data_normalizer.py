"""Data normalization for SERP responses."""

import warnings
from abc import ABC, abstractmethod
from typing import Any
from ...types import NormalizedSERPData


class BaseDataNormalizer(ABC):
    """Base class for SERP data normalization."""

    @abstractmethod
    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize SERP data to consistent format."""
        pass


class GoogleDataNormalizer(BaseDataNormalizer):
    """Data normalizer for Google SERP responses."""

    # Length of prefix to check for HTML detection
    HTML_DETECTION_PREFIX_LENGTH = 200

    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize Google SERP data."""
        if not isinstance(data, (dict, str)):
            return {"results": []}

        if isinstance(data, str):
            return {
                "results": [],
                "raw_html": data,
            }

        # Handle raw HTML response (body field)
        if "body" in data and isinstance(data.get("body"), str):
            body = data["body"]
            # Check if body is HTML with improved detection
            body_lower = body.strip().lower()
            is_html = (
                body_lower.startswith(("<html", "<!doctype", "<!DOCTYPE"))
                or "<html" in body_lower[: self.HTML_DETECTION_PREFIX_LENGTH]
            )

            if is_html:
                warnings.warn(
                    "SERP API returned raw HTML instead of parsed JSON. "
                    "This usually means:\n"
                    "1. The zone doesn't support automatic parsing\n"
                    "2. The brd_json=1 parameter didn't work as expected\n"
                    "3. You may need to use a different zone type or endpoint\n\n"
                    "The raw HTML is available in the 'raw_html' field of the response. "
                    "Consider using an HTML parser (e.g., BeautifulSoup) to extract results.",
                    UserWarning,
                    stacklevel=3,
                )
                return {
                    "results": [],
                    "raw_html": body,
                    "status_code": data.get("status_code"),
                }

        results = []
        organic = data.get("organic", [])

        for i, item in enumerate(organic, 1):
            results.append(
                {
                    "position": item.get("rank", i),
                    "title": item.get("title", ""),
                    "url": item.get("link", item.get("url", "")),
                    "description": item.get("description", ""),
                    "displayed_url": item.get("display_link", item.get("displayed_url", "")),
                }
            )

        normalized: NormalizedSERPData = {
            "results": results,
            "total_results": data.get("total_results"),
            "search_info": data.get("search_information", {}),
        }

        if "featured_snippet" in data:
            normalized["featured_snippet"] = data["featured_snippet"]

        if "knowledge_panel" in data:
            normalized["knowledge_panel"] = data["knowledge_panel"]

        if "people_also_ask" in data:
            normalized["people_also_ask"] = data["people_also_ask"]

        if "related_searches" in data:
            normalized["related_searches"] = data["related_searches"]

        if "ads" in data:
            normalized["ads"] = data["ads"]

        return normalized


class BingDataNormalizer(BaseDataNormalizer):
    """Data normalizer for Bing SERP responses."""

    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize Bing SERP data."""
        if isinstance(data, dict):
            return data
        return {"results": data if isinstance(data, list) else []}


class YandexDataNormalizer(BaseDataNormalizer):
    """Data normalizer for Yandex SERP responses."""

    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize Yandex SERP data."""
        if isinstance(data, dict):
            return data
        return {"results": data if isinstance(data, list) else []}
