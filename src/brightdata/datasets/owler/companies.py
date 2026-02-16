"""
Owler Companies Information dataset.

Company profiles from Owler with competitive intelligence,
funding data, and business metrics.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
COMPANY_FIELDS = [
    "companyId",
    "companyName",
    "shortName",
    "ownership",
    "industrySectors",
    "industries",
    "website",
    "domainName",
    "phoneNumber",
    "description",
    "founded",
    "status",
    "teamName",
    "url",
    "cpLink",
    "sicCode",
]

EMPLOYEE_REVENUE_FIELDS = [
    "employeeCount",
    "formattedEmployeeCount",
    "employeeRange",
    "revenue",
    "revenueRange",
    "formattedRevenue",
    "est_annual_revenue",
    "est_employees",
    "employeeHistory",
    "revenueHistory",
    "revenueEmpHistory",
]

LOCATION_FIELDS = [
    "country",
    "city",
    "state",
    "zipcode",
    "street1Address",
    "location",
    "DMACode",
]

FUNDING_FIELDS = [
    "totalAcquisitions",
    "totalCompetitors",
    "totalFundings",
    "totalInvestments",
    "totalFunding",
    "formattedFunding",
    "companyAcquisitionInfo",
    "companyFundingInfo",
    "fundingChartInfo",
]

LEADERSHIP_FIELDS = [
    "ceoDetail",
    "leaderShipDetails",
]

CONTENT_FIELDS = [
    "summarySection",
    "keyHighlights",
    "trendingNews",
    "newsPageFeed",
    "seoTextMap",
]

RELATED_FIELDS = [
    "cg",
    "cgCompaniesCount",
    "companies",
    "recommendedCompanies",
    "trendingCompanies",
]


class OwlerCompanies(BaseDataset):
    """
    Owler Companies Information dataset.

    Company profiles with competitive intelligence, funding history,
    employee and revenue metrics, and leadership information.

    Field Categories:
        - Company: Name, ownership, industry, website, status
        - Employee/Revenue: Counts, ranges, history
        - Location: Address, city, state, country
        - Funding: Acquisitions, investments, funding rounds
        - Leadership: CEO details, leadership team
        - Content: Summary, highlights, news
        - Related: Competitors, recommended companies

    Example:
        >>> owler = client.datasets.owler_companies
        >>> # Discover available fields
        >>> metadata = await owler.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by country
        >>> snapshot_id = await owler(
        ...     filter={"name": "country", "operator": "=", "value": "USA"},
        ...     records_limit=100
        ... )
        >>> data = await owler.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vilaxi10wutoage7"
    NAME = "owler_companies"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company-related field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_employee_revenue_fields() -> List[str]:
        """Get employee and revenue field names."""
        return EMPLOYEE_REVENUE_FIELDS.copy()

    @staticmethod
    def get_location_fields() -> List[str]:
        """Get location-related field names."""
        return LOCATION_FIELDS.copy()

    @staticmethod
    def get_funding_fields() -> List[str]:
        """Get funding-related field names."""
        return FUNDING_FIELDS.copy()

    @staticmethod
    def get_leadership_fields() -> List[str]:
        """Get leadership-related field names."""
        return LEADERSHIP_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "employee_revenue": [],
            "location": [],
            "funding": [],
            "leadership": [],
            "content": [],
            "related": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        emp_rev_set = set(EMPLOYEE_REVENUE_FIELDS)
        location_set = set(LOCATION_FIELDS)
        funding_set = set(FUNDING_FIELDS)
        leadership_set = set(LEADERSHIP_FIELDS)
        content_set = set(CONTENT_FIELDS)
        related_set = set(RELATED_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set or name.startswith("company"):
                result["company"].append(name)
            elif name in emp_rev_set or "employee" in name.lower() or "revenue" in name.lower():
                result["employee_revenue"].append(name)
            elif name in location_set:
                result["location"].append(name)
            elif name in funding_set or "funding" in name.lower() or "acquisition" in name.lower():
                result["funding"].append(name)
            elif name in leadership_set or "ceo" in name.lower() or "leader" in name.lower():
                result["leadership"].append(name)
            elif name in content_set or "news" in name.lower() or "seo" in name.lower():
                result["content"].append(name)
            elif name in related_set or "competitor" in name.lower():
                result["related"].append(name)
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
            "companyId",
            "url",
            "cpLink",
            "domainName",
        ]
