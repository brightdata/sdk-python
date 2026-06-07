"""Data normalization for SERP responses."""

import warnings
from abc import ABC, abstractmethod
from typing import Any
from ..types import NormalizedSERPData


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

        general = data.get("general", {}) if isinstance(data.get("general"), dict) else {}

        results = []
        for i, item in enumerate(data.get("organic", []), 1):
            results.append(
                {
                    "position": item.get("rank", i),
                    "title": item.get("title", ""),
                    "url": item.get("link", item.get("url", "")),
                    "description": item.get("description", ""),
                    "displayed_url": item.get("display_link", item.get("displayed_url", "")),
                }
            )

        # `general.results_cnt` is where Bright Data puts the result count for
        # Google (same shape as parsed_bing). Fall back to the old top-level
        # `total_results` key in case the API ever puts it there.
        total = general.get("results_cnt", data.get("total_results"))

        normalized: NormalizedSERPData = {
            "results": results,
            "total_results": total,
            "search_info": general or data.get("search_information", {}),
        }

        # Google-specific top-level sections — pass through only if present.
        # `related` is the actual key; `related_searches` kept for any
        # alternate shape we haven't seen yet.
        for key in (
            "featured_snippet",
            "knowledge_panel",
            "people_also_ask",
            "related",
            "related_searches",
            "ads",
            "videos",
            "perspectives",
            "pagination",
        ):
            if key in data:
                normalized[key] = data[key]

        return normalized


class BingDataNormalizer(BaseDataNormalizer):
    """Data normalizer for Bing SERP responses.

    Shape of `parsed_bing` responses (verified against the live API):
      {
        "general": {"results_cnt": int, "query": str, "search_engine": "bing",
                    "country_code": str, "location": str, "language": str, ...},
        "navigation_tabs": [...],
        "top_pla":    [...],   # top product-listing ads
        "middle_ads": [...],
        "bottom_ads": [...],
        "organic":    [{"link", "title", "description", "display_link",
                        "rank", "global_rank", "tracking_link",
                        "site_name", "extensions"}, ...],
        "related":    [...],
        "pagination": {...}
      }
    """

    HTML_DETECTION_PREFIX_LENGTH = 200

    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize Bing SERP data."""
        if not isinstance(data, (dict, str)):
            return {"results": []}

        if isinstance(data, str):
            return {"results": [], "raw_html": data}

        # Handle raw HTML fallback (zone misconfigured / parser skipped)
        if "body" in data and isinstance(data.get("body"), str):
            body = data["body"]
            body_lower = body.strip().lower()
            is_html = (
                body_lower.startswith(("<html", "<!doctype"))
                or "<html" in body_lower[: self.HTML_DETECTION_PREFIX_LENGTH]
            )

            if is_html:
                warnings.warn(
                    "Bing SERP API returned raw HTML instead of parsed JSON. "
                    "The zone may not have the parsed_bing data_format enabled. "
                    "The raw HTML is available in the 'raw_html' field.",
                    UserWarning,
                    stacklevel=3,
                )
                return {
                    "results": [],
                    "raw_html": body,
                    "status_code": data.get("status_code"),
                }

        general = data.get("general", {}) if isinstance(data.get("general"), dict) else {}

        results = []
        for i, item in enumerate(data.get("organic", []), 1):
            results.append(
                {
                    "position": item.get("rank", i),
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("description", ""),
                    "displayed_url": item.get("display_link", ""),
                }
            )

        normalized: NormalizedSERPData = {
            "results": results,
            "total_results": general.get("results_cnt"),
            "search_info": general,
        }

        # Bing-specific top-level sections — pass through only if present.
        for key in (
            "related",
            "navigation_tabs",
            "top_pla",
            "middle_ads",
            "bottom_ads",
            "pagination",
        ):
            if key in data:
                normalized[key] = data[key]

        return normalized


class YandexDataNormalizer(BaseDataNormalizer):
    """Data normalizer for Yandex SERP responses.

    Bright Data does not provide a parsed JSON format for Yandex (verified:
    brd_json=1 → HTTP 400 "JSON output is not supported"; no parsed_yandex
    data_format exists). Responses always come back as raw HTML. This
    normalizer surfaces the HTML via `raw_html` with an empty `results` list
    so callers can plug in their own parser (e.g. BeautifulSoup).
    """

    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize Yandex SERP data (raw HTML only).

        The base service can hand us the Yandex HTML in two different shapes
        depending on the response path:
          * `{"raw_html": "<html>..."}` — when format=raw came back as text
            and `_execute_serp_request` fell through to the raw-HTML wrapper.
          * `{"body": "<html>...", "status_code": 200}` — when the API
            returned the wrapped JSON envelope and the base layer unwrapped
            it.
        Handle both.
        """
        if isinstance(data, str):
            return {"results": [], "raw_html": data}

        if not isinstance(data, dict):
            return {"results": []}

        raw_html = data.get("raw_html")
        if isinstance(raw_html, str) and raw_html:
            return {"results": [], "raw_html": raw_html}

        body = data.get("body")
        if isinstance(body, str) and body:
            return {
                "results": [],
                "raw_html": body,
                "status_code": data.get("status_code"),
            }

        return {"results": []}
