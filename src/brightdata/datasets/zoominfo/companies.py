"""
ZoomInfo Companies Information dataset.

Company and contact data from ZoomInfo including financials,
employee counts, tech stack, and org charts.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
COMPANY_FIELDS = [
    "url",
    "id",
    "name",
    "description",
    "website",
    "industry",
    "headquarters",
    "phone_number",
]

FINANCIAL_FIELDS = [
    "revenue",
    "revenue_currency",
    "revenue_text",
    "stock_symbol",
    "total_funding_amount",
    "most_recent_funding_amount",
    "funding_currency",
    "funding_rounds",
]

EMPLOYEE_FIELDS = [
    "employees",
    "employees_text",
    "total_employees",
    "c_level_employees",
    "vp_level_employees",
    "director_level_employees",
    "manager_level_employees",
    "non_manager_employees",
]

LEADERSHIP_FIELDS = [
    "leadership",
    "ceo",
    "top_contacts",
    "org_chart",
    "ceo_rating",
]

TECH_FIELDS = [
    "products_owned",
    "tech_stack",
]

OTHER_FIELDS = [
    "popular_searches",
    "business_classification_codes",
    "social_media",
    "enps score",
    "similar_companies",
    "email_formats",
    "recent_scoops",
    "news_and_media",
]


class ZoomInfoCompanies(BaseDataset):
    """
    ZoomInfo Companies Information dataset.

    Comprehensive company data including financials, employee counts,
    leadership contacts, tech stack, and organizational structure.

    Field Categories:
        - Company: Basic info, website, industry
        - Financial: Revenue, funding, stock symbol
        - Employees: Counts by level (C-level, VP, Director, etc.)
        - Leadership: CEO, contacts, org chart
        - Tech: Tech stack, products owned

    Example:
        >>> zoominfo = client.datasets.zoominfo_companies
        >>> # Discover available fields
        >>> metadata = await zoominfo.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by industry
        >>> snapshot_id = await zoominfo(
        ...     filter={"name": "industry", "operator": "=", "value": "Technology"},
        ...     records_limit=100
        ... )
        >>> data = await zoominfo.download(snapshot_id)
    """

    DATASET_ID = "gd_m0ci4a4ivx3j5l6nx"
    NAME = "zoominfo_companies"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company identity field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_financial_fields() -> List[str]:
        """Get financial-related field names."""
        return FINANCIAL_FIELDS.copy()

    @staticmethod
    def get_employee_fields() -> List[str]:
        """Get employee count field names."""
        return EMPLOYEE_FIELDS.copy()

    @staticmethod
    def get_leadership_fields() -> List[str]:
        """Get leadership and contact field names."""
        return LEADERSHIP_FIELDS.copy()

    @staticmethod
    def get_tech_fields() -> List[str]:
        """Get technology-related field names."""
        return TECH_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "financial": [],
            "employees": [],
            "leadership": [],
            "tech": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        financial_set = set(FINANCIAL_FIELDS)
        employee_set = set(EMPLOYEE_FIELDS)
        leadership_set = set(LEADERSHIP_FIELDS)
        tech_set = set(TECH_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set:
                result["company"].append(name)
            elif name in financial_set or "funding" in name or "revenue" in name:
                result["financial"].append(name)
            elif name in employee_set or "employee" in name:
                result["employees"].append(name)
            elif name in leadership_set:
                result["leadership"].append(name)
            elif name in tech_set:
                result["tech"].append(name)
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
