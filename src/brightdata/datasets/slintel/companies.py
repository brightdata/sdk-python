"""
Slintel 6sense Company Information dataset.

Company profiles from 6sense/Slintel with technographics,
industry data, and business information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
COMPANY_FIELDS = [
    "name",
    "about",
    "num_employees",
    "type",
    "industries",
    "website",
    "logo",
    "location",
    "region",
    "country_code",
    "id",
    "url",
    "stock_symbol",
]

TECH_FIELDS = [
    "techstack_arr",
    "slintel_resources",
]

SOCIAL_FIELDS = [
    "social_media_urls",
    "company_news",
    "last_updated",
]


class SlintelCompanies(BaseDataset):
    """
    Slintel 6sense Company Information dataset.

    Company profiles with technographics, industry classification,
    and business intelligence data.

    Field Categories:
        - Company: Name, description, size, type, industry, location
        - Tech: Technology stack, Slintel resources
        - Social: Social media URLs, company news, last updated

    Example:
        >>> slintel = client.datasets.slintel_companies
        >>> # Discover available fields
        >>> metadata = await slintel.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by country
        >>> snapshot_id = await slintel(
        ...     filter={"name": "country_code", "operator": "=", "value": "US"},
        ...     records_limit=100
        ... )
        >>> data = await slintel.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vilg5a1decoahvgq"
    NAME = "slintel_companies"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company-related field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_tech_fields() -> List[str]:
        """Get technology-related field names."""
        return TECH_FIELDS.copy()

    @staticmethod
    def get_social_fields() -> List[str]:
        """Get social and news field names."""
        return SOCIAL_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "tech": [],
            "social": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        tech_set = set(TECH_FIELDS)
        social_set = set(SOCIAL_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set:
                result["company"].append(name)
            elif name in tech_set or "tech" in name.lower():
                result["tech"].append(name)
            elif name in social_set or "social" in name or "news" in name:
                result["social"].append(name)
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
            "id",
            "url",
            "website",
        ]
