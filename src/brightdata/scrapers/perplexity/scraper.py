"""
Perplexity scraper - AI-powered search with citations.

Supports:
- Prompt-based Perplexity search
- Country-specific search
- Markdown export option
- Batch processing of multiple prompts

API Specifications:
- client.scrape.perplexity.search(prompt, country, ..., timeout=180)       # async
- client.scrape.perplexity.search_sync(prompt, country, ..., timeout=180)  # sync
"""

import asyncio
from typing import List, Any, Optional, Union

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_SHORT, COST_PER_RECORD_PERPLEXITY
from ...exceptions import ValidationError


@register("perplexity")
class PerplexityScraper(BaseWebScraper):
    """
    Perplexity AI search scraper.

    Provides access to Perplexity AI through Bright Data's Perplexity dataset.
    Supports prompts with country-specific search and markdown export.

    Methods:
        search(): Single or batch prompt search (async)
        search_sync(): Single or batch prompt search (sync)

    Example:
        >>> scraper = PerplexityScraper(bearer_token="token")
        >>>
        >>> # Async
        >>> result = await scraper.search(
        ...     prompt="What are the latest AI trends?",
        ...     country="US"
        ... )
        >>>
        >>> # Sync
        >>> result = scraper.search_sync(
        ...     prompt="What are the latest AI trends?",
        ...     country="US"
        ... )

    Response data fields:
        - url (str): The Perplexity search URL generated
        - prompt (str): The full prompt with context
        - answer_html (str): HTML-formatted response content
        - suggested_followup (list): Array of suggested follow-up questions
        - citations (list): Array of citation objects with:
            - domain (str): Source domain
            - position (str): Citation position number
            - title (str): Source title
            - url (str): Source URL
        - web_search_query (list): Array of search queries used
    """

    DATASET_ID = "gd_m7dhdot1vw9a7gc1n"  # Perplexity dataset
    PLATFORM_NAME = "perplexity"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_SHORT
    COST_PER_RECORD = COST_PER_RECORD_PERPLEXITY

    # ============================================================================
    # SEARCH METHODS
    # ============================================================================

    async def search(
        self,
        prompt: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        index: Optional[Union[int, List[int]]] = None,
        export_markdown_file: Optional[Union[bool, List[bool]]] = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: Optional[int] = None,
    ) -> ScrapeResult:
        """
        Search Perplexity AI with prompt(s) (async).

        Args:
            prompt: The search prompt(s) to send to Perplexity (required)
            country: Country code(s) for search context (e.g., "US", "GB")
            index: Unique ID(s) for tracking requests
            export_markdown_file: Export response as markdown file
            poll_interval: Seconds between status checks (default: 10)
            poll_timeout: Maximum seconds to wait (default: 180)

        Returns:
            ScrapeResult with Perplexity response

        Example:
            >>> # Single prompt
            >>> result = await scraper.search(
            ...     prompt="What are the latest trends in AI?",
            ...     country="US"
            ... )
            >>> print(result.data['answer_html'])
            >>> print(result.data['citations'])
            >>>
            >>> # Batch prompts
            >>> result = await scraper.search(
            ...     prompt=["What is Python?", "What is JavaScript?"],
            ...     country=["US", "GB"]
            ... )
        """
        if not prompt:
            raise ValidationError("Prompt is required")

        # Normalize to list for batch processing
        prompts = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompts)

        # Normalize all parameters to match batch size
        countries = self._normalize_param(country, batch_size, "US")
        indices = self._normalize_param(index, batch_size, None)
        export_markdowns = self._normalize_param(export_markdown_file, batch_size, None)

        # Validate prompts
        for p in prompts:
            if not p or not isinstance(p, str):
                raise ValidationError("Each prompt must be a non-empty string")

        # Build payload - URL is fixed to https://www.perplexity.ai
        payload = []
        for i in range(batch_size):
            item = {
                "url": "https://www.perplexity.ai",
                "prompt": prompts[i],
            }

            if countries[i]:
                item["country"] = countries[i].upper()

            if indices[i] is not None:
                item["index"] = indices[i]

            if export_markdowns[i] is not None:
                item["export_markdown_file"] = export_markdowns[i]

            payload.append(item)

        # Execute workflow
        timeout = poll_timeout or self.MIN_POLL_TIMEOUT
        sdk_function = get_caller_function_name()

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID,
            poll_interval=poll_interval,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            normalize_func=self.normalize_result,
        )

        # Set fixed URL
        result.url = "https://www.perplexity.ai"

        return result

    def search_sync(
        self,
        prompt: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        index: Optional[Union[int, List[int]]] = None,
        export_markdown_file: Optional[Union[bool, List[bool]]] = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: Optional[int] = None,
    ) -> ScrapeResult:
        """
        Search Perplexity AI with prompt(s) (sync).

        See search() for full documentation.

        Example:
            >>> result = scraper.search_sync(
            ...     prompt="Explain quantum computing",
            ...     country="US"
            ... )
        """

        async def _run():
            async with self.engine:
                return await self.search(
                    prompt=prompt,
                    country=country,
                    index=index,
                    export_markdown_file=export_markdown_file,
                    poll_interval=poll_interval,
                    poll_timeout=poll_timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # SEARCH TRIGGER/STATUS/FETCH (Manual Control)
    # ============================================================================

    async def search_trigger(
        self,
        prompt: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        index: Optional[Union[int, List[int]]] = None,
        export_markdown_file: Optional[Union[bool, List[bool]]] = None,
    ) -> ScrapeJob:
        """
        Trigger Perplexity search (async - manual control).

        Starts a search operation and returns immediately with a Job object.
        Use the Job to check status and fetch results when ready.

        Args:
            prompt: The search prompt(s) to send to Perplexity (required)
            country: Country code(s) for search context
            index: Unique ID(s) for tracking requests
            export_markdown_file: Export response as markdown file

        Returns:
            ScrapeJob object for status checking and result fetching

        Example:
            >>> job = await scraper.search_trigger("What is machine learning?")
            >>> print(f"Job ID: {job.snapshot_id}")
            >>> status = await job.status()
            >>> if status == "ready":
            ...     data = await job.fetch()
        """
        if not prompt:
            raise ValidationError("Prompt is required")

        # Normalize to list
        prompts = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompts)

        # Normalize parameters
        countries = self._normalize_param(country, batch_size, "US")
        indices = self._normalize_param(index, batch_size, None)
        export_markdowns = self._normalize_param(export_markdown_file, batch_size, None)

        # Build payload
        payload = []
        for i in range(batch_size):
            item = {
                "url": "https://www.perplexity.ai",
                "prompt": prompts[i],
            }

            if countries[i]:
                item["country"] = countries[i].upper()

            if indices[i] is not None:
                item["index"] = indices[i]

            if export_markdowns[i] is not None:
                item["export_markdown_file"] = export_markdowns[i]

            payload.append(item)

        # Trigger the scrape
        snapshot_id = await self.api_client.trigger(payload=payload, dataset_id=self.DATASET_ID)

        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )

    def search_trigger_sync(
        self,
        prompt: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        index: Optional[Union[int, List[int]]] = None,
        export_markdown_file: Optional[Union[bool, List[bool]]] = None,
    ) -> ScrapeJob:
        """Trigger Perplexity search (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.search_trigger(prompt, country, index, export_markdown_file)

        return asyncio.run(_run())

    async def search_status(self, snapshot_id: str) -> str:
        """
        Check Perplexity search status (async).

        Args:
            snapshot_id: Snapshot ID from trigger operation

        Returns:
            Status string: "ready", "in_progress", "error"

        Example:
            >>> status = await scraper.search_status(snapshot_id)
        """
        return await self._check_status_async(snapshot_id)

    def search_status_sync(self, snapshot_id: str) -> str:
        """Check Perplexity search status (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.search_status(snapshot_id)

        return asyncio.run(_run())

    async def search_fetch(self, snapshot_id: str) -> Any:
        """
        Fetch Perplexity search results (async).

        Args:
            snapshot_id: Snapshot ID from trigger operation

        Returns:
            Search results data

        Example:
            >>> data = await scraper.search_fetch(snapshot_id)
        """
        return await self._fetch_results_async(snapshot_id)

    def search_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch Perplexity search results (sync wrapper)."""

        async def _run():
            async with self.engine:
                return await self.search_fetch(snapshot_id)

        return asyncio.run(_run())

    # ============================================================================
    # SCRAPE OVERRIDE (Perplexity doesn't use URL-based scraping)
    # ============================================================================

    async def scrape_async(
        self, urls: Union[str, List[str]], **kwargs
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        Perplexity doesn't support URL-based scraping.

        Use search() or search_sync() methods instead.
        """
        raise NotImplementedError(
            "Perplexity scraper doesn't support URL-based scraping. "
            "Use search() or search_sync() methods instead."
        )

    def scrape(self, urls: Union[str, List[str]], **kwargs):
        """Perplexity doesn't support URL-based scraping."""
        raise NotImplementedError(
            "Perplexity scraper doesn't support URL-based scraping. "
            "Use search() or search_sync() methods instead."
        )

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _normalize_param(
        self,
        param: Optional[Union[Any, List[Any]]],
        target_length: int,
        default_value: Any = None,
    ) -> List[Any]:
        """
        Normalize parameter to list of specified length.

        Args:
            param: Single value or list
            target_length: Desired list length
            default_value: Default value if param is None

        Returns:
            List of values with target_length
        """
        if param is None:
            return [default_value] * target_length

        if isinstance(param, (str, bool, int)):
            # Single value - repeat for batch
            return [param] * target_length

        if isinstance(param, list):
            # Extend or truncate to match target length
            if len(param) < target_length:
                # Repeat last value or use default
                last_val = param[-1] if param else default_value
                return param + [last_val] * (target_length - len(param))
            return param[:target_length]

        return [default_value] * target_length
