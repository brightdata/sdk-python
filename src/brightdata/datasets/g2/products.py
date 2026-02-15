"""
G2 Software Product Overview dataset.

Software product listings from G2 with ratings, reviews, pricing,
and competitive analysis.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
PRODUCT_FIELDS = [
    "url",
    "product_name",
    "product_id",
    "product_url",
    "software_product_id",
    "numerical_id",
    "logo",
    "description",
    "overview",
    "what_is_description",
]

SELLER_FIELDS = [
    "seller",
    "ownership",
    "seller_website",
    "headquarters",
    "seller_description",
    "year_founded",
    "overview_provided_by",
]

RATING_FIELDS = [
    "rating",
    "reviews_count",
    "rating_split",
    "pros_list",
    "cons_list",
    "reviews",
    "highest_rated_features",
]

COMPETITIVE_FIELDS = [
    "competitors",
    "position_against_competitors",
    "top_alternatives",
    "top_alternatives_url",
]

CONTENT_FIELDS = [
    "pricing",
    "full_pricing_page",
    "official_screenshots",
    "official_downloads",
    "official_videos",
    "Features",
]

CATEGORY_FIELDS = [
    "categories",
    "main_category",
    "main_subject",
    "languages_supported",
    "badge",
    "claimed",
    "region",
    "country_code",
]


class G2Products(BaseDataset):
    """
    G2 Software Product Overview dataset.

    Software product listings with ratings, reviews, pricing,
    features, and competitive positioning from G2.

    Field Categories:
        - Product: Name, ID, description, overview
        - Seller: Company info, website, headquarters
        - Rating: Scores, reviews, pros/cons
        - Competitive: Competitors, alternatives, positioning
        - Content: Pricing, screenshots, videos, features
        - Category: Categories, languages, region

    Example:
        >>> g2 = client.datasets.g2_products
        >>> # Discover available fields
        >>> metadata = await g2.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by rating
        >>> snapshot_id = await g2(
        ...     filter={"name": "rating", "operator": ">=", "value": "4.5"},
        ...     records_limit=100
        ... )
        >>> data = await g2.download(snapshot_id)
    """

    DATASET_ID = "gd_l88xp4k01qnhvyqlvw"
    NAME = "g2_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_product_fields() -> List[str]:
        """Get product identity field names."""
        return PRODUCT_FIELDS.copy()

    @staticmethod
    def get_seller_fields() -> List[str]:
        """Get seller/vendor field names."""
        return SELLER_FIELDS.copy()

    @staticmethod
    def get_rating_fields() -> List[str]:
        """Get rating and review field names."""
        return RATING_FIELDS.copy()

    @staticmethod
    def get_competitive_fields() -> List[str]:
        """Get competitive analysis field names."""
        return COMPETITIVE_FIELDS.copy()

    @staticmethod
    def get_content_fields() -> List[str]:
        """Get content field names (pricing, media)."""
        return CONTENT_FIELDS.copy()

    @staticmethod
    def get_category_fields() -> List[str]:
        """Get category and classification field names."""
        return CATEGORY_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "product": [],
            "seller": [],
            "rating": [],
            "competitive": [],
            "content": [],
            "category": [],
            "other": [],
        }

        product_set = set(PRODUCT_FIELDS)
        seller_set = set(SELLER_FIELDS)
        rating_set = set(RATING_FIELDS)
        competitive_set = set(COMPETITIVE_FIELDS)
        content_set = set(CONTENT_FIELDS)
        category_set = set(CATEGORY_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in product_set or name.startswith("product_"):
                result["product"].append(name)
            elif name in seller_set or name.startswith("seller"):
                result["seller"].append(name)
            elif name in rating_set or "rating" in name or "review" in name:
                result["rating"].append(name)
            elif name in competitive_set or "competitor" in name or "alternative" in name:
                result["competitive"].append(name)
            elif name in content_set or "pricing" in name:
                result["content"].append(name)
            elif name in category_set or "category" in name:
                result["category"].append(name)
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
            "product_id",
            "software_product_id",
            "numerical_id",
            "url",
        ]
