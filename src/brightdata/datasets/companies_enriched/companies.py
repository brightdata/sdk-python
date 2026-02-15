"""
Companies Enriched dataset.

Multi-source company information combining data from:
- LinkedIn (_lc)
- Slintel/6sense (_sl)
- Owler (_ow)
- Crunchbase (_cb)
- Indeed (_in)
- ZoomInfo (_zi)
- Glassdoor (_gd)

Use get_metadata() to discover all 336+ available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


# Data source suffixes
SOURCES = {
    "_lc": "linkedin",
    "_sl": "slintel",
    "_ow": "owler",
    "_cb": "crunchbase",
    "_in": "indeed",
    "_zi": "zoominfo",
    "_gd": "glassdoor",
}


class CompaniesEnriched(BaseDataset):
    """
    Companies Enriched dataset.

    Aggregates company information from 7+ data sources into a single dataset.
    Each field is suffixed with its source (e.g., `name_lc` for LinkedIn,
    `revenue_cb` for Crunchbase).

    Data Sources:
        - LinkedIn (_lc): Company profiles, followers, employees
        - Slintel (_sl): Tech stack, company news
        - Owler (_ow): Revenue, funding, competitors
        - Crunchbase (_cb): Funding rounds, investors, IPO status
        - Indeed (_in): Job listings, reviews, salaries
        - ZoomInfo (_zi): Contacts, org charts, tech stack
        - Glassdoor (_gd): Ratings, reviews, salaries

    Example:
        >>> companies = client.datasets.companies_enriched
        >>> # Discover available fields
        >>> metadata = await companies.get_metadata()
        >>> print(f"Total fields: {len(metadata.fields)}")
        >>>
        >>> # Get fields by source
        >>> linkedin_fields = await companies.get_fields_by_source("linkedin")
        >>> crunchbase_fields = await companies.get_fields_by_source("crunchbase")
        >>>
        >>> # Filter companies
        >>> snapshot_id = await companies(
        ...     filter={"name": "industries_lc", "operator": "=", "value": "Technology"},
        ...     records_limit=100
        ... )
        >>> data = await companies.download(snapshot_id)
    """

    # TODO: Replace with actual dataset ID
    DATASET_ID = "gd_lxxxxxxxxxxxxxx"  # Get from Bright Data console
    NAME = "companies_enriched"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_source: Optional[Dict[str, List[str]]] = None

    async def get_fields_by_source(self, source: str, include_inactive: bool = False) -> List[str]:
        """
        Get field names from a specific data source.

        Args:
            source: Source name - one of: linkedin, slintel, owler,
                    crunchbase, indeed, zoominfo, glassdoor
            include_inactive: Include inactive fields (default: False)

        Returns:
            List of field names from that source

        Example:
            >>> linkedin_fields = await companies.get_fields_by_source("linkedin")
            >>> # ['url_lc', 'name_lc', 'followers_lc', ...]
        """
        metadata = await self.get_metadata()
        suffix = self._get_suffix_for_source(source)

        if suffix is None:
            raise ValueError(
                f"Unknown source: {source}. " f"Valid sources: {list(SOURCES.values())}"
            )

        fields = []
        for name, field_info in metadata.fields.items():
            if name.endswith(suffix):
                if include_inactive or field_info.active:
                    fields.append(name)

        return sorted(fields)

    async def get_all_sources(self) -> Dict[str, List[str]]:
        """
        Get all fields grouped by data source.

        Returns:
            Dict mapping source name to list of field names

        Example:
            >>> sources = await companies.get_all_sources()
            >>> for source, fields in sources.items():
            ...     print(f"{source}: {len(fields)} fields")
        """
        if self._fields_by_source is not None:
            return self._fields_by_source

        metadata = await self.get_metadata()
        result: Dict[str, List[str]] = {source: [] for source in SOURCES.values()}
        result["other"] = []  # Fields without recognized suffix

        for name, field_info in metadata.fields.items():
            if not field_info.active:
                continue

            source_found = False
            for suffix, source_name in SOURCES.items():
                if name.endswith(suffix):
                    result[source_name].append(name)
                    source_found = True
                    break

            if not source_found:
                result["other"].append(name)

        # Sort each list
        for source in result:
            result[source] = sorted(result[source])

        self._fields_by_source = result
        return result

    async def get_common_fields(self) -> Dict[str, Dict[str, str]]:
        """
        Get common field types across sources.

        Returns:
            Dict mapping concept to source fields.
            E.g., {"name": {"linkedin": "name_lc", "crunchbase": "name_cb"}}

        Example:
            >>> common = await companies.get_common_fields()
            >>> # Get name from all sources that have it
            >>> name_fields = common.get("name", {})
        """
        # Common field patterns across sources
        common_patterns = {
            "name": [
                "name_lc",
                "name_sl",
                "companyName_ow",
                "name_cb",
                "name_in",
                "name_zi",
                "company_gd",
            ],
            "url": ["url_lc", "url_sl", "url_ow", "url_cb", "url_in", "url_zi", "url_gd"],
            "website": [
                "website_lc",
                "website_sl",
                "website_ow",
                "website_cb",
                "website_in",
                "website_zi",
                "details_website_gd",
            ],
            "industry": [
                "industries_lc",
                "industries_sl",
                "industries_ow",
                "industries_cb",
                "industry_in",
                "industry_zi",
                "industry_gd",
            ],
            "employees": [
                "employees_lc",
                "num_employees_sl",
                "employeeCount_ow",
                "num_employees_cb",
                "company_size_in",
                "employees_zi",
                "details_size_gd",
            ],
            "revenue": ["revenue_ow", "revenue_zi", "revenue_in", "details_revenue_gd"],
            "founded": ["founded_lc", "founded_ow", "founded_date_cb", "details_founded_gd"],
            "country": [
                "country_code_lc",
                "country_code_sl",
                "country_ow",
                "country_code_cb",
                "country_code_in",
                "country_code_gd",
            ],
            "description": [
                "about_lc",
                "about_sl",
                "description_ow",
                "about_cb",
                "description_in",
                "description_zi",
            ],
            "logo": ["logo_lc", "logo_sl", "image_cb", "logo_in", "logo_gd"],
            "headquarters": [
                "headquarters_lc",
                "location_sl",
                "city_ow",
                "location_cb",
                "headquarters_in",
                "headquarters_zi",
                "details_headquarters_gd",
            ],
        }

        metadata = await self.get_metadata()
        available_fields = set(metadata.fields.keys())

        result: Dict[str, Dict[str, str]] = {}
        for concept, field_names in common_patterns.items():
            result[concept] = {}
            for field_name in field_names:
                if field_name in available_fields:
                    # Extract source from suffix
                    for suffix, source_name in SOURCES.items():
                        if field_name.endswith(suffix):
                            result[concept][source_name] = field_name
                            break

        return result

    async def search_fields(self, keyword: str) -> List[str]:
        """
        Search for fields containing a keyword.

        Args:
            keyword: Keyword to search for (case-insensitive)

        Returns:
            List of matching field names

        Example:
            >>> funding_fields = await companies.search_fields("funding")
            >>> # ['funding_lc', 'totalFunding_ow', 'funding_rounds_cb', ...]
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

    def _get_suffix_for_source(self, source: str) -> Optional[str]:
        """Get the field suffix for a source name."""
        source_lower = source.lower()
        for suffix, name in SOURCES.items():
            if name == source_lower:
                return suffix
        return None

    @staticmethod
    def get_source_for_field(field_name: str) -> Optional[str]:
        """
        Get the data source for a field name.

        Args:
            field_name: Field name (e.g., "name_lc")

        Returns:
            Source name (e.g., "linkedin") or None if not recognized
        """
        for suffix, source_name in SOURCES.items():
            if field_name.endswith(suffix):
                return source_name
        return None

    @classmethod
    def list_sources(cls) -> List[str]:
        """
        List all available data sources.

        Returns:
            List of source names
        """
        return list(SOURCES.values())
