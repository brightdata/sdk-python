"""
Manta Businesses dataset.

Business listings from Manta with company details,
location, contact information, and revenue estimates.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
COMPANY_FIELDS = [
    "company_name",
    "company_id",
    "business_categories",
    "sic_code",
    "description",
    "services",
    "owner",
    "manta_link",
    "url",
]

LOCATION_FIELDS = [
    "business_state",
    "business_city",
    "business_country",
    "business_zip_code",
    "business_street_name",
    "latitude",
    "longitude",
    "location_type",
]

CONTACT_FIELDS = [
    "phone_number",
    "website",
    "links",
]

OPERATING_FIELDS = [
    "opening_hours",
    "closing_hours",
    "avg_opening_hour",
    "avg_closing_hour",
    "closed_on",
    "year_established",
]

METRICS_FIELDS = [
    "estimated_annual_revenue",
    "num_employees",
    "review_count",
    "reviews",
]


class MantaBusinesses(BaseDataset):
    """
    Manta Businesses dataset.

    Business listings with company details, location data,
    operating hours, and financial estimates.

    Field Categories:
        - Company: Name, categories, SIC code, description, owner
        - Location: Address, city, state, country, coordinates
        - Contact: Phone, website, links
        - Operating: Hours, established date
        - Metrics: Revenue, employees, reviews

    Example:
        >>> manta = client.datasets.manta_businesses
        >>> # Discover available fields
        >>> metadata = await manta.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by state
        >>> snapshot_id = await manta(
        ...     filter={"name": "business_state", "operator": "=", "value": "California"},
        ...     records_limit=100
        ... )
        >>> data = await manta.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vil1d81g0u8763b2"
    NAME = "manta_businesses"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company-related field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_location_fields() -> List[str]:
        """Get location-related field names."""
        return LOCATION_FIELDS.copy()

    @staticmethod
    def get_contact_fields() -> List[str]:
        """Get contact-related field names."""
        return CONTACT_FIELDS.copy()

    @staticmethod
    def get_operating_fields() -> List[str]:
        """Get operating hours field names."""
        return OPERATING_FIELDS.copy()

    @staticmethod
    def get_metrics_fields() -> List[str]:
        """Get business metrics field names."""
        return METRICS_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "location": [],
            "contact": [],
            "operating": [],
            "metrics": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        location_set = set(LOCATION_FIELDS)
        contact_set = set(CONTACT_FIELDS)
        operating_set = set(OPERATING_FIELDS)
        metrics_set = set(METRICS_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set or name.startswith("company"):
                result["company"].append(name)
            elif name in location_set or name.startswith("business_"):
                result["location"].append(name)
            elif name in contact_set:
                result["contact"].append(name)
            elif name in operating_set or "hour" in name.lower():
                result["operating"].append(name)
            elif name in metrics_set or "revenue" in name.lower() or "employee" in name.lower():
                result["metrics"].append(name)
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
            "manta_link",
        ]
