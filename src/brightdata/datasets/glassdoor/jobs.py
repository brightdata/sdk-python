"""
Glassdoor Job Listings dataset.

Job postings from Glassdoor with company info, ratings, and pay data.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
JOB_FIELDS = [
    "url",
    "job_title",
    "job_location",
    "job_overview",
    "job_posting_id",
    "job_application_link",
]

COMPANY_FIELDS = [
    "company_url_overview",
    "company_name",
    "company_rating",
    "company_id",
    "company_headquarters",
    "company_founded_year",
    "company_industry",
    "company_revenue",
    "company_size",
    "company_type",
    "company_sector",
    "company_website",
    "company_ceo",
]

RATING_FIELDS = [
    "company_career_opportunities_rating",
    "company_comp_and_benefits_rating",
    "company_culture_and_values_rating",
    "company_senior_management_rating",
    "company_work/life_balance_rating",
    "company_benefits_rating",
    "percentage_that_recommend_company_to_a friend",
    "percentage_that_approve_of_ceo",
]

PAY_FIELDS = [
    "pay_range_glassdoor_est",
    "pay_median_glassdoor",
    "pay_range_employer_est",
    "pay_median_employer",
    "pay_range_currency",
    "pay_type",
]


class GlassdoorJobs(BaseDataset):
    """
    Glassdoor Job Listings dataset.

    Job postings with detailed company information, ratings,
    salary estimates, and employee reviews.

    Field Categories:
        - Job: Title, location, overview, application link
        - Company: Name, industry, size, headquarters
        - Ratings: Career opportunities, culture, management, etc.
        - Pay: Salary ranges from Glassdoor and employer estimates

    Example:
        >>> jobs = client.datasets.glassdoor_jobs
        >>> # Discover available fields
        >>> metadata = await jobs.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by job title
        >>> snapshot_id = await jobs(
        ...     filter={"name": "job_title", "operator": "contains", "value": "Engineer"},
        ...     records_limit=100
        ... )
        >>> data = await jobs.download(snapshot_id)
    """

    DATASET_ID = "gd_lpfbbndm1xnopbrcr0"
    NAME = "glassdoor_jobs"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_job_fields() -> List[str]:
        """Get job-related field names."""
        return JOB_FIELDS.copy()

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company-related field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_rating_fields() -> List[str]:
        """Get rating field names."""
        return RATING_FIELDS.copy()

    @staticmethod
    def get_pay_fields() -> List[str]:
        """Get pay-related field names."""
        return PAY_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "job": [],
            "company": [],
            "rating": [],
            "pay": [],
            "other": [],
        }

        job_set = set(JOB_FIELDS)
        company_set = set(COMPANY_FIELDS)
        rating_set = set(RATING_FIELDS)
        pay_set = set(PAY_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in job_set or name.startswith("job_"):
                result["job"].append(name)
            elif name in company_set or name.startswith("company_"):
                result["company"].append(name)
            elif name in rating_set or "rating" in name:
                result["rating"].append(name)
            elif name in pay_set or name.startswith("pay_"):
                result["pay"].append(name)
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
            "job_posting_id",
            "url",
            "company_id",
        ]
