"""
LinkedIn People Profiles dataset.

Dataset ID: gd_l1viktl72bvl7bjuj0
Records: 620M+ profiles

See FIELDS dict for all filterable fields with descriptions and fill rates.
"""

from typing import TYPE_CHECKING, Dict, Any

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class LinkedInPeopleProfiles(BaseDataset):
    """
    LinkedIn People Profiles dataset.

    Access 620M+ LinkedIn profile records with filtering.

    Example:
        >>> profiles = client.datasets.linkedin_profiles
        >>> metadata = await profiles.get_metadata()
        >>> snapshot_id = await profiles.filter(
        ...     filter={"name": "industry", "operator": "=", "value": "Technology"},
        ...     records_limit=100
        ... )
        >>> data = await profiles.download(snapshot_id)
    """

    DATASET_ID = "gd_l1viktl72bvl7bjuj0"
    NAME = "linkedin_people_profiles"

    # All available fields with metadata
    # Format: field_name -> {"type": str, "description": str, "fill_rate": float}
    FIELDS: Dict[str, Dict[str, Any]] = {
        "id": {
            "type": "text",
            "description": "A unique identifier for the person's LinkedIn profile",
            "fill_rate": 100.00,
        },
        "name": {
            "type": "text",
            "description": "Profile name",
            "fill_rate": 97.54,
        },
        "first_name": {
            "type": "text",
            "description": "First name of the user",
            "fill_rate": 95.10,
        },
        "last_name": {
            "type": "text",
            "description": "Last name of the user",
            "fill_rate": 94.80,
        },
        "city": {
            "type": "text",
            "description": "Geographical location of the user",
            "fill_rate": 96.30,
        },
        "country_code": {
            "type": "text",
            "description": "Geographical location of the user",
            "fill_rate": 97.11,
        },
        "location": {
            "type": "text",
            "description": "Geographical location of the user",
            "fill_rate": 61.93,
        },
        "position": {
            "type": "text",
            "description": "The current job title or position of the profile",
            "fill_rate": 91.23,
        },
        "about": {
            "type": "text",
            "description": "A concise profile summary. May be truncated with '...'",
            "fill_rate": 18.90,
        },
        "url": {
            "type": "url",
            "description": "URL that links directly to the LinkedIn profile",
            "fill_rate": 100.00,
        },
        "input_url": {
            "type": "url",
            "description": "The URL that was entered when starting the scraping process",
            "fill_rate": 100.00,
        },
        "linkedin_id": {
            "type": "text",
            "description": "LinkedIn profile identifier",
            "fill_rate": 100.00,
        },
        "linkedin_num_id": {
            "type": "text",
            "description": "Numeric LinkedIn profile ID",
            "fill_rate": 100.00,
        },
        "avatar": {
            "type": "url",
            "description": "URL that links to the profile picture of the LinkedIn user",
            "fill_rate": 96.28,
        },
        "banner_image": {
            "type": "url",
            "description": "Banner image URL",
            "fill_rate": 96.28,
        },
        "default_avatar": {
            "type": "boolean",
            "description": "Is the avatar picture the default empty picture",
            "fill_rate": 95.73,
        },
        "followers": {
            "type": "number",
            "description": "How many users/companies following the profile",
            "fill_rate": 71.39,
        },
        "connections": {
            "type": "number",
            "description": "How many connections the profile has",
            "fill_rate": 70.33,
        },
        "recommendations_count": {
            "type": "number",
            "description": "Total number of recommendations received",
            "fill_rate": 3.65,
        },
        "influencer": {
            "type": "boolean",
            "description": "Indicator if the profile is marked as influencer",
            "fill_rate": 46.06,
        },
        "memorialized_account": {
            "type": "boolean",
            "description": "Boolean indicating if the account is memorialized",
            "fill_rate": 99.44,
        },
        # Current company fields
        "current_company_name": {
            "type": "text",
            "description": "The name of the latest/current company of the profile",
            "fill_rate": 69.60,
        },
        "current_company_company_id": {
            "type": "text",
            "description": "The id of the latest/current company of the profile",
            "fill_rate": 38.94,
        },
        "current_company": {
            "type": "object",
            "description": "Current professional position info: company name, job title, company ID, industry",
            "fill_rate": 100.00,
            "nested_fields": 6,
        },
        # Experience & Education
        "experience": {
            "type": "array",
            "description": "Professional history: job titles, dates, companies, locations",
            "fill_rate": 71.49,
            "nested_fields": 16,
        },
        "education": {
            "type": "array",
            "description": "Educational background: degree, field, start/end year",
            "fill_rate": 41.97,
            "nested_fields": 10,
        },
        "educations_details": {
            "type": "text",
            "description": "Educational background as text",
            "fill_rate": 42.08,
        },
        # Activity & Posts
        "posts": {
            "type": "array",
            "description": "User's last LinkedIn posts: title, date, URL",
            "fill_rate": 1.27,
            "nested_fields": 7,
        },
        "activity": {
            "type": "array",
            "description": "Any activity the user has regarding posts",
            "fill_rate": 32.95,
            "nested_fields": 5,
        },
        # Professional credentials
        "certifications": {
            "type": "array",
            "description": "Licenses & Certifications",
            "fill_rate": 8.35,
            "nested_fields": 5,
        },
        "courses": {
            "type": "array",
            "description": "Courses or educational programs undertaken",
            "fill_rate": 2.55,
            "nested_fields": 3,
        },
        "languages": {
            "type": "array",
            "description": "User's language proficiencies",
            "fill_rate": 9.19,
            "nested_fields": 2,
        },
        "publications": {
            "type": "array",
            "description": "Published works or presentations",
            "fill_rate": 1.23,
            "nested_fields": 4,
        },
        "patents": {
            "type": "array",
            "description": "Patents filed or granted",
            "fill_rate": 0.13,
            "nested_fields": 4,
        },
        "projects": {
            "type": "array",
            "description": "Professional or academic projects",
            "fill_rate": 2.08,
            "nested_fields": 4,
        },
        "honors_and_awards": {
            "type": "array",
            "description": "Awards and recognitions received",
            "fill_rate": 2.13,
            "nested_fields": 4,
        },
        # Social & Network
        "recommendations": {
            "type": "array",
            "description": "Recommendations received from connections/colleagues",
            "fill_rate": 3.61,
        },
        "volunteer_experience": {
            "type": "array",
            "description": "Information related to volunteer work",
            "fill_rate": 4.12,
            "nested_fields": 8,
        },
        "organizations": {
            "type": "array",
            "description": "Memberships in professional organizations",
            "fill_rate": 1.78,
            "nested_fields": 6,
        },
        "people_also_viewed": {
            "type": "array",
            "description": "Profiles that viewers of this profile also viewed",
            "fill_rate": 33.36,
            "nested_fields": 4,
        },
        "similar_profiles": {
            "type": "array",
            "description": "Profiles similar to the current one",
            "fill_rate": 0.58,
            "nested_fields": 4,
        },
        "bio_links": {
            "type": "array",
            "description": "External links added to the bio",
            "fill_rate": 2.96,
            "nested_fields": 2,
        },
    }

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)

    @classmethod
    def get_field_names(cls) -> list:
        """Get list of all field names."""
        return list(cls.FIELDS.keys())

    @classmethod
    def get_high_fill_rate_fields(cls, min_rate: float = 50.0) -> list:
        """Get fields with fill rate above threshold."""
        return [name for name, info in cls.FIELDS.items() if info.get("fill_rate", 0) >= min_rate]
