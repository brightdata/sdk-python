"""
Type definitions for Bright Data SDK.

This module provides type definitions for API responses used internally.
"""

from typing import Any, TypedDict

from typing_extensions import NotRequired


class ZoneInfo(TypedDict, total=False):
    """Zone information from API."""

    name: str
    zone: NotRequired[str]
    status: NotRequired[str]
    plan: NotRequired[dict[str, Any]]
    created: NotRequired[str]


class AccountInfo(TypedDict):
    """Account information returned by get_account_info()."""

    customer_id: str | None
    zones: list[ZoneInfo]
    zone_count: int
    token_valid: bool
    retrieved_at: str


class SERPOrganicResult(TypedDict, total=False):
    """Single organic search result."""

    position: int
    title: str
    url: str
    description: str
    displayed_url: NotRequired[str]


class SERPFeaturedSnippet(TypedDict, total=False):
    """Featured snippet in SERP."""

    title: str
    description: str
    url: str


class SERPKnowledgePanel(TypedDict, total=False):
    """Knowledge panel in SERP."""

    title: str
    type: str
    description: str


class NormalizedSERPData(TypedDict, total=False):
    """Normalized SERP data structure."""

    results: list[SERPOrganicResult]
    total_results: NotRequired[int]
    featured_snippet: NotRequired[SERPFeaturedSnippet]
    knowledge_panel: NotRequired[SERPKnowledgePanel]
    people_also_ask: NotRequired[list[dict[str, str]]]
    related_searches: NotRequired[list[str]]
    ads: NotRequired[list[dict[str, Any]]]
    search_info: NotRequired[dict[str, Any]]
    raw_html: NotRequired[str]


__all__ = [
    "AccountInfo",
    "NormalizedSERPData",
    "SERPFeaturedSnippet",
    "SERPKnowledgePanel",
    "SERPOrganicResult",
    "ZoneInfo",
]
