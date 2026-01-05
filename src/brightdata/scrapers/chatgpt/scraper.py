"""
ChatGPT scraper - ChatGPT conversation extraction.

Supports:
- Prompt-based ChatGPT interactions
- Web search enabled prompts
- Follow-up conversations
"""

import asyncio
from typing import List, Any, Optional, Union

from ..base import BaseWebScraper
from ..registry import register
from ..job import ScrapeJob
from ...models import ScrapeResult
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_LONG, COST_PER_RECORD_CHATGPT
from ...exceptions import ValidationError


@register("chatgpt")
class ChatGPTScraper(BaseWebScraper):
    """
    ChatGPT interaction scraper.

    Provides access to ChatGPT through Bright Data's ChatGPT dataset.
    Supports prompts with optional web search and follow-up conversations.

    Methods:
        prompt(): Single prompt interaction (async)
        prompt_sync(): Single prompt interaction (sync)
        prompts(): Batch prompt processing (async)
        prompts_sync(): Batch prompt processing (sync)

    Example:
        >>> scraper = ChatGPTScraper(bearer_token="token")
        >>>
        >>> # Async
        >>> result = await scraper.prompt(
        ...     prompt="Explain async programming in Python",
        ...     web_search=False
        ... )
        >>>
        >>> # Sync
        >>> result = scraper.prompt_sync(
        ...     prompt="Explain async programming in Python",
        ...     web_search=False
        ... )
    """

    DATASET_ID = "gd_m7aof0k82r803d5bjm"  # ChatGPT dataset
    PLATFORM_NAME = "chatgpt"
    MIN_POLL_TIMEOUT = DEFAULT_TIMEOUT_LONG  # ChatGPT usually responds faster
    COST_PER_RECORD = COST_PER_RECORD_CHATGPT  # ChatGPT interactions cost more

    # ============================================================================
    # PROMPT METHODS
    # ============================================================================

    async def prompt(
        self,
        prompt: str,
        country: str = "us",
        web_search: bool = False,
        additional_prompt: Optional[str] = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: Optional[int] = None,
    ) -> ScrapeResult:
        """
        Send single prompt to ChatGPT (async).

        Args:
            prompt: The prompt/question to send to ChatGPT
            country: Country code for ChatGPT region
            web_search: Enable web search for up-to-date information
            additional_prompt: Follow-up prompt after initial response
            poll_interval: Seconds between status checks
            poll_timeout: Maximum seconds to wait

        Returns:
            ScrapeResult with ChatGPT response

        Example:
            >>> result = await scraper.prompt(
            ...     prompt="What are the latest trends in AI?",
            ...     web_search=True
            ... )
            >>> print(result.data['response'])
        """
        if not prompt or not isinstance(prompt, str):
            raise ValidationError("Prompt must be a non-empty string")

        # Build payload - ChatGPT scraper requires url field pointing to ChatGPT
        payload = [
            {
                "url": "https://chatgpt.com/",
                "prompt": prompt,
                "country": country.upper(),
                "web_search": web_search,
            }
        ]

        if additional_prompt:
            payload[0]["additional_prompt"] = additional_prompt

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

        return result


    def prompt_sync(
        self,
        prompt: str,
        country: str = "us",
        web_search: bool = False,
        additional_prompt: Optional[str] = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: Optional[int] = None,
    ) -> ScrapeResult:
        """
        Send prompt to ChatGPT (sync).

        See prompt() for full documentation.

        Example:
            >>> result = scraper.prompt_sync("Explain Python asyncio")
        """
        async def _run():
            async with self.engine:
                return await self.prompt(
                    prompt=prompt,
                    country=country,
                    web_search=web_search,
                    additional_prompt=additional_prompt,
                    poll_interval=poll_interval,
                    poll_timeout=poll_timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # PROMPT TRIGGER/STATUS/FETCH (Manual Control)
    # ============================================================================

    async def prompt_trigger(
        self,
        prompt: str,
        country: str = "us",
        web_search: bool = False,
        additional_prompt: Optional[str] = None,
    ) -> "ScrapeJob":
        """Trigger ChatGPT prompt (async - manual control)."""
        from ..job import ScrapeJob

        if not prompt or not isinstance(prompt, str):
            raise ValidationError("Prompt must be a non-empty string")

        # Build payload
        payload = [
            {
                "url": "https://chatgpt.com/",
                "prompt": prompt,
                "country": country.upper(),
                "web_search": web_search,
            }
        ]

        if additional_prompt:
            payload[0]["additional_prompt"] = additional_prompt

        # Trigger the scrape
        snapshot_id = await self.api_client.trigger(payload=payload, dataset_id=self.DATASET_ID)

        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )


    def prompt_trigger_sync(
        self,
        prompt: str,
        country: str = "us",
        web_search: bool = False,
        additional_prompt: Optional[str] = None,
    ) -> "ScrapeJob":
        """Trigger ChatGPT prompt (sync wrapper)."""
        async def _run():
            async with self.engine:
                return await self.prompt_trigger(prompt, country, web_search, additional_prompt)
        return asyncio.run(_run())

    async def prompt_status(self, snapshot_id: str) -> str:
        """Check ChatGPT prompt status (async)."""
        return await self._check_status_async(snapshot_id)


    def prompt_status_sync(self, snapshot_id: str) -> str:
        """Check ChatGPT prompt status (sync wrapper)."""
        async def _run():
            async with self.engine:
                return await self.prompt_status(snapshot_id)
        return asyncio.run(_run())

    async def prompt_fetch(self, snapshot_id: str) -> Any:
        """Fetch ChatGPT prompt results (async)."""
        return await self._fetch_results_async(snapshot_id)


    def prompt_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch ChatGPT prompt results (sync wrapper)."""
        async def _run():
            async with self.engine:
                return await self.prompt_fetch(snapshot_id)
        return asyncio.run(_run())

    # ============================================================================
    # BATCH PROMPTS METHODS
    # ============================================================================

    async def prompts(
        self,
        prompts: List[str],
        countries: Optional[List[str]] = None,
        web_searches: Optional[List[bool]] = None,
        additional_prompts: Optional[List[str]] = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: Optional[int] = None,
    ) -> ScrapeResult:
        """
        Send multiple prompts to ChatGPT in batch (async).

        Args:
            prompts: List of prompts to send
            countries: List of country codes (one per prompt, optional)
            web_searches: List of web_search flags (one per prompt, optional)
            additional_prompts: List of follow-up prompts (optional)
            poll_interval: Seconds between status checks
            poll_timeout: Maximum seconds to wait

        Returns:
            ScrapeResult with list of ChatGPT responses

        Example:
            >>> result = await scraper.prompts(
            ...     prompts=[
            ...         "Explain Python",
            ...         "Explain JavaScript",
            ...         "Compare both languages"
            ...     ],
            ...     web_searches=[False, False, False]
            ... )
        """
        if not prompts or not isinstance(prompts, list):
            raise ValidationError("Prompts must be a non-empty list")

        # Build batch payload - ChatGPT scraper requires url field
        payload = []
        for i, prompt in enumerate(prompts):
            item = {
                "url": "https://chatgpt.com/",
                "prompt": prompt,
                "country": countries[i].upper() if countries and i < len(countries) else "US",
                "web_search": web_searches[i] if web_searches and i < len(web_searches) else False,
            }

            if additional_prompts and i < len(additional_prompts):
                item["additional_prompt"] = additional_prompts[i]

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

        return result


    def prompts_sync(
        self,
        prompts: List[str],
        countries: Optional[List[str]] = None,
        web_searches: Optional[List[bool]] = None,
        additional_prompts: Optional[List[str]] = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: Optional[int] = None,
    ) -> ScrapeResult:
        """
        Send multiple prompts (sync).

        See prompts() for full documentation.
        """
        async def _run():
            async with self.engine:
                return await self.prompts(
                    prompts=prompts,
                    countries=countries,
                    web_searches=web_searches,
                    additional_prompts=additional_prompts,
                    poll_interval=poll_interval,
                    poll_timeout=poll_timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # PROMPTS TRIGGER/STATUS/FETCH (Manual Control for batch)
    # ============================================================================

    async def prompts_trigger(
        self,
        prompts: List[str],
        countries: Optional[List[str]] = None,
        web_searches: Optional[List[bool]] = None,
        additional_prompts: Optional[List[str]] = None,
    ) -> "ScrapeJob":
        """Trigger ChatGPT batch prompts (async - manual control)."""
        from ..job import ScrapeJob

        if not prompts or not isinstance(prompts, list):
            raise ValidationError("Prompts must be a non-empty list")

        # Build batch payload
        payload = []
        for i, prompt in enumerate(prompts):
            item = {
                "url": "https://chatgpt.com/",
                "prompt": prompt,
                "country": (countries[i] if countries and i < len(countries) else "US").upper(),
                "web_search": web_searches[i] if web_searches and i < len(web_searches) else False,
            }
            if additional_prompts and i < len(additional_prompts):
                item["additional_prompt"] = additional_prompts[i]
            payload.append(item)

        # Trigger the scrape
        snapshot_id = await self.api_client.trigger(payload=payload, dataset_id=self.DATASET_ID)

        return ScrapeJob(
            snapshot_id=snapshot_id,
            api_client=self.api_client,
            platform_name=self.PLATFORM_NAME,
            cost_per_record=self.COST_PER_RECORD,
        )


    def prompts_trigger_sync(
        self,
        prompts: List[str],
        countries: Optional[List[str]] = None,
        web_searches: Optional[List[bool]] = None,
        additional_prompts: Optional[List[str]] = None,
    ) -> "ScrapeJob":
        """Trigger ChatGPT batch prompts (sync wrapper)."""
        async def _run():
            async with self.engine:
                return await self.prompts_trigger(prompts, countries, web_searches, additional_prompts)
        return asyncio.run(_run())

    async def prompts_status(self, snapshot_id: str) -> str:
        """Check ChatGPT batch prompts status (async)."""
        return await self._check_status_async(snapshot_id)


    def prompts_status_sync(self, snapshot_id: str) -> str:
        """Check ChatGPT batch prompts status (sync wrapper)."""
        async def _run():
            async with self.engine:
                return await self.prompts_status(snapshot_id)
        return asyncio.run(_run())

    async def prompts_fetch(self, snapshot_id: str) -> Any:
        """Fetch ChatGPT batch prompts results (async)."""
        return await self._fetch_results_async(snapshot_id)


    def prompts_fetch_sync(self, snapshot_id: str) -> Any:
        """Fetch ChatGPT batch prompts results (sync wrapper)."""
        async def _run():
            async with self.engine:
                return await self.prompts_fetch(snapshot_id)
        return asyncio.run(_run())

    # ============================================================================
    # SCRAPE OVERRIDE (ChatGPT doesn't use URL-based scraping)
    # ============================================================================

    async def scrape(
        self, urls: Union[str, List[str]], **kwargs
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """
        ChatGPT doesn't support URL-based scraping.

        Use prompt() or prompts() methods instead.
        """
        raise NotImplementedError(
            "ChatGPT scraper doesn't support URL-based scraping. "
            "Use prompt() or prompts() methods instead."
        )


    def scrape_sync(self, urls: Union[str, List[str]], **kwargs):
        """ChatGPT doesn't support URL-based scraping."""
        raise NotImplementedError(
            "ChatGPT scraper doesn't support URL-based scraping. "
            "Use prompt() or prompts() methods instead."
        )
