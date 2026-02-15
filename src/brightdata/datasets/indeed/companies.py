"""
Indeed Companies Info dataset.

Company profiles from Indeed with job listings, reviews,
salaries, and company details.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
COMPANY_FIELDS = [
    "name",
    "description",
    "url",
    "website",
    "industry",
    "company_size",
    "revenue",
    "logo",
    "headquarters",
    "country_code",
    "details",
    "related_companies",
    "company_id",
    "overall_rating",
]

WORK_CULTURE_FIELDS = [
    "work_happiness",
    "benefits",
]

REVIEWS_FIELDS = [
    "reviews",
    "reviews_count",
    "reviews_url",
]

SALARIES_FIELDS = [
    "salaries",
    "salaries_count",
    "salaries_url",
]

JOBS_FIELDS = [
    "jobs_categories",
    "jobs_count",
    "jobs_url",
]

OTHER_CONTENT_FIELDS = [
    "q&a_count",
    "q&a_url",
    "interviews_count",
    "interviews_url",
    "photos_count",
    "photos_url",
]


class IndeedCompanies(BaseDataset):
    """
    Indeed Companies Info dataset.

    Company profiles with job listings, employee reviews,
    salary data, and company culture information.

    Field Categories:
        - Company: Name, description, industry, size, revenue, location
        - Work Culture: Work happiness scores, benefits
        - Reviews: Review counts and links
        - Salaries: Salary information and links
        - Jobs: Job categories and listings
        - Other Content: Q&A, interviews, photos

    Example:
        >>> indeed = client.datasets.indeed_companies
        >>> # Discover available fields
        >>> metadata = await indeed.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by industry
        >>> snapshot_id = await indeed(
        ...     filter={"name": "industry", "operator": "=", "value": "Technology"},
        ...     records_limit=100
        ... )
        >>> data = await indeed.download(snapshot_id)
    """

    DATASET_ID = "gd_l7qekxkv2i7ve6hx1s"
    NAME = "indeed_companies"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company-related field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_work_culture_fields() -> List[str]:
        """Get work culture field names."""
        return WORK_CULTURE_FIELDS.copy()

    @staticmethod
    def get_reviews_fields() -> List[str]:
        """Get reviews-related field names."""
        return REVIEWS_FIELDS.copy()

    @staticmethod
    def get_salaries_fields() -> List[str]:
        """Get salaries-related field names."""
        return SALARIES_FIELDS.copy()

    @staticmethod
    def get_jobs_fields() -> List[str]:
        """Get jobs-related field names."""
        return JOBS_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "work_culture": [],
            "reviews": [],
            "salaries": [],
            "jobs": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        work_set = set(WORK_CULTURE_FIELDS)
        reviews_set = set(REVIEWS_FIELDS)
        salaries_set = set(SALARIES_FIELDS)
        jobs_set = set(JOBS_FIELDS)
        other_content_set = set(OTHER_CONTENT_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set or name.startswith("company"):
                result["company"].append(name)
            elif name in work_set or "happiness" in name or "benefit" in name:
                result["work_culture"].append(name)
            elif name in reviews_set or "review" in name.lower():
                result["reviews"].append(name)
            elif name in salaries_set or "salar" in name.lower():
                result["salaries"].append(name)
            elif name in jobs_set or "job" in name.lower():
                result["jobs"].append(name)
            elif name in other_content_set:
                result["other"].append(name)
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
            "website",
        ]
