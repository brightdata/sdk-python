"""
Type definitions for Bright Data SDK.

Provides TypedDict definitions for payloads, responses, and configuration
for 100% type safety and excellent developer experience.
"""

from typing import TypedDict, Optional, List, Literal, Union, Any, Dict
from typing_extensions import NotRequired


class DatasetTriggerPayload(TypedDict, total=False):
    """Payload for /datasets/v3/trigger endpoint."""
    url: str
    keyword: str
    location: str
    country: str
    max_results: int


class AmazonProductPayload(TypedDict, total=False):
    """Amazon product scrape payload."""
    url: str  # Required
    reviews_count: NotRequired[int]
    images_count: NotRequired[int]


class AmazonReviewPayload(TypedDict, total=False):
    """Amazon review scrape payload."""
    url: str  # Required
    pastDays: NotRequired[int]
    keyWord: NotRequired[str]
    numOfReviews: NotRequired[int]


class LinkedInProfilePayload(TypedDict, total=False):
    """LinkedIn profile scrape payload."""
    url: str  # Required


class LinkedInJobPayload(TypedDict, total=False):
    """LinkedIn job scrape payload."""
    url: str  # Required


class LinkedInCompanyPayload(TypedDict, total=False):
    """LinkedIn company scrape payload."""
    url: str  # Required


class LinkedInPostPayload(TypedDict, total=False):
    """LinkedIn post scrape payload."""
    url: str  # Required


class LinkedInProfileSearchPayload(TypedDict, total=False):
    """LinkedIn profile search payload."""
    firstName: str  # Required
    lastName: NotRequired[str]
    title: NotRequired[str]
    company: NotRequired[str]
    location: NotRequired[str]
    max_results: NotRequired[int]


class LinkedInJobSearchPayload(TypedDict, total=False):
    """LinkedIn job search payload."""
    url: NotRequired[str]
    keyword: NotRequired[str]
    location: NotRequired[str]
    country: NotRequired[str]
    timeRange: NotRequired[str]
    jobType: NotRequired[str]
    experienceLevel: NotRequired[str]
    remote: NotRequired[bool]
    company: NotRequired[str]
    locationRadius: NotRequired[str]


class LinkedInPostSearchPayload(TypedDict, total=False):
    """LinkedIn post search payload."""
    profile_url: str  # Required
    start_date: NotRequired[str]
    end_date: NotRequired[str]


class ChatGPTPromptPayload(TypedDict, total=False):
    """ChatGPT prompt payload."""
    prompt: str  # Required
    country: NotRequired[str]
    web_search: NotRequired[bool]
    additional_prompt: NotRequired[str]


class FacebookPostsProfilePayload(TypedDict, total=False):
    """Facebook posts by profile URL payload."""
    url: str  # Required
    num_of_posts: NotRequired[int]
    posts_to_not_include: NotRequired[List[str]]
    start_date: NotRequired[str]  # MM-DD-YYYY
    end_date: NotRequired[str]  # MM-DD-YYYY


class FacebookPostsGroupPayload(TypedDict, total=False):
    """Facebook posts by group URL payload."""
    url: str  # Required
    num_of_posts: NotRequired[int]
    posts_to_not_include: NotRequired[List[str]]
    start_date: NotRequired[str]  # MM-DD-YYYY
    end_date: NotRequired[str]  # MM-DD-YYYY


class FacebookPostPayload(TypedDict, total=False):
    """Facebook post by URL payload."""
    url: str  # Required


class FacebookCommentsPayload(TypedDict, total=False):
    """Facebook comments by post URL payload."""
    url: str  # Required
    num_of_comments: NotRequired[int]
    comments_to_not_include: NotRequired[List[str]]
    start_date: NotRequired[str]  # MM-DD-YYYY
    end_date: NotRequired[str]  # MM-DD-YYYY


class FacebookReelsPayload(TypedDict, total=False):
    """Facebook reels by profile URL payload."""
    url: str  # Required
    num_of_posts: NotRequired[int]
    posts_to_not_include: NotRequired[List[str]]
    start_date: NotRequired[str]
    end_date: NotRequired[str]


class InstagramProfilePayload(TypedDict, total=False):
    """Instagram profile by URL payload."""
    url: str  # Required


class InstagramPostPayload(TypedDict, total=False):
    """Instagram post by URL payload."""
    url: str  # Required


class InstagramCommentPayload(TypedDict, total=False):
    """Instagram comments by post URL payload."""
    url: str  # Required


class InstagramReelPayload(TypedDict, total=False):
    """Instagram reel by URL payload."""
    url: str  # Required


class InstagramPostsDiscoverPayload(TypedDict, total=False):
    """Instagram posts discovery by URL payload."""
    url: str  # Required
    num_of_posts: NotRequired[int]
    posts_to_not_include: NotRequired[List[str]]
    start_date: NotRequired[str]  # MM-DD-YYYY
    end_date: NotRequired[str]  # MM-DD-YYYY
    post_type: NotRequired[str]  # e.g., "post", "reel"


class InstagramReelsDiscoverPayload(TypedDict, total=False):
    """Instagram reels discovery by URL payload."""
    url: str  # Required
    num_of_posts: NotRequired[int]
    posts_to_not_include: NotRequired[List[str]]
    start_date: NotRequired[str]  # MM-DD-YYYY
    end_date: NotRequired[str]  # MM-DD-YYYY


class TriggerResponse(TypedDict):
    """Response from /datasets/v3/trigger."""
    snapshot_id: str


class ProgressResponse(TypedDict):
    """Response from /datasets/v3/progress/{snapshot_id}."""
    status: Literal["ready", "in_progress", "error", "failed"]
    progress: NotRequired[int]


class SnapshotResponse(TypedDict):
    """Response from /datasets/v3/snapshot/{snapshot_id}."""
    data: List[Dict[str, Any]]


class ZoneInfo(TypedDict, total=False):
    """Zone information from API."""
    name: str
    zone: NotRequired[str]
    status: NotRequired[str]
    plan: NotRequired[Dict[str, Any]]
    created: NotRequired[str]


DeviceType = Literal["desktop", "mobile", "tablet"]
ResponseFormat = Literal["raw", "json"]
HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
SearchEngine = Literal["google", "bing", "yandex"]
Platform = Literal["amazon", "linkedin", "chatgpt", "instagram", "reddit"]


URLParam = Union[str, List[str]]
OptionalURLParam = Optional[Union[str, List[str]]]
StringParam = Union[str, List[str]]
OptionalStringParam = Optional[Union[str, List[str]]]


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
    # Payloads
    "DatasetTriggerPayload",
    "AmazonProductPayload",
    "AmazonReviewPayload",
    "LinkedInProfilePayload",
    "LinkedInJobPayload",
    "LinkedInCompanyPayload",
    "LinkedInPostPayload",
    "LinkedInProfileSearchPayload",
    "LinkedInJobSearchPayload",
    "LinkedInPostSearchPayload",
    "ChatGPTPromptPayload",
    "FacebookPostsProfilePayload",
    "FacebookPostsGroupPayload",
    "FacebookPostPayload",
    "FacebookCommentsPayload",
    "FacebookReelsPayload",
    # Instagram Payloads
    "InstagramProfilePayload",
    "InstagramPostPayload",
    "InstagramCommentPayload",
    "InstagramReelPayload",
    "InstagramPostsDiscoverPayload",
    "InstagramReelsDiscoverPayload",
    # Responses
    "TriggerResponse",
    "ProgressResponse",
    "SnapshotResponse",
    "ZoneInfo",
    "AccountInfo",
    # SERP
    "SERPOrganicResult",
    "SERPFeaturedSnippet",
    "SERPKnowledgePanel",
    "NormalizedSERPData",
    # Literals
    "DeviceType",
    "ResponseFormat",
    "HTTPMethod",
    "SearchEngine",
    "Platform",
    # Aliases
    "URLParam",
    "OptionalURLParam",
    "StringParam",
    "OptionalStringParam",
]
