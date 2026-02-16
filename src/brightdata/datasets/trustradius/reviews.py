"""
TrustRadius Product Reviews dataset.

Software product reviews from TrustRadius with detailed
ratings, pros/cons, and reviewer information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories
PRODUCT_FIELDS = [
    "url",
    "product_id",
    "product_name",
]

REVIEW_FIELDS = [
    "review_id",
    "review_url",
    "review_title",
    "review_rating",
    "review_date",
    "usability_rating",
    "implementation_rating",
    "support_rating",
    "likelihood_to_recommend",
    "likelihood_to_renew",
    "start_date",
    "updated_date",
    "author_incentivized",
]

AUTHOR_FIELDS = [
    "review_author",
    "author_position",
    "author_company_name",
    "author_company_industry",
    "author_company_size",
    "author_labels",
    "author_experience_years",
    "author_linkedin_url",
    "author_image",
]

CONTENT_FIELDS = [
    "pros",
    "cons",
    "pros_cons",
    "usecases_deployment_scope",
    "return_on_investment",
    "efficiencies_gained",
    "key_insights",
    "usability_pros",
    "usability_cons",
    "easy_tasks",
    "difficult_tasks",
    "support_pros",
    "support_cons",
    "implementation_issues",
    "implementation_partner",
]

PRODUCT_DETAILS_FIELDS = [
    "alternatives_considered",
    "other_software_used",
    "users_and_roles",
    "support_headcount_required",
    "business_processes_supported",
    "innovative_uses",
    "future_planned_uses",
    "products_replaced",
    "key_differentiators",
    "feature_ratings",
]


class TrustRadiusReviews(BaseDataset):
    """
    TrustRadius Product Reviews dataset.

    Software product reviews with detailed ratings,
    pros/cons analysis, and reviewer company information.

    Field Categories:
        - Product: ID, name, URL
        - Review: Ratings, dates, recommendation scores
        - Author: Reviewer info, company, experience
        - Content: Pros, cons, insights, ROI
        - Product Details: Alternatives, features, use cases

    Example:
        >>> reviews = client.datasets.trustradius_reviews
        >>> # Discover available fields
        >>> metadata = await reviews.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Filter by rating
        >>> snapshot_id = await reviews(
        ...     filter={"name": "review_rating", "operator": ">=", "value": "8"},
        ...     records_limit=100
        ... )
        >>> data = await reviews.download(snapshot_id)
    """

    DATASET_ID = "gd_lztojazw1389985ops"
    NAME = "trustradius_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_product_fields() -> List[str]:
        """Get product-related field names."""
        return PRODUCT_FIELDS.copy()

    @staticmethod
    def get_review_fields() -> List[str]:
        """Get review-related field names."""
        return REVIEW_FIELDS.copy()

    @staticmethod
    def get_author_fields() -> List[str]:
        """Get author-related field names."""
        return AUTHOR_FIELDS.copy()

    @staticmethod
    def get_content_fields() -> List[str]:
        """Get content-related field names."""
        return CONTENT_FIELDS.copy()

    @staticmethod
    def get_product_details_fields() -> List[str]:
        """Get product details field names."""
        return PRODUCT_DETAILS_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """Get all fields grouped by category."""
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "product": [],
            "review": [],
            "author": [],
            "content": [],
            "product_details": [],
            "other": [],
        }

        product_set = set(PRODUCT_FIELDS)
        review_set = set(REVIEW_FIELDS)
        author_set = set(AUTHOR_FIELDS)
        content_set = set(CONTENT_FIELDS)
        details_set = set(PRODUCT_DETAILS_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in product_set or name.startswith("product"):
                result["product"].append(name)
            elif name in review_set or (name.startswith("review") and name not in author_set):
                result["review"].append(name)
            elif name in author_set or name.startswith("author"):
                result["author"].append(name)
            elif name in content_set or name in ["pros", "cons"]:
                result["content"].append(name)
            elif name in details_set:
                result["product_details"].append(name)
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
            "product_id",
            "review_url",
            "url",
        ]
