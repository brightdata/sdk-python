"""
World Population dataset.

Dataset ID: gd_lrqeq7u3bil0pmelk

See FIELDS dict for all filterable fields with descriptions.
"""

from typing import TYPE_CHECKING, Dict, Any

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class WorldPopulation(BaseDataset):
    """
    World Population dataset.

    Access world population statistics by country with filtering.

    Example:
        >>> population = client.datasets.world_population
        >>> metadata = await population.get_metadata()
        >>> snapshot_id = await population.filter(
        ...     filter={"name": "continent", "operator": "=", "value": "Europe"},
        ...     records_limit=100
        ... )
        >>> data = await population.download(snapshot_id)
    """

    DATASET_ID = "gd_lrqeq7u3bil0pmelk"
    NAME = "world_population"

    # All available fields with metadata
    FIELDS: Dict[str, Dict[str, Any]] = {
        # Country identification
        "url": {
            "type": "url",
            "description": "Country page URL",
        },
        "country": {
            "type": "text",
            "description": "Country name",
        },
        "abbreviation": {
            "type": "text",
            "description": "Country code (e.g., USA, GBR)",
        },
        "flag_image": {
            "type": "url",
            "description": "Country flag image URL",
        },
        # Geographic info
        "capital": {
            "type": "text",
            "description": "Capital city",
        },
        "continent": {
            "type": "text",
            "description": "Continent name",
        },
        "regions": {
            "type": "array",
            "description": "Geographic regions",
        },
        "largest_cities": {
            "type": "array",
            "description": "Largest cities in the country",
        },
        # Area
        "country_area": {
            "type": "number",
            "description": "Total area (km²)",
        },
        "country_land_area": {
            "type": "number",
            "description": "Land area (km²)",
        },
        "country_density": {
            "type": "number",
            "description": "Population density per km²",
        },
        # Population
        "last_year_population": {
            "type": "number",
            "description": "Population from last year",
        },
        "country_population_rank": {
            "type": "number",
            "description": "World population rank",
        },
        "population_world_percentage": {
            "type": "number",
            "description": "Percentage of world population",
        },
        "population_by_year": {
            "type": "object",
            "description": "Historical population data by year",
        },
        # Population changes
        "annual_population_growth": {
            "type": "text",
            "description": "Annual population growth rate and count",
        },
        "population_change": {
            "type": "number",
            "description": "Total population change",
        },
        "net_change_per_day": {
            "type": "number",
            "description": "Net population change per day",
        },
        # Demographics
        "births_per_day": {
            "type": "number",
            "description": "Average births per day",
        },
        "deaths_per_day": {
            "type": "number",
            "description": "Average deaths per day",
        },
        "emigrations_per_day": {
            "type": "number",
            "description": "Average emigrations per day",
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
    def get_population_fields(cls) -> list:
        """Get all population-related fields."""
        return [name for name in cls.FIELDS.keys() if "population" in name.lower()]

    @classmethod
    def get_demographic_fields(cls) -> list:
        """Get demographic fields (births, deaths, migrations)."""
        return [
            name
            for name in cls.FIELDS.keys()
            if any(kw in name.lower() for kw in ["birth", "death", "emigration", "change"])
        ]
