"""
IMDB Movies dataset.

Dataset ID: gd_l1vikf2h1a4t6x8qzu

See FIELDS dict for all filterable fields with descriptions.
"""

from typing import TYPE_CHECKING, Dict, Any

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class IMDBMovies(BaseDataset):
    """
    IMDB Movies dataset.

    Access IMDB movie/TV records with filtering.

    Example:
        >>> movies = client.datasets.imdb_movies
        >>> metadata = await movies.get_metadata()
        >>> snapshot_id = await movies.filter(
        ...     filter={"name": "imdb_rating", "operator": ">", "value": 8.0},
        ...     records_limit=100
        ... )
        >>> data = await movies.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vikf2h1a4t6x8qzu"
    NAME = "imdb_movies"

    # All available fields with metadata
    FIELDS: Dict[str, Dict[str, Any]] = {
        # Core identification
        "id": {
            "type": "text",
            "description": "IMDB title ID (e.g., tt5931912)",
        },
        "title": {
            "type": "text",
            "description": "Movie/show title",
        },
        "url": {
            "type": "url",
            "description": "IMDB page URL",
        },
        "media_type": {
            "type": "text",
            "description": "Type of media (Feature Film, Documentary, etc.)",
        },
        # Ratings & reviews
        "imdb_rating": {
            "type": "number",
            "description": "IMDB rating (0-10)",
        },
        "imdb_rating_count": {
            "type": "number",
            "description": "Number of IMDB ratings",
        },
        "popularity": {
            "type": "number",
            "description": "Popularity score",
        },
        "review_count": {
            "type": "number",
            "description": "Number of user reviews",
        },
        "review_rating": {
            "type": "number",
            "description": "Average user review rating",
        },
        "critics_review_count": {
            "type": "number",
            "description": "Number of critic reviews",
        },
        "featured_review": {
            "type": "text",
            "description": "Featured user review text",
        },
        # Content details
        "genres": {
            "type": "array",
            "description": "List of genres (e.g., Drama, Comedy)",
        },
        "presentation": {
            "type": "text",
            "description": "Short presentation/tagline",
        },
        "storyline": {
            "type": "text",
            "description": "Plot summary/storyline",
        },
        "comment": {
            "type": "text",
            "description": "Additional comments",
        },
        # Cast & crew
        "credit": {
            "type": "array",
            "description": "Credits (directors, writers, etc.)",
        },
        "top_cast": {
            "type": "array",
            "description": "Top cast members with character names",
        },
        # Release details
        "details_release_date": {
            "type": "text",
            "description": "Release date",
        },
        "details_countries_of_origin": {
            "type": "text",
            "description": "Countries of origin",
        },
        "details_language": {
            "type": "text",
            "description": "Languages",
        },
        "details_also_known_as": {
            "type": "text",
            "description": "Alternative titles",
        },
        "details_filming_locations": {
            "type": "text",
            "description": "Filming locations",
        },
        "details_production_companies": {
            "type": "text",
            "description": "Production companies",
        },
        "details_official_site": {
            "type": "url",
            "description": "Official website URL",
        },
        # Technical specs
        "specs_color": {
            "type": "text",
            "description": "Color format (Color, Black and White)",
        },
        "specs_sound_mix": {
            "type": "text",
            "description": "Sound mix format",
        },
        "specs_aspect_ratio": {
            "type": "text",
            "description": "Aspect ratio",
        },
        # Media
        "poster_url": {
            "type": "url",
            "description": "Movie poster image URL",
        },
        "videos": {
            "type": "array",
            "description": "Video links (trailers, clips)",
        },
        "photos": {
            "type": "array",
            "description": "Photo gallery links",
        },
        # Awards & box office
        "awards": {
            "type": "text",
            "description": "Awards and nominations",
        },
        "boxoffice_budget": {
            "type": "text",
            "description": "Production budget",
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
        rating_keywords = ["rating", "review", "score"]
        return [
            name for name in cls.FIELDS.keys() if any(kw in name.lower() for kw in rating_keywords)
        ]
