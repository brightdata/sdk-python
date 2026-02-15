"""
Yelp Businesses Overview dataset.

Business listings from Yelp with ratings, location, and amenities.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
BUSINESS_FIELDS = [
    "business_id",
    "yelp_biz_id",
    "name",
    "is_claimed",
    "is_closed",
]

LOCATION_FIELDS = [
    "address",
    "full_address",
    "city",
    "state",
    "country",
    "zip_code",
    "latitude",
    "longitude",
    "service_area",
]

CONTACT_FIELDS = [
    "website",
    "phone_number",
    "opening_hours",
    "url",
]

RATING_FIELDS = [
    "overall_rating",
    "reviews_count",
    "price_range",
]

CONTENT_FIELDS = [
    "categories",
    "amenities",
    "about_the_business",
    "highlights",
    "services_offered",
    "updates_from_business",
    "images_videos_urls",
]


class YelpBusinesses(BaseDataset):
    """
    Yelp Businesses Overview dataset.

    Business listings with ratings, location data, amenities,
    and contact information from Yelp.

    Field Categories:
        - Business: ID, name, claimed status
        - Location: Address, city, state, coordinates
        - Contact: Website, phone, hours
        - Ratings: Overall rating, review count, price range
        - Content: Categories, amenities, services, photos

    Example:
        >>> yelp = client.datasets.yelp_businesses
        >>> # Discover available fields
        >>> metadata = await yelp.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by rating
        >>> snapshot_id = await yelp(
        ...     filter={"name": "overall_rating", "operator": ">=", "value": "4"},
        ...     records_limit=100
        ... )
        >>> data = await yelp.download(snapshot_id)
    """

    DATASET_ID = "gd_lgugwl0519h1p14rwk"
    NAME = "yelp_businesses"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_business_fields() -> List[str]:
        """Get business identity field names."""
        return BUSINESS_FIELDS.copy()

    @staticmethod
    def get_location_fields() -> List[str]:
        """Get location-related field names."""
        return LOCATION_FIELDS.copy()

    @staticmethod
    def get_contact_fields() -> List[str]:
        """Get contact information field names."""
        return CONTACT_FIELDS.copy()

    @staticmethod
    def get_rating_fields() -> List[str]:
        """Get rating-related field names."""
        return RATING_FIELDS.copy()

    @staticmethod
    def get_content_fields() -> List[str]:
        """Get content field names."""
        return CONTENT_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "business": [],
            "location": [],
            "contact": [],
            "rating": [],
            "content": [],
            "other": [],
        }

        business_set = set(BUSINESS_FIELDS)
        location_set = set(LOCATION_FIELDS)
        contact_set = set(CONTACT_FIELDS)
        rating_set = set(RATING_FIELDS)
        content_set = set(CONTENT_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in business_set:
                result["business"].append(name)
            elif name in location_set:
                result["location"].append(name)
            elif name in contact_set:
                result["contact"].append(name)
            elif name in rating_set:
                result["rating"].append(name)
            elif name in content_set:
                result["content"].append(name)
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
            "business_id",
            "yelp_biz_id",
            "url",
        ]
