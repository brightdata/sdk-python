"""
Trustpilot Business Reviews dataset.

Business reviews from Trustpilot with company info, ratings,
and reviewer details.

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
    "company_logo",
    "company_website",
    "company_rating_name",
    "company_overall_rating",
    "is_verified_company",
    "company_total_reviews",
    "company_about",
    "company_email",
    "company_phone",
    "company_location",
    "company_country",
    "company_category",
    "company_other_categories",
    "company activity",
    "breadcrumbs",
]

RATING_DISTRIBUTION_FIELDS = [
    "5_star",
    "4_star",
    "3_star",
    "2_star",
    "1_star",
]

REVIEW_FIELDS = [
    "review_id",
    "review_date",
    "review_rating",
    "review_title",
    "review_content",
    "is_verified_review",
    "review_date_of_experience",
    "review_replies",
    "review_useful_count",
    "review_url",
    "date_posted",
    "url",
]

REVIEWER_FIELDS = [
    "reviewer_name",
    "reviewer_location",
    "reviews_posted_overall",
]


class TrustpilotReviews(BaseDataset):
    """
    Trustpilot Business Reviews dataset.

    Business reviews with company profiles, rating distributions,
    and detailed review content from Trustpilot.

    Field Categories:
        - Company: Name, website, rating, verification status
        - Rating Distribution: Star rating breakdown (1-5 stars)
        - Review: Content, date, rating, replies
        - Reviewer: Name, location, review count

    Example:
        >>> trustpilot = client.datasets.trustpilot_reviews
        >>> # Discover available fields
        >>> metadata = await trustpilot.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by rating
        >>> snapshot_id = await trustpilot(
        ...     filter={"name": "review_rating", "operator": ">=", "value": "4"},
        ...     records_limit=100
        ... )
        >>> data = await trustpilot.download(snapshot_id)
    """

    DATASET_ID = "gd_lm5zmhwd2sni130p"
    NAME = "trustpilot_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_company_fields() -> List[str]:
        """Get company-related field names."""
        return COMPANY_FIELDS.copy()

    @staticmethod
    def get_rating_distribution_fields() -> List[str]:
        """Get rating distribution field names."""
        return RATING_DISTRIBUTION_FIELDS.copy()

    @staticmethod
    def get_review_fields() -> List[str]:
        """Get review content field names."""
        return REVIEW_FIELDS.copy()

    @staticmethod
    def get_reviewer_fields() -> List[str]:
        """Get reviewer-related field names."""
        return REVIEWER_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "company": [],
            "rating_distribution": [],
            "review": [],
            "reviewer": [],
            "other": [],
        }

        company_set = set(COMPANY_FIELDS)
        rating_set = set(RATING_DISTRIBUTION_FIELDS)
        review_set = set(REVIEW_FIELDS)
        reviewer_set = set(REVIEWER_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in company_set or name.startswith("company_"):
                result["company"].append(name)
            elif name in rating_set or name.endswith("_star"):
                result["rating_distribution"].append(name)
            elif name in review_set or name.startswith("review"):
                result["review"].append(name)
            elif name in reviewer_set or name.startswith("reviewer"):
                result["reviewer"].append(name)
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
            "company_id",
            "review_url",
            "url",
        ]
