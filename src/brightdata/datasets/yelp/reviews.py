"""
Yelp Business Reviews dataset.

Individual business reviews from Yelp with reviewer details,
ratings, and reactions.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
BUSINESS_FIELDS = [
    "business_id",
    "business_name",
    "url",
]

REVIEW_FIELDS = [
    "review_id",
    "rating",
    "date",
    "date_iso_format",
    "content",
    "review_image",
    "reactions",
    "replies",
    "review_order",
    "recommended_review",
]

REVIEWER_FIELDS = [
    "review_auther",  # JSON with Friends, Image, Location, Photos, Reviews_made, URL
    "profile_pic_url",
    "elite_status",
    "check-in_status",
]


class YelpReviews(BaseDataset):
    """
    Yelp Business Reviews dataset.

    Individual reviews for businesses with reviewer information,
    ratings, reactions, and reply data.

    Field Categories:
        - Business: ID, name, URL
        - Review: Content, rating, date, images, reactions, replies
        - Reviewer: Author info, profile pic, elite status, check-ins

    Example:
        >>> reviews = client.datasets.yelp_reviews
        >>> # Discover available fields
        >>> metadata = await reviews.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by rating
        >>> snapshot_id = await reviews(
        ...     filter={"name": "rating", "operator": ">=", "value": "4"},
        ...     records_limit=100
        ... )
        >>> data = await reviews.download(snapshot_id)
    """

    DATASET_ID = "gd_lgzhlu9323u3k24jkv"
    NAME = "yelp_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_business_fields() -> List[str]:
        """Get business-related field names."""
        return BUSINESS_FIELDS.copy()

    @staticmethod
    def get_review_fields() -> List[str]:
        """Get review content field names."""
        return REVIEW_FIELDS.copy()

    @staticmethod
    def get_reviewer_fields() -> List[str]:
        """Get reviewer-related field names."""
        return REVIEWER_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "business": [],
            "review": [],
            "reviewer": [],
            "other": [],
        }

        business_set = set(BUSINESS_FIELDS)
        review_set = set(REVIEW_FIELDS)
        reviewer_set = set(REVIEWER_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in business_set or name.startswith("business"):
                result["business"].append(name)
            elif name in review_set or name.startswith("review"):
                result["review"].append(name)
            elif name in reviewer_set or name.startswith("reviewer") or "author" in name.lower():
                result["reviewer"].append(name)
            else:
                result["other"].append(name)

        for category in result:
            result[category] = sorted(result[category])

        self._fields_by_category = result
        return result

    async def search_fields(self, keyword: str) -> List[str]:
        """Search for fields containing a keyword."""
        metadata = await self.get_metadata()
        keyword_lower = keyword.lower()

        matches = []
        for name, field_info in metadata.fields.items():
            if keyword_lower in name.lower():
                matches.append(name)
            elif field_info.description and keyword_lower in field_info.description.lower():
                matches.append(name)

        return sorted(matches)

    @staticmethod
    def get_identifier_fields() -> List[str]:
        """Get fields that can be used as unique identifiers."""
        return [
            "review_id",
            "business_id",
            "url",
        ]
