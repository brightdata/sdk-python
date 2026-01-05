"""
Amazon Search Scraper - Discovery/parameter-based operations.

Implements:
- client.search.amazon.products()      - Find products by keyword/category/filters (async)
- client.search.amazon.products_sync() - Find products by keyword/category/filters (sync)

Async methods are the default. Sync methods use asyncio.run() internally.
"""

import asyncio
from typing import Union, List, Optional, Dict, Any

from ...core.engine import AsyncEngine
from ...models import ScrapeResult
from ...exceptions import ValidationError
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_MEDIUM, DEFAULT_COST_PER_RECORD
from ..api_client import DatasetAPIClient
from ..workflow import WorkflowExecutor


class AmazonSearchScraper:
    """
    Amazon Search Scraper for parameter-based discovery.

    Provides discovery methods that search Amazon by parameters
    rather than extracting from specific URLs.

    Example:
        >>> scraper = AmazonSearchScraper(bearer_token="token")
        >>> result = scraper.products(
        ...     keyword="laptop",
        ...     min_price=500,
        ...     max_price=2000
        ... )
    """

    # Amazon dataset IDs
    DATASET_ID_PRODUCTS_SEARCH = "gd_lwdb4vjm1ehb499uxs"  # Amazon Products Search (15.84M records)

    def __init__(self, bearer_token: str, engine: Optional[AsyncEngine] = None):
        """
        Initialize Amazon search scraper.

        Args:
            bearer_token: Bright Data API token
            engine: Optional AsyncEngine instance (reused from client)
        """
        self.bearer_token = bearer_token
        self.engine = engine if engine is not None else AsyncEngine(bearer_token)
        self.api_client = DatasetAPIClient(self.engine)
        self.workflow_executor = WorkflowExecutor(
            api_client=self.api_client,
            platform_name="amazon",
            cost_per_record=DEFAULT_COST_PER_RECORD,
        )

    # ============================================================================
    # PRODUCTS SEARCH (by keyword + filters)
    # ============================================================================

    async def products(
        self,
        keyword: Optional[Union[str, List[str]]] = None,
        url: Optional[Union[str, List[str]]] = None,
        category: Optional[Union[str, List[str]]] = None,
        min_price: Optional[Union[int, List[int]]] = None,
        max_price: Optional[Union[int, List[int]]] = None,
        condition: Optional[Union[str, List[str]]] = None,
        prime_eligible: Optional[bool] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Search Amazon products by keyword and filters.

        Args:
            keyword: Search keyword(s) (e.g., "laptop", "wireless headphones")
            url: Category or search URL(s) (optional, alternative to keyword)
            category: Category name or ID(s) (optional)
            min_price: Minimum price filter(s) in cents (optional)
            max_price: Maximum price filter(s) in cents (optional)
            condition: Product condition(s): "new", "used", "refurbished" (optional)
            prime_eligible: Filter for Prime-eligible products only (optional)
            country: Country code(s) - 2-letter format like "US", "UK" (optional)
            timeout: Operation timeout in seconds (default: 240)

        Returns:
            ScrapeResult with matching products

        Example:
            >>> async with BrightDataClient() as client:
            ...     result = await client.search.amazon.products(
            ...         keyword="laptop",
            ...         min_price=50000,  # $500 in cents
            ...         max_price=200000,  # $2000 in cents
            ...         prime_eligible=True
            ...     )
        """
        # At least one search criteria required
        if not any([keyword, url, category]):
            raise ValidationError(
                "At least one search parameter required " "(keyword, url, or category)"
            )

        # Determine batch size (use longest list)
        batch_size = 1
        if keyword and isinstance(keyword, list):
            batch_size = max(batch_size, len(keyword))
        if url and isinstance(url, list):
            batch_size = max(batch_size, len(url))
        if category and isinstance(category, list):
            batch_size = max(batch_size, len(category))

        # Normalize all parameters to lists
        keywords = self._normalize_param(keyword, batch_size)
        urls = self._normalize_param(url, batch_size)
        categories = self._normalize_param(category, batch_size)
        min_prices = self._normalize_param(min_price, batch_size)
        max_prices = self._normalize_param(max_price, batch_size)
        conditions = self._normalize_param(condition, batch_size)
        countries = self._normalize_param(country, batch_size)

        # Build payload - Amazon Products Search dataset expects keyword field
        payload = []
        for i in range(batch_size):
            item = {}

            # If URL provided directly, use it
            if urls and i < len(urls):
                item["url"] = urls[i]
                # Extract keyword from URL if possible for the keyword field
                if "k=" in urls[i]:
                    import urllib.parse

                    parsed = urllib.parse.urlparse(urls[i])
                    params = urllib.parse.parse_qs(parsed.query)
                    item["keyword"] = params.get("k", [""])[0]
                else:
                    item["keyword"] = ""
            else:
                # Send keyword directly (dataset expects this field)
                item["keyword"] = keywords[i] if keywords and i < len(keywords) else ""

                # Optionally build URL for additional context
                if item["keyword"]:
                    search_url = self._build_amazon_search_url(
                        keyword=item["keyword"],
                        category=categories[i] if categories and i < len(categories) else None,
                        min_price=min_prices[i] if min_prices and i < len(min_prices) else None,
                        max_price=max_prices[i] if max_prices and i < len(max_prices) else None,
                        condition=conditions[i] if conditions and i < len(conditions) else None,
                        prime_eligible=prime_eligible,
                        country=countries[i] if countries and i < len(countries) else None,
                    )
                    item["url"] = search_url

            payload.append(item)

        return await self._execute_search(
            payload=payload,
            dataset_id=self.DATASET_ID_PRODUCTS_SEARCH,
            timeout=timeout,
        )


    def products_sync(
        self,
        keyword: Optional[Union[str, List[str]]] = None,
        url: Optional[Union[str, List[str]]] = None,
        category: Optional[Union[str, List[str]]] = None,
        min_price: Optional[Union[int, List[int]]] = None,
        max_price: Optional[Union[int, List[int]]] = None,
        condition: Optional[Union[str, List[str]]] = None,
        prime_eligible: Optional[bool] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_MEDIUM,
    ) -> ScrapeResult:
        """
        Search Amazon products by keyword and filters (sync version).

        See products() for full documentation.
        """
        async def _run():
            async with self.engine:
                return await self.products(
                    keyword=keyword,
                    url=url,
                    category=category,
                    min_price=min_price,
                    max_price=max_price,
                    condition=condition,
                    prime_eligible=prime_eligible,
                    country=country,
                    timeout=timeout,
                )
        return asyncio.run(_run())

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _normalize_param(
        self, param: Optional[Union[str, int, List[str], List[int]]], target_length: int
    ) -> Optional[List]:
        """
        Normalize parameter to list.

        Args:
            param: String, int, or list
            target_length: Desired list length

        Returns:
            List, or None if param is None
        """
        if param is None:
            return None

        if isinstance(param, (str, int)):
            # Repeat single value for batch
            return [param] * target_length

        return param

    def _build_amazon_search_url(
        self,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        condition: Optional[str] = None,
        prime_eligible: Optional[bool] = None,
        country: Optional[str] = None,
    ) -> str:
        """
        Build Amazon search URL from parameters.

        Amazon API requires URLs, not raw search parameters.
        This method constructs a valid Amazon search URL from the provided filters.

        Args:
            keyword: Search keyword
            category: Category name or ID
            min_price: Minimum price in cents
            max_price: Maximum price in cents
            condition: Product condition
            prime_eligible: Prime eligible filter
            country: Country code

        Returns:
            Amazon search URL

        Example:
            >>> _build_amazon_search_url(
            ...     keyword="laptop",
            ...     min_price=50000,
            ...     max_price=200000,
            ...     prime_eligible=True
            ... )
            'https://www.amazon.com/s?k=laptop&rh=p_36%3A50000-200000%2Cp_85%3A2470955011'
        """
        from urllib.parse import urlencode

        # Determine domain based on country
        domain_map = {
            "US": "amazon.com",
            "UK": "amazon.co.uk",
            "DE": "amazon.de",
            "FR": "amazon.fr",
            "IT": "amazon.it",
            "ES": "amazon.es",
            "CA": "amazon.ca",
            "JP": "amazon.co.jp",
            "IN": "amazon.in",
            "MX": "amazon.com.mx",
            "BR": "amazon.com.br",
            "AU": "amazon.com.au",
        }

        domain = domain_map.get(country.upper() if country else "US", "amazon.com")
        base_url = f"https://www.{domain}/s"

        params = {}
        rh_parts = []  # refinement parameters

        # Keyword
        if keyword:
            params["k"] = keyword

        # Category
        if category:
            params["i"] = category

        # Price range (p_36: price in cents)
        if min_price is not None or max_price is not None:
            min_p = min_price or 0
            max_p = max_price or 999999999
            rh_parts.append(f"p_36:{min_p}-{max_p}")

        # Prime eligible (p_85: Prime)
        if prime_eligible:
            rh_parts.append("p_85:2470955011")

        # Condition (p_n_condition-type)
        if condition:
            condition_map = {
                "new": "p_n_condition-type:New",
                "used": "p_n_condition-type:Used",
                "refurbished": "p_n_condition-type:Refurbished",
            }
            if condition.lower() in condition_map:
                rh_parts.append(condition_map[condition.lower()])

        # Add refinement parameters
        if rh_parts:
            params["rh"] = ",".join(rh_parts)

        # Build URL
        if params:
            url = f"{base_url}?{urlencode(params)}"
        else:
            url = base_url

        return url

    async def _execute_search(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        timeout: int,
    ) -> ScrapeResult:
        """
        Execute search operation via trigger/poll/fetch.

        Args:
            payload: Search parameters
            dataset_id: Amazon dataset ID
            timeout: Operation timeout

        Returns:
            ScrapeResult with search results
        """
        # Use workflow executor for trigger/poll/fetch
        sdk_function = get_caller_function_name()

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=dataset_id,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
        )

        return result
