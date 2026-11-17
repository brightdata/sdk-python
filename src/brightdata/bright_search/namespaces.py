"""Public Business and E-commerce categories within client.search."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING

from .models import (
    BrightSearchDebug,
    BrightSearchMode,
    BrightSearchPage,
    BrightSearchQuery,
    BrightSearchView,
)

if TYPE_CHECKING:
    from ..serp.service import SearchService


class BusinessSearchService:
    """Search company and professional records through client.search.business."""

    def __init__(self, search_service: "SearchService"):
        self._search_service = search_service

    async def companies(
        self,
        query: BrightSearchQuery,
        *,
        mode: BrightSearchMode,
        source: Optional[str] = None,
        view: Optional[BrightSearchView] = None,
        offset: int = 0,
        limit: int = 10,
        debug: Optional[BrightSearchDebug] = None,
    ) -> BrightSearchPage:
        """Search company records and return one page.

        Use a structured query with mode="ludicrous", or natural language
        with mode="instant" or "smart". Source and view default on the server
        to linkedin_company and id_only. Pagination and retries are explicit
        caller decisions.

        Example:
            >>> async with BrightDataClient(auto_create_zones=False) as client:
            ...     page = await client.search.business.companies(
            ...         "US software companies", mode="instant", view="summary"
            ...     )
            ...     for document in page.documents:
            ...         print(document["bright_id"], document["data"].get("name"))
        """
        return await self._search_service._bright_search().search(
            "company",
            query,
            mode=mode,
            source=source,
            view=view,
            offset=offset,
            limit=limit,
            debug=debug,
        )

    async def people(
        self,
        query: BrightSearchQuery,
        *,
        mode: BrightSearchMode,
        source: Optional[str] = None,
        view: Optional[BrightSearchView] = None,
        offset: int = 0,
        limit: int = 10,
        debug: Optional[BrightSearchDebug] = None,
    ) -> BrightSearchPage:
        """Search professional records using the same options as companies().

        The default source is linkedin_people. All projected entity fields
        are optional; matched is a reached count, not generally a total.
        """
        return await self._search_service._bright_search().search(
            "people",
            query,
            mode=mode,
            source=source,
            view=view,
            offset=offset,
            limit=limit,
            debug=debug,
        )


class EcommerceSearchService:
    """Search product records through client.search.ecommerce."""

    def __init__(self, search_service: "SearchService"):
        self._search_service = search_service

    async def products(
        self,
        query: Dict[str, Any],
        *,
        mode: Literal["ludicrous"],
        source: Optional[str] = None,
        view: Optional[BrightSearchView] = None,
        offset: int = 0,
        limit: int = 10,
        debug: Optional[BrightSearchDebug] = None,
    ) -> BrightSearchPage:
        """Search products with a structured query and mode="ludicrous".

        The default source retail_products_live supports id_only, full, and custom
        field lists; it does not publish a summary view.
        """
        return await self._search_service._bright_search().search(
            "ecommerce",
            query,
            mode=mode,
            source=source,
            view=view,
            offset=offset,
            limit=limit,
            debug=debug,
        )
