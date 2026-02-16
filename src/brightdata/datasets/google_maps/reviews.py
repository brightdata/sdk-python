"""
Google Maps Reviews dataset.

Reviews and ratings from Google Maps places including
reviewer information, place details, and owner responses.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
PLACE_FIELDS = [
    "url",
    "place_id",
    "place_name",
    "country",
    "address",
    "category",
    "cid",
    "fid_location",
    "place_general_rating",
    "overall_place_riviews",
    "questions_answers",
]

REVIEWER_FIELDS = [
    "reviewer_name",
    "reviews_by_reviewer",
    "photos_by_reviewer",
    "reviewer_url",
    "local_guide",
    "profile_pic_url",
]

REVIEW_FIELDS = [
    "review_id",
    "review_rating",
    "review",
    "review_date",
    "number_of_likes",
    "response_of_owner",
    "response_date",
    "photos",
    "review_details",
]


class GoogleMapsReviews(BaseDataset):
    """
    Google Maps Reviews dataset.

    Reviews and ratings from Google Maps places including detailed
    reviewer information, place metadata, and business owner responses.

    Field Categories:
        - Place: Location info, ratings, address, category
        - Reviewer: Name, profile, local guide status
        - Review: Rating, text, date, photos, owner response

    Example:
        >>> reviews = client.datasets.google_maps_reviews
        >>> # Discover available fields
        >>> metadata = await reviews.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Get fields by category
        >>> place_fields = reviews.get_place_fields()
        >>> review_fields = reviews.get_review_fields()
        >>>
        >>> # Filter reviews
        >>> snapshot_id = await reviews(
        ...     filter={"name": "review_rating", "operator": ">=", "value": "4"},
        ...     records_limit=100
        ... )
        >>> data = await reviews.download(snapshot_id)
    """

    DATASET_ID = "gd_luzfs1dn2oa0teb81"
    NAME = "google_maps_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_place_fields() -> List[str]:
        """
        Get place-related field names.

        Returns:
            List of place field names
        """
        return PLACE_FIELDS.copy()

    @staticmethod
    def get_reviewer_fields() -> List[str]:
        """
        Get reviewer-related field names.

        Returns:
            List of reviewer field names
        """
        return REVIEWER_FIELDS.copy()

    @staticmethod
    def get_review_fields() -> List[str]:
        """
        Get review-related field names.

        Returns:
            List of review field names
        """
        return REVIEW_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """
        Get all fields grouped by category.

        Returns:
            Dict mapping category name to list of field names
        """
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "place": [],
            "reviewer": [],
            "review": [],
            "other": [],
        }

        place_set = set(PLACE_FIELDS)
        reviewer_set = set(REVIEWER_FIELDS)
        review_set = set(REVIEW_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in place_set or name.startswith("place_"):
                result["place"].append(name)
            elif name in reviewer_set or name.startswith("reviewer"):
                result["reviewer"].append(name)
            elif name in review_set or name.startswith("review"):
                result["review"].append(name)
            else:
                result["other"].append(name)

        for category in result:
            result[category] = sorted(result[category])

        self._fields_by_category = result
        return result

    async def search_fields(self, keyword: str) -> List[str]:
        """
        Search for fields containing a keyword.

        Args:
            keyword: Keyword to search for (case-insensitive)

        Returns:
            List of matching field names
        """
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
        """
        Get fields that can be used as unique identifiers.

        Returns:
            List of identifier field names
        """
        return [
            "review_id",
            "place_id",
            "cid",
            "url",
        ]
