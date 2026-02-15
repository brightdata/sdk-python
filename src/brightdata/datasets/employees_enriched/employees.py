"""
Employees Business Enriched dataset.

LinkedIn employee profiles enriched with company information.
Contains profile data (education, experience, certifications) alongside
associated company details (revenue, funding, size).

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Field categories for organization
PROFILE_FIELDS = [
    "url",
    "profile_url",
    "linkedin_num_id",
    "avatar",
    "profile_name",
    "certifications",
    "profile_location",
    "profile_connections",
    "profile_country_code",
    "profile_education_full",
    "profile_last_education",
    "profile_experience_full",
    "profile_last_experience",
    "profile_followers",
    "profile_linkedin_id",
    "profile_current_position",
    "profile_current_title",
    "profile_activity",
    "profile_posts",
    "profile_about",
    "profile_courses",
    "profile_volunteer_experience",
    "profile_languages",
    "profile_publications",
    "profile_recommendations",
    "profile_recommendations_count",
    "profile_organizations",
    "profile_projects",
    "profile_bio_links",
]

COMPANY_FIELDS = [
    "company_name",
    "company_id",
    "company_linkedin_url",
    "company_size",
    "company_country_code",
    "company_description",
    "company_other_employees",
    "employees_in_linkedin",
    "company_linkedin_followers",
    "company_locations",
    "company_founded_year",
    "company_headquarters",
    "company_categories",
    "company_logo",
    "company_slogan",
    "company_specialties",
    "company_updates",
    "company_website",
    "company_type",
    "company_clean_domain",
    "company_revenue_usd",
    "company_total_funding",
    "company_total_employees",
    "company_stock_symbol",
    "company_is_non_profit",
    "company_parent_company",
]


class EmployeesEnriched(BaseDataset):
    """
    Employees Business Enriched dataset.

    LinkedIn employee profiles enriched with their associated company
    information. Each record contains detailed profile data alongside
    company metrics.

    Field Categories:
        - Profile: Personal info, education, experience, certifications
        - Company: Associated company details, revenue, funding, size

    Example:
        >>> employees = client.datasets.employees_enriched
        >>> # Discover available fields
        >>> metadata = await employees.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Get fields by category
        >>> profile_fields = employees.get_profile_fields()
        >>> company_fields = employees.get_company_fields()
        >>>
        >>> # Filter employees
        >>> snapshot_id = await employees(
        ...     filter={"name": "profile_country_code", "operator": "=", "value": "US"},
        ...     records_limit=100
        ... )
        >>> data = await employees.download(snapshot_id)
    """

    # TODO: Replace with actual dataset ID
    DATASET_ID = "gd_lxxxxxxxxxxxxxx"  # Get from Bright Data console
    NAME = "employees_enriched"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None

    @staticmethod
    def get_profile_fields() -> List[str]:
        """
        Get all profile-related field names.

        Returns:
            List of profile field names

        Example:
            >>> profile_fields = employees.get_profile_fields()
            >>> # ['url', 'profile_url', 'profile_name', ...]
        """
        return PROFILE_FIELDS.copy()

    @staticmethod
    def get_company_fields() -> List[str]:
        """
        Get all company-related field names.

        Returns:
            List of company field names

        Example:
            >>> company_fields = employees.get_company_fields()
            >>> # ['company_name', 'company_id', 'company_revenue_usd', ...]
        """
        return COMPANY_FIELDS.copy()

    async def get_fields_by_category(self) -> Dict[str, List[str]]:
        """
        Get all fields grouped by category.

        Returns:
            Dict mapping category name to list of field names

        Example:
            >>> categories = await employees.get_fields_by_category()
            >>> for category, fields in categories.items():
            ...     print(f"{category}: {len(fields)} fields")
        """
        if self._fields_by_category is not None:
            return self._fields_by_category

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {
            "profile": [],
            "company": [],
            "other": [],
        }

        profile_set = set(PROFILE_FIELDS)
        company_set = set(COMPANY_FIELDS)

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            if name in profile_set or name.startswith("profile_"):
                result["profile"].append(name)
            elif name in company_set or name.startswith("company_"):
                result["company"].append(name)
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
            >>> education_fields = await employees.search_fields("education")
            >>> # ['profile_education_full', 'profile_last_education']
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

    async def get_experience_fields(self) -> List[str]:
        """
        Get fields related to work experience.

        Returns:
            List of experience-related field names
        """
        return await self.search_fields("experience")

    async def get_education_fields(self) -> List[str]:
        """
        Get fields related to education.

        Returns:
            List of education-related field names
        """
        return await self.search_fields("education")

    @staticmethod
    def get_identifier_fields() -> List[str]:
        """
        Get fields that can be used as unique identifiers.

        Returns:
            List of identifier field names
        """
        return [
            "url",
            "profile_url",
            "linkedin_num_id",
            "profile_linkedin_id",
            "company_id",
            "company_linkedin_url",
        ]
