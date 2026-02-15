"""
G2 Software Product Reviews dataset.

Individual product reviews from G2 with author details and ratings.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
REVIEW_FIELDS = [
    "review_id",
    "date",
    "title",
    "text",
    "tags",
    "stars",
    "review_url",
]

AUTHOR_FIELDS = [
    "author_id",
    "author",
    "position",
    "company_size",
]

PRODUCT_FIELDS = [
    "url",
    "product_url",
    "page",
    "pages",
    "product_name",
    "vendor_name",
    "sort_filter",
]


class G2Reviews(BaseDataset):
    """
    G2 Software Product Reviews dataset.

    Individual product reviews with author information, ratings,
    and detailed review content.

    Field Categories:
        - Review: ID, date, title, text, stars, tags
        - Author: ID, name, position, company size
        - Product: Name, vendor, URL

    Example:
        >>> reviews = client.datasets.g2_reviews
        >>> # Discover available fields
        >>> metadata = await reviews.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by rating
        >>> snapshot_id = await reviews(
        ...     filter={"name": "stars", "operator": ">=", "value": "4"},
        ...     records_limit=100
        ... )
        >>> data = await reviews.download(snapshot_id)
    """

    DATASET_ID = "gd_l88xvdka1uao86xvlb"
    NAME = "g2_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_review_fields() -> List[str]:
        """Get review content field names."""
        return REVIEW_FIELDS.copy()

    @staticmethod
    def get_author_fields() -> List[str]:
        """Get author-related field names."""
        return AUTHOR_FIELDS.copy()

    @staticmethod
    def get_product_fields() -> List[str]:
        """Get product-related field names."""
        return PRODUCT_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "review": [],
            "author": [],
            "product": [],
            "other": [],
        }

        review_set = set(REVIEW_FIELDS)
        author_set = set(AUTHOR_FIELDS)
        product_set = set(PRODUCT_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in review_set or name.startswith("review"):
                result["review"].append(name)
            elif name in author_set or name.startswith("author"):
                result["author"].append(name)
            elif name in product_set or name.startswith("product"):
                result["product"].append(name)
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
            "author_id",
            "review_url",
        ]
