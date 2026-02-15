"""
LinkedIn Profiles Jobs Listings dataset.

LinkedIn profiles with associated job recommendations and listings.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
PROFILE_FIELDS = [
    "url",
    "linkedin_id",
    "name",
    "about",
    "position",
    "country_code",
]

CAREER_FIELDS = [
    "experience",
    "education",
    "current_company",
]

JOB_FIELDS = [
    "optional_jobs",
]


class LinkedInJobListings(BaseDataset):
    """
    LinkedIn Profiles Jobs Listings dataset.

    LinkedIn profiles enriched with job recommendations and listings
    that match the profile's skills and experience.

    Field Categories:
        - Profile: Basic profile info (name, position, country)
        - Career: Experience, education, current company
        - Jobs: Recommended job listings

    Example:
        >>> jobs = client.datasets.linkedin_job_listings
        >>> # Discover available fields
        >>> metadata = await jobs.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by country
        >>> snapshot_id = await jobs(
        ...     filter={"name": "country_code", "operator": "=", "value": "US"},
        ...     records_limit=100
        ... )
        >>> data = await jobs.download(snapshot_id)
    """

    DATASET_ID = "gd_lpfll7v5hcqtkxl6l"
    NAME = "linkedin_job_listings"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_profile_fields() -> List[str]:
        """Get profile-related field names."""
        return PROFILE_FIELDS.copy()

    @staticmethod
    def get_career_fields() -> List[str]:
        """Get career-related field names."""
        return CAREER_FIELDS.copy()

    @staticmethod
    def get_job_fields() -> List[str]:
        """Get job listing field names."""
        return JOB_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "profile": [],
            "career": [],
            "jobs": [],
            "other": [],
        }

        profile_set = set(PROFILE_FIELDS)
        career_set = set(CAREER_FIELDS)
        job_set = set(JOB_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in profile_set:
                result["profile"].append(name)
            elif name in career_set:
                result["career"].append(name)
            elif name in job_set or "job" in name.lower():
                result["jobs"].append(name)
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
            "url",
            "linkedin_id",
        ]
