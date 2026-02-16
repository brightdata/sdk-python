"""
Glassdoor Companies Reviews dataset.

Employee reviews with detailed ratings, pros/cons, and employee information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
COMPANY_FIELDS = [
    "overview_id",
    "company_name",
    "glassdoor_employer_id",
]

REVIEW_FIELDS = [
    "review_id",
    "review_url",
    "rating_date",
    "summary",
    "review_pros",
    "review_cons",
    "review_advice",
    "advice_to_management",
]

EMPLOYEE_FIELDS = [
    "employee_job_end_year",
    "employee_length",
    "employee_responses",
    "employee_status",
    "employee_type",
    "employee_location",
    "employee_job_title",
]

RATING_FIELDS = [
    "rating_overall",
    "rating_culture_values",
    "rating_diversity_inclusion",
    "rating_work_life",
    "rating_compensation_benefits",
    "rating_senior_leadership",
    "rating_career_opportunities",
]

FLAG_FIELDS = [
    "flag_covid",
    "flag_featured",
    "flags_business_outlook",
    "flags_ceo_approval",
    "flags_recommend_frend",
]

COUNT_FIELDS = [
    "count_helpful",
    "count_unhelpful",
]


class GlassdoorReviews(BaseDataset):
    """
    Glassdoor Companies Reviews dataset.

    Employee reviews with detailed ratings across multiple dimensions,
    pros/cons, advice to management, and employee metadata.

    Field Categories:
        - Company: Employer ID and name
        - Review: Review text, pros, cons, advice
        - Employee: Job title, status, tenure, location
        - Ratings: Overall, culture, work-life, compensation, etc.
        - Flags: COVID, featured, outlook, CEO approval

    Example:
        >>> reviews = client.datasets.glassdoor_reviews
        >>> # Discover available fields
        >>> metadata = await reviews.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Get rating fields
        >>> ratings = reviews.get_rating_fields()
        >>>
        >>> # Filter by rating
        >>> snapshot_id = await reviews(
        ...     filter={"name": "rating_overall", "operator": ">=", "value": "4"},
        ...     records_limit=100
        ... )
        >>> data = await reviews.download(snapshot_id)
    """

    DATASET_ID = "gd_l7j1po0921hbu0ri1z"
    NAME = "glassdoor_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company-related field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_review_fields() -> List[str]:
        """Get review content field names."""
        return REVIEW_FIELDS.copy()

    @staticmethod
    def get_employee_fields() -> List[str]:
        """Get employee-related field names."""
        return EMPLOYEE_FIELDS.copy()

    @staticmethod
    def get_rating_fields() -> List[str]:
        """Get all rating field names."""
        return RATING_FIELDS.copy()

    @staticmethod
    def get_flag_fields() -> List[str]:
        """Get flag field names."""
        return FLAG_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "review": [],
            "employee": [],
            "rating": [],
            "flag": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        review_set = set(REVIEW_FIELDS)
        employee_set = set(EMPLOYEE_FIELDS)
        rating_set = set(RATING_FIELDS)
        flag_set = set(FLAG_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set:
                result["company"].append(name)
            elif name in review_set or name.startswith("review"):
                result["review"].append(name)
            elif name in employee_set or name.startswith("employee"):
                result["employee"].append(name)
            elif name in rating_set or name.startswith("rating"):
                result["rating"].append(name)
            elif name in flag_set or name.startswith("flag"):
                result["flag"].append(name)
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
            "review_id",
            "overview_id",
            "glassdoor_employer_id",
            "review_url",
        ]
