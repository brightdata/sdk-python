"""
VentureRadar Company Information dataset.

Company profiles from VentureRadar with startup intelligence,
funding signals, and competitive data.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
COMPANY_FIELDS = [
    "url",
    "name",
    "title",
    "description",
    "description_source",
    "location",
    "country_code",
    "ownership",
    "founded",
    "company_id",
    "website",
]

SCORES_FIELDS = [
    "score",
    "auto_analyst_score",
    "website_popularity",
    "website_popularity_graph",
    "sub_scores",
]

CONTACT_FIELDS = [
    "email",
    "linkedin",
    "twitter",
    "keywords",
]

INTELLIGENCE_FIELDS = [
    "similar",
    "hostorical_profiles",
    "areas_of_focus",
    "cards",
    "funding_signals",
    "employee_satisfaction",
]


class VentureRadarCompanies(BaseDataset):
    """
    VentureRadar Company Information dataset.

    Startup and company profiles with analyst scores,
    funding signals, and competitive intelligence.

    Field Categories:
        - Company: Name, description, location, ownership, founded
        - Scores: Analyst scores, website popularity, sub-scores
        - Contact: Email, LinkedIn, Twitter, keywords
        - Intelligence: Similar companies, funding signals, focus areas

    Example:
        >>> vr = client.datasets.ventureradar_companies
        >>> # Discover available fields
        >>> metadata = await vr.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by country
        >>> snapshot_id = await vr(
        ...     filter={"name": "country_code", "operator": "=", "value": "US"},
        ...     records_limit=100
        ... )
        >>> data = await vr.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vilsfd1xpsndbtpr"
    NAME = "ventureradar_companies"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company-related field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_scores_fields() -> List[str]:
        """Get scores and metrics field names."""
        return SCORES_FIELDS.copy()

    @staticmethod
    def get_contact_fields() -> List[str]:
        """Get contact and social field names."""
        return CONTACT_FIELDS.copy()

    @staticmethod
    def get_intelligence_fields() -> List[str]:
        """Get business intelligence field names."""
        return INTELLIGENCE_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "scores": [],
            "contact": [],
            "intelligence": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        scores_set = set(SCORES_FIELDS)
        contact_set = set(CONTACT_FIELDS)
        intelligence_set = set(INTELLIGENCE_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set:
                result["company"].append(name)
            elif name in scores_set or "score" in name.lower() or "popularity" in name.lower():
                result["scores"].append(name)
            elif name in contact_set:
                result["contact"].append(name)
            elif name in intelligence_set or "funding" in name.lower() or "similar" in name.lower():
                result["intelligence"].append(name)
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
            "company_id",
            "url",
            "website",
        ]
