"""
Xing Social Network Profiles dataset.

Professional profiles from Xing with experience, education,
skills, and contact information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
PROFILE_FIELDS = [
    "account_id",
    "familyName",
    "givenName",
    "name",
    "gender",
    "membership",
    "country_code",
    "honorificPrefix",
    "jobTitle",
    "image",
    "url",
    "addressLocality",
]

EXPERIENCE_FIELDS = [
    "experience",
    "education",
    "languages",
    "skills",
]

SOCIAL_FIELDS = [
    "groups",
    "interests",
    "similar_profiles",
    "wants",
]


class XingProfiles(BaseDataset):
    """
    Xing Social Network Profiles dataset.

    Professional profiles with career history, education,
    skills, and networking information.

    Field Categories:
        - Profile: Name, gender, membership, location, job title
        - Experience: Work history, education, languages, skills
        - Social: Groups, interests, similar profiles, wants

    Example:
        >>> xing = client.datasets.xing_profiles
        >>> # Discover available fields
        >>> metadata = await xing.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by country
        >>> snapshot_id = await xing(
        ...     filter={"name": "country_code", "operator": "=", "value": "DE"},
        ...     records_limit=100
        ... )
        >>> data = await xing.download(snapshot_id)
    """

    DATASET_ID = "gd_l3lh4ev31oqrvvblv6"
    NAME = "xing_profiles"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_profile_fields() -> List[str]:
        """Get profile-related field names."""
        return PROFILE_FIELDS.copy()

    @staticmethod
    def get_experience_fields() -> List[str]:
        """Get experience and education field names."""
        return EXPERIENCE_FIELDS.copy()

    @staticmethod
    def get_social_fields() -> List[str]:
        """Get social networking field names."""
        return SOCIAL_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "profile": [],
            "experience": [],
            "social": [],
            "other": [],
        }

        profile_set = set(PROFILE_FIELDS)
        experience_set = set(EXPERIENCE_FIELDS)
        social_set = set(SOCIAL_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in profile_set:
                result["profile"].append(name)
            elif name in experience_set or "experience" in name or "education" in name:
                result["experience"].append(name)
            elif name in social_set or "group" in name or "interest" in name:
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
            "account_id",
            "url",
        ]
