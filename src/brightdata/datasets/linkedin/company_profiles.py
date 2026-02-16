"""
LinkedIn Company Profiles dataset.

Dataset ID: gd_l1vikfnt1wgvvqz95w
Records: 58.5M+ companies

See FIELDS dict for all filterable fields with descriptions.
"""

from typing import TYPE_CHECKING, Dict, Any

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class LinkedInCompanyProfiles(BaseDataset):
    """
    LinkedIn Company Profiles dataset.

    Access 58.5M+ LinkedIn company records with filtering.

    Example:
        >>> companies = client.datasets.linkedin_companies
        >>> metadata = await companies.get_metadata()
        >>> snapshot_id = await companies.filter(
        ...     filter={"name": "company_size", "operator": "=", "value": "1001-5000"},
        ...     records_limit=100
        ... )
        >>> data = await companies.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vikfnt1wgvvqz95w"
    NAME = "linkedin_company_profiles"

    # All available fields with metadata
    # Format: field_name -> {"type": str, "description": str}
    FIELDS: Dict[str, Dict[str, Any]] = {
        "id": {
            "type": "text",
            "description": "Unique identifier for the company profile (URL slug)",
        },
        "name": {
            "type": "text",
            "description": "Company name",
        },
        "country_code": {
            "type": "text",
            "description": "Two-letter country code (e.g., US, GB, FR)",
        },
        "locations": {
            "type": "array",
            "description": "List of company office locations with addresses",
        },
        "followers": {
            "type": "number",
            "description": "Number of LinkedIn followers",
        },
        "employees_in_linkedin": {
            "type": "number",
            "description": "Number of employees with LinkedIn profiles",
        },
        "about": {
            "type": "text",
            "description": "Company description/about section",
        },
        "specialties": {
            "type": "array",
            "description": "List of company specialties/expertise areas",
        },
        "company_size": {
            "type": "text",
            "description": "Employee count range (e.g., '1001-5000 employees')",
        },
        "organization_type": {
            "type": "text",
            "description": "Type of organization (e.g., Public Company, Private)",
        },
        "industries": {
            "type": "text",
            "description": "Primary industry classification",
        },
        "website": {
            "type": "url",
            "description": "Company website URL",
        },
        "crunchbase_url": {
            "type": "url",
            "description": "Link to Crunchbase profile if available",
        },
        "founded": {
            "type": "number",
            "description": "Year the company was founded",
        },
        "company_id": {
            "type": "text",
            "description": "LinkedIn numeric company ID",
        },
        "employees": {
            "type": "array",
            "description": "List of employee profiles with basic info",
        },
        "headquarters": {
            "type": "text",
            "description": "City/region of company headquarters",
        },
        "image": {
            "type": "url",
            "description": "Company cover/banner image URL",
        },
        "logo": {
            "type": "url",
            "description": "Company logo image URL",
        },
        "similar": {
            "type": "array",
            "description": "Similar companies suggested by LinkedIn",
        },
        "url": {
            "type": "url",
            "description": "Full LinkedIn company profile URL",
        },
        "updates": {
            "type": "array",
            "description": "Recent company posts/updates",
        },
        "slogan": {
            "type": "text",
            "description": "Company tagline or slogan",
        },
        "affiliated": {
            "type": "array",
            "description": "Affiliated/subsidiary companies",
        },
        "funding": {
            "type": "object",
            "description": "Funding information if available",
        },
        "investors": {
            "type": "array",
            "description": "List of investors if available",
        },
        "formatted_locations": {
            "type": "array",
            "description": "Formatted address strings for locations",
        },
        "stock_info": {
            "type": "object",
            "description": "Stock ticker and exchange info for public companies",
        },
        "get_directions_url": {
            "type": "array",
            "description": "Map/directions URLs for office locations",
        },
        "description": {
            "type": "text",
            "description": "Brief company description with follower count",
        },
        "additional_information": {
            "type": "object",
            "description": "Extra company details and metadata",
        },
        "country_codes_array": {
            "type": "array",
            "description": "All country codes where company operates",
        },
        "alumni": {
            "type": "array",
            "description": "Notable alumni from the company",
        },
        "alumni_information": {
            "type": "object",
            "description": "Statistics about company alumni",
        },
        "website_simplified": {
            "type": "text",
            "description": "Simplified/masked website domain",
        },
        "unformatted_about": {
            "type": "text",
            "description": "Raw about text without formatting",
        },
    }

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)

    @classmethod
    def get_field_names(cls) -> list:
        """Get list of all field names."""
        return list(cls.FIELDS.keys())

    @classmethod
    def get_text_fields(cls) -> list:
        """Get fields that are text type (commonly used for filtering)."""
        return [name for name, info in cls.FIELDS.items() if info.get("type") == "text"]
