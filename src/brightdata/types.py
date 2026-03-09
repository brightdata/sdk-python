"""
Type definitions for Bright Data SDK.

This module provides type definitions for API responses used internally.
"""

from typing import TypedDict, Optional, List, Dict, Any
from typing_extensions import NotRequired


class ZoneInfo(TypedDict, total=False):
    """Zone information from API."""

    name: str
    zone: NotRequired[str]
    status: NotRequired[str]
    plan: NotRequired[Dict[str, Any]]
    created: NotRequired[str]


class AccountInfo(TypedDict):
    """Account information returned by get_account_info()."""

    customer_id: Optional[str]
    zones: List[ZoneInfo]
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

    results: List[SERPOrganicResult]
    total_results: NotRequired[int]
    featured_snippet: NotRequired[SERPFeaturedSnippet]
    knowledge_panel: NotRequired[SERPKnowledgePanel]
    people_also_ask: NotRequired[List[Dict[str, str]]]
    related_searches: NotRequired[List[str]]
    ads: NotRequired[List[Dict[str, Any]]]
    search_info: NotRequired[Dict[str, Any]]
    raw_html: NotRequired[str]


__all__ = [
    "ZoneInfo",
    "AccountInfo",
    "SERPOrganicResult",
    "SERPFeaturedSnippet",
    "SERPKnowledgePanel",
    "NormalizedSERPData",
]
