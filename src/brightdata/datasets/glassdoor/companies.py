"""
Glassdoor Companies Overview dataset.

Company information from Glassdoor including ratings, reviews,
salary data, and interview insights.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories for organization
DETAILS_FIELDS = [
    "id",
    "company",
    "country_code",
    "region",
    "company_type",
    "industry",
    "details_size",
    "details_founded",
    "details_type",
    "details_headquarters",
    "details_industry",
    "details_revenue",
    "details_website",
    "stock_symbol",
    "competitors",
    "additional_information",
]

RATINGS_FIELDS = [
    "ratings_overall",
    "ratings_career_opportunities",
    "ratings_ceo_approval",
    "ratings_ceo_approval_count",
    "ratings_compensation_benefits",
    "ratings_culture_values",
    "ratings_senior_management",
    "ratings_work_life_balance",
    "ratings_business_outlook",
    "ratings_recommend_to_friend",
    "ratings_rated_ceo",
    "diversity_inclusion_score",
    "diversity_inclusion_count",
    "career_opportunities_distribution",
]

URL_FIELDS = [
    "url",
    "url_overview",
    "url_jobs",
    "url_reviews",
    "url_faq",
    "benefits_url",
    "salaries_url",
    "interviews_url",
    "photos_url",
]

COUNT_FIELDS = [
    "salaries_count",
    "interviews_count",
    "benefits_count",
    "jobs_count",
    "photos_count",
    "reviews_count",
]

INTERVIEW_FIELDS = [
    "interview_difficulty",
    "interviews_count",
    "interviews_experience",
    "interviews_url",
]


class GlassdoorCompanies(BaseDataset):
    """
    Glassdoor Companies Overview dataset.

    Company information from Glassdoor including employee ratings,
    CEO approval, salary insights, and interview experiences.

    Field Categories:
        - Details: Company info, size, industry, headquarters
        - Ratings: Overall rating, work-life balance, culture, compensation
        - URLs: Links to company pages on Glassdoor
        - Counts: Number of reviews, salaries, interviews, etc.
        - Interviews: Interview difficulty and experience data

    Example:
        >>> glassdoor = client.datasets.glassdoor_companies
        >>> # Discover available fields
        >>> metadata = await glassdoor.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Get fields by category
        >>> ratings = glassdoor.get_ratings_fields()
        >>> details = glassdoor.get_details_fields()
        >>>
        >>> # Filter companies by rating
        >>> snapshot_id = await glassdoor(
        ...     filter={"name": "ratings_overall", "operator": ">=", "value": "4.0"},
        ...     records_limit=100
        ... )
        >>> data = await glassdoor.download(snapshot_id)
    """

    DATASET_ID = "gd_l7j0bx501ockwldaqf"
    NAME = "glassdoor_companies"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_details_fields() -> List[str]:
        """
        Get company details field names.

        Returns:
            List of details field names

        Example:
            >>> details = glassdoor.get_details_fields()
            >>> # ['id', 'company', 'details_size', 'details_industry', ...]
        """
        return DETAILS_FIELDS.copy()

    @staticmethod
    def get_ratings_fields() -> List[str]:
        """
        Get all ratings-related field names.

        Returns:
            List of ratings field names

        Example:
            >>> ratings = glassdoor.get_ratings_fields()
            >>> # ['ratings_overall', 'ratings_work_life_balance', ...]
        """
        return RATINGS_FIELDS.copy()

    @staticmethod
    def get_url_fields() -> List[str]:
        """
        Get all URL field names.

        Returns:
            List of URL field names

        Example:
            >>> urls = glassdoor.get_url_fields()
            >>> # ['url', 'url_overview', 'url_jobs', ...]
        """
        return URL_FIELDS.copy()

    @staticmethod
    def get_count_fields() -> List[str]:
        """
        Get all count-related field names.

        Returns:
            List of count field names

        Example:
            >>> counts = glassdoor.get_count_fields()
            >>> # ['reviews_count', 'salaries_count', ...]
        """
        return COUNT_FIELDS.copy()

    @staticmethod
    def get_interview_fields() -> List[str]:
        """
        Get interview-related field names.

        Returns:
            List of interview field names

        Example:
            >>> interviews = glassdoor.get_interview_fields()
            >>> # ['interview_difficulty', 'interviews_experience', ...]
        """
        return INTERVIEW_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """
        Get all fields grouped by category.

        Returns:
            Dict mapping category name to list of field names

        Example:
            >>> categories = await glassdoor.get_fields_by_category()
            >>> for category, fields in categories.items():
            ...     print(f"{category}: {len(fields)} fields")
        """
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "details": [],
            "ratings": [],
            "urls": [],
            "counts": [],
            "other": [],
        }

        details_set = set(DETAILS_FIELDS)
        ratings_set = set(RATINGS_FIELDS)
        url_set = set(URL_FIELDS)
        count_set = set(COUNT_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in details_set or name.startswith("details_"):
                result["details"].append(name)
            elif name in ratings_set or name.startswith("ratings_"):
                result["ratings"].append(name)
            elif name in url_set or name.endswith("_url"):
                result["urls"].append(name)
            elif name in count_set or name.endswith("_count"):
                result["counts"].append(name)
            else:
                result["other"].append(name)

        # Sort each list
        for category in result:
            result[category] = sorted(result[category])

        self._fields_by_category = result
        return result

    async def search_fields(self, keyword: str) -> List[str]:
        """
        Search for fields containing a keyword.

        Args:
            keyword: Keyword to search for (case-insensitive)

        Returns:
            List of matching field names

        Example:
            >>> salary_fields = await glassdoor.search_fields("salary")
            >>> # ['salaries_url', 'salaries_count']
        """
        metadata = await self.get_metadata()
        keyword_lower = keyword.lower()

        matches = []
        for name, field_info in metadata.fields.items():
            if keyword_lower in name.lower():
                matches.append(name)
            elif field_info.description and keyword_lower in field_info.description.lower():
                matches.append(name)

        return sorted(matches)

    async def get_diversity_fields(self) -> List[str]:
        """
        Get diversity and inclusion related fields.

        Returns:
            List of diversity-related field names
        """
        return await self.search_fields("diversity")

    async def get_ceo_fields(self) -> List[str]:
        """
        Get CEO-related fields.

        Returns:
            List of CEO-related field names
        """
        return await self.search_fields("ceo")

    @staticmethod
    def get_identifier_fields() -> List[str]:
        """
        Get fields that can be used as unique identifiers.

        Returns:
            List of identifier field names
        """
        return [
            "id",
            "url",
            "url_overview",
            "details_website",
        ]
