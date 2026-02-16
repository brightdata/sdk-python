"""
US Lawyers Directory dataset.

Lawyer profiles from Martindale-Hubbell with practice areas,
education, reviews, and contact information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
PROFILE_FIELDS = [
    "url",
    "name",
    "isln",
    "photo",
    "address",
    "mailing_address",
    "location",
    "type",
    "filial",
    "company",
]

EDUCATION_FIELDS = [
    "admission",
    "law_school_attended",
    "university_attended",
    "year_of_first_admission",
    "year_established",
]

PRACTICE_FIELDS = [
    "areas_of_practice",
    "practice_count",
    "office_hours",
    "office_size",
    "languages",
]

CONTACT_FIELDS = [
    "fax",
    "phone",
    "phone_cell",
    "phone_telecopier",
    "website",
    "video_call",
]

REVIEW_FIELDS = [
    "profile_peer_review_count",
    "profile_peer_review_star",
    "profile_peer_review_awards",
    "profile_peer_review_detail",
    "profile_visibility",
    "profile_client_recomendation_count",
    "profile_client_recomendation_rating",
    "profile_client_review_count",
    "profile_client_review_detail",
    "profile_client_review_list",
    "profile_client_review_rating",
    "awards",
]

CONTENT_FIELDS = [
    "biography",
    "about",
    "birth_information",
    "memberships",
    "hobbies_interests",
    "people",
    "clients",
    "clients2",
    "transactions",
    "payment_information",
    "state_bar_summary",
    "minority_owned",
]


class USLawyers(BaseDataset):
    """
    US Lawyers Directory dataset.

    Lawyer profiles with practice areas, education background,
    peer reviews, client reviews, and contact information.

    Field Categories:
        - Profile: Name, photo, address, company, type
        - Education: Law school, university, admission dates
        - Practice: Areas of practice, languages, office details
        - Contact: Phone, fax, website, video call
        - Review: Peer reviews, client reviews, ratings, awards
        - Content: Biography, memberships, clients

    Example:
        >>> lawyers = client.datasets.us_lawyers
        >>> # Discover available fields
        >>> metadata = await lawyers.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by location
        >>> snapshot_id = await lawyers(
        ...     filter={"name": "location", "operator": "=", "value": "CA"},
        ...     records_limit=100
        ... )
        >>> data = await lawyers.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vil5n11okchcbvax"
    NAME = "us_lawyers"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_profile_fields() -> List[str]:
        """Get profile-related field names."""
        return PROFILE_FIELDS.copy()

    @staticmethod
    def get_education_fields() -> List[str]:
        """Get education-related field names."""
        return EDUCATION_FIELDS.copy()

    @staticmethod
    def get_practice_fields() -> List[str]:
        """Get practice-related field names."""
        return PRACTICE_FIELDS.copy()

    @staticmethod
    def get_contact_fields() -> List[str]:
        """Get contact-related field names."""
        return CONTACT_FIELDS.copy()

    @staticmethod
    def get_review_fields() -> List[str]:
        """Get review-related field names."""
        return REVIEW_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "profile": [],
            "education": [],
            "practice": [],
            "contact": [],
            "review": [],
            "content": [],
            "other": [],
        }

        profile_set = set(PROFILE_FIELDS)
        education_set = set(EDUCATION_FIELDS)
        practice_set = set(PRACTICE_FIELDS)
        contact_set = set(CONTACT_FIELDS)
        review_set = set(REVIEW_FIELDS)
        content_set = set(CONTENT_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in profile_set:
                result["profile"].append(name)
            elif name in education_set or "school" in name.lower() or "admission" in name.lower():
                result["education"].append(name)
            elif name in practice_set or "practice" in name.lower():
                result["practice"].append(name)
            elif name in contact_set or "phone" in name.lower():
                result["contact"].append(name)
            elif name in review_set or "review" in name.lower() or "rating" in name.lower():
                result["review"].append(name)
            elif name in content_set:
                result["content"].append(name)
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
            "isln",
            "url",
        ]
