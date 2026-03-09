"""
DigiKey scraper - URL-based collection and category discovery for electronic components.

Supports:
- Products: collect by URL
- Category discovery: discover new parts by category URL

API Specifications:
- client.scrape.digikey.products(url, ...)                     # async
- client.scrape.digikey.products_sync(url, ...)                # sync
- client.scrape.digikey.discover_by_category(url, ...)         # async
- client.scrape.digikey.discover_by_category_sync(url, ...)    # sync
"""

import asyncio
from typing import List, Any, Union

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.validation import validate_url, validate_url_list
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, DEFAULT_COST_PER_RECORD


@register("digikey")
class DigiKeyScraper(BaseWebScraper):
    """
    DigiKey scraper for electronic components.

    Extracts structured data from DigiKey URLs for:
    - Products (collect by URL)
    - Category discovery (discover new parts from category pages)

    Example:
        >>> scraper = DigiKeyScraper(bearer_token="token")
        >>>
        >>> # Collect product data
        >>> result = await scraper.products(
        ...     url="https://www.digikey.com/en/products/detail/..."
        ... )
        >>>
        >>> # Discover products by category
        >>> result = await scraper.discover_by_category(
        ...     url="https://www.digikey.com/en/products/category/..."
        ... )
    """

    # Dataset ID (single dataset for all operations)
    DATASET_ID = "gd_lj74waf72416ro0k65"

    PLATFORM_NAME = "digikey"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_MEDIUM
    COST_PER_RECORD = DEFAULT_COST_PER_RECORD

    # ============================================================================
    # PRODUCTS - Collect by URL
    # ============================================================================

    async def products(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Collect DigiKey product data by URL (async).

        Args:
            url: Product URL(s) like https://www.digikey.com/en/products/detail/...
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult or List[ScrapeResult] with product data

        Example:
            >>> result = await scraper.products(
            ...     url="https://www.digikey.com/en/products/detail/STMicroelectronics/STM32F407VGT6/2747117"
            ... )
            >>> print(result.data)
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        is_single = isinstance(url, str)
        url_list = [url] if is_single else url
        payload = [{"url": u} for u in url_list]

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
        )

        if is_single and isinstance(result.data, list) and len(result.data) == 1:
            result.url = url if isinstance(url, str) else url[0]
            result.data = result.data[0]
        return result

    def products_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Collect DigiKey product data by URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.products(url, timeout)

        return asyncio.run(_run())

    # --- Products Trigger/Status/Fetch ---

    async def products_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger DigiKey products collection (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"url": u} for u in url_list]

        snapshot_id = await self.api_client.trigger(payload=payload, dataset_id=self.DATASET_ID)
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def products_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger DigiKey products collection (sync)."""
        return asyncio.run(self.products_trigger(url))

    async def products_status(self, snapshot_id: str) -> str:
        """Check DigiKey products collection status."""
        return await self._check_status_async(snapshot_id)

    def products_status_sync(self, snapshot_id: str) -> str:
        """Check DigiKey products collection status (sync)."""
        return asyncio.run(self.products_status(snapshot_id))

    async def products_fetch(self, snapshot_id: str) -> Any:
        """Fetch DigiKey products results."""
        return await self._fetch_results_async(snapshot_id)

    def products_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch DigiKey products results (sync)."""
        return asyncio.run(self.products_fetch(snapshot_id))

    # ============================================================================
    # DISCOVER BY CATEGORY
    # ============================================================================

    async def discover_by_category(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Discover DigiKey products by category URL (async).

        Crawls category pages to discover new parts.

        Args:
            url: Category URL(s) like https://www.digikey.com/en/products/category/...
            timeout: Maximum wait time in seconds (default: 240)

        Returns:
            ScrapeResult with discovered products

        Example:
            >>> result = await scraper.discover_by_category(
            ...     url="https://www.digikey.com/en/products/category/integrated-circuits/36"
            ... )
        """
        if isinstance(url, str):
            validate_url(url)
        else:
            validate_url_list(url)

        url_list = [url] if isinstance(url, str) else url
        payload = [{"category_url": u} for u in url_list]

        sdk_function = get_caller_function_name()
        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
            extra_params={"type": "discover_new", "discover_by": "category"},
        )
        return result

    def discover_by_category_sync(
        self,
        url: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """Discover DigiKey products by category URL (sync)."""

        async def _run():
            async with self.engine:
                return await self.discover_by_category(url, timeout)

        return asyncio.run(_run())

    # --- Discover Trigger/Status/Fetch ---

    async def discover_by_category_trigger(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger DigiKey category discovery (manual control)."""
        url_list = [url] if isinstance(url, str) else url
        payload = [{"category_url": u} for u in url_list]

        snapshot_id = await self.api_client.trigger(
            payload=payload,
            dataset_id=self.DATASET_ID,
            extra_params={"type": "discover_new", "discover_by": "category"},
        )
        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def discover_by_category_trigger_sync(self, url: Union[str, List[str]]) -> ScrapeJob:
        """Trigger DigiKey category discovery (sync)."""
        return asyncio.run(self.discover_by_category_trigger(url))

    async def discover_by_category_status(self, snapshot_id: str) -> str:
        """Check DigiKey category discovery status."""
        return await self._check_status_async(snapshot_id)

    def discover_by_category_status_sync(self, snapshot_id: str) -> str:
        """Check DigiKey category discovery status (sync)."""
        return asyncio.run(self.discover_by_category_status(snapshot_id))

    async def discover_by_category_fetch(self, snapshot_id: str) -> Any:
        """Fetch DigiKey category discovery results."""
        return await self._fetch_results_async(snapshot_id)

    def discover_by_category_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch DigiKey category discovery results (sync)."""
        return asyncio.run(self.discover_by_category_fetch(snapshot_id))
