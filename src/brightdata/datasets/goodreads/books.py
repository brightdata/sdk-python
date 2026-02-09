"""
Goodreads Books dataset.

Dataset ID: gd_lreq6ho72fhvovjj7a

See FIELDS dict for all filterable fields with descriptions.
"""

from typing import TYPE_CHECKING, Dict, Any

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class GoodreadsBooks(BaseDataset):
    """
    Goodreads Books dataset.

    Access Goodreads book records with filtering.

    Example:
        >>> books = client.datasets.goodreads_books
        >>> metadata = await books.get_metadata()
        >>> snapshot_id = await books.filter(
        ...     filter={"name": "star_rating", "operator": ">", "value": 4.0},
        ...     records_limit=100
        ... )
        >>> data = await books.download(snapshot_id)
    """

    DATASET_ID = "gd_lreq6ho72fhvovjj7a"
    NAME = "goodreads_books"

    # All available fields with metadata
    FIELDS: Dict[str, Dict[str, Any]] = {
        # Book identification
        "id": {
            "type": "text",
            "description": "Goodreads book ID",
        },
        "url": {
            "type": "url",
            "description": "Goodreads book page URL",
        },
        "isbn": {
            "type": "text",
            "description": "ISBN number",
        },
        # Book details
        "name": {
            "type": "text",
            "description": "Book title",
        },
        "author": {
            "type": "array",
            "description": "Author name(s)",
        },
        "summary": {
            "type": "text",
            "description": "Book summary/description",
        },
        "genres": {
            "type": "array",
            "description": "Book genres/categories",
        },
        "first_published": {
            "type": "text",
            "description": "First publication date",
        },
        # Ratings & reviews
        "star_rating": {
            "type": "number",
            "description": "Average star rating (0-5)",
        },
        "num_ratings": {
            "type": "number",
            "description": "Total number of ratings",
        },
        "num_reviews": {
            "type": "number",
            "description": "Total number of reviews",
        },
        "community_reviews": {
            "type": "object",
            "description": "Breakdown of reviews by star rating",
        },
        # Author info
        "about_author": {
            "type": "object",
            "description": "Author information (name, books, followers)",
        },
        # Pricing
        "kindle_price": {
            "type": "text",
            "description": "Kindle edition price",
        },
    }

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)

    @classmethod
    def get_field_names(cls) -> list:
        """Get list of all field names."""
        return list(cls.FIELDS.keys())

    @classmethod
    def get_fields_by_type(cls, field_type: str) -> list:
        """Get fields of a specific type (text, number, array, object, url, boolean)."""
        return [name for name, info in cls.FIELDS.items() if info.get("type") == field_type]

    @classmethod
    def get_rating_fields(cls) -> list:
        """Get all rating-related fields."""
        return [
            name
            for name in cls.FIELDS.keys()
            if "rating" in name.lower() or "review" in name.lower()
        ]
