"""
PitchBook Companies Information dataset.

Private equity and venture capital company data including
financing rounds, investments, and deal information.

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
    "company_name",
    "company_socials",
    "year_founded",
    "status",
    "employees",
    "description",
    "contact_information",
]

DEAL_FIELDS = [
    "latest_deal_type",
    "latest_deal_amount",
    "latest_deal_amount_value",
    "latest_deal_date",
    "financing_rounds",
]

INVESTMENT_FIELDS = [
    "investments",
    "all_investments",
]

IP_FIELDS = [
    "patents",
    "patent_activity",
]

OTHER_FIELDS = [
    "competitors",
    "research_analysis",
    "faq",
]


class PitchBookCompanies(BaseDataset):
    """
    PitchBook Companies Information dataset.

    Private company data from PitchBook including financing history,
    deals, investments, patents, and competitive analysis.

    Field Categories:
        - Company: Basic info, socials, status, employees
        - Deals: Latest deal info, financing rounds
        - Investments: Investment history
        - IP: Patents and patent activity
        - Other: Competitors, research, FAQ

    Example:
        >>> pitchbook = client.datasets.pitchbook_companies
        >>> # Discover available fields
        >>> metadata = await pitchbook.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by status
        >>> snapshot_id = await pitchbook(
        ...     filter={"name": "status", "operator": "=", "value": "Private"},
        ...     records_limit=100
        ... )
        >>> data = await pitchbook.download(snapshot_id)
    """

    DATASET_ID = "gd_m4ijiqfp2n9oe3oluj"
    NAME = "pitchbook_companies"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company identity field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_deal_fields() -> List[str]:
        """Get deal-related field names."""
        return DEAL_FIELDS.copy()

    @staticmethod
    def get_investment_fields() -> List[str]:
        """Get investment field names."""
        return INVESTMENT_FIELDS.copy()

    @staticmethod
    def get_ip_fields() -> List[str]:
        """Get intellectual property field names."""
        return IP_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "deals": [],
            "investments": [],
            "ip": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        deal_set = set(DEAL_FIELDS)
        investment_set = set(INVESTMENT_FIELDS)
        ip_set = set(IP_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set:
                result["company"].append(name)
            elif name in deal_set or "deal" in name or "financing" in name:
                result["deals"].append(name)
            elif name in investment_set or "investment" in name:
                result["investments"].append(name)
            elif name in ip_set or "patent" in name:
                result["ip"].append(name)
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
        ]
