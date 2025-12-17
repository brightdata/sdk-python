"""
ChatGPT Search Service - Prompt-based discovery.

API Specification:
- client.search.chatGPT(prompt, country, secondaryPrompt, webSearch, timeout) - async
- client.search.chatGPT_sync(prompt, country, secondaryPrompt, webSearch, timeout) - sync

All parameters accept str | array<str> or bool | array<bool>
Uses standard async workflow (trigger/poll/fetch).
"""

import asyncio
from typing import Union, List, Optional, Dict, Any

from ...core.engine import AsyncEngine
from ...models import ScrapeResult
from ...exceptions import ValidationError
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_SHORT, COST_PER_RECORD_CHATGPT
from ..api_client import DatasetAPIClient
from ..workflow import WorkflowExecutor


class ChatGPTSearchService:
    """
    ChatGPT Search Service for prompt-based discovery.

    Sends prompts to ChatGPT and retrieves structured responses.
    Supports batch processing and web search capabilities.

    Example:
        >>> search = ChatGPTSearchService(bearer_token="token")
        >>>
        >>> # Async
        >>> result = await search.chatGPT(
        ...     prompt="Explain Python async programming",
        ...     country="us",
        ...     webSearch=True,
        ...     timeout=180
        ... )
        >>>
        >>> # Sync
        >>> result = search.chatGPT_sync(
        ...     prompt="Explain Python async programming",
        ...     country="us",
        ...     webSearch=True,
        ...     timeout=180
        ... )
    """

    DATASET_ID = "gd_m7aof0k82r803d5bjm"  # ChatGPT dataset

    def __init__(self, bearer_token: str, engine: Optional[AsyncEngine] = None):
        """
        Initialize ChatGPT search service.

        Args:
            bearer_token: Bright Data API token
            engine: Optional AsyncEngine instance. If not provided, creates a new one.
                    Allows dependency injection for testing and flexibility.
        """
        self.bearer_token = bearer_token
        self.engine = engine if engine is not None else AsyncEngine(bearer_token)
        self.api_client = DatasetAPIClient(self.engine)
        self.workflow_executor = WorkflowExecutor(
            api_client=self.api_client,
            platform_name="chatgpt",
            cost_per_record=COST_PER_RECORD_CHATGPT,
        )

    # ============================================================================
    # CHATGPT PROMPT DISCOVERY
    # ============================================================================

    async def chatGPT(
        self,
        prompt: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        secondaryPrompt: Optional[Union[str, List[str]]] = None,
        webSearch: Optional[Union[bool, List[bool]]] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Send prompt(s) to ChatGPT (async).

        Uses standard async workflow: trigger job, poll until ready, then fetch results.

        Args:
            prompt: Prompt(s) to send to ChatGPT (required)
            country: Country code(s) in 2-letter format (optional)
            secondaryPrompt: Secondary prompt(s) for continued conversation (optional)
            webSearch: Enable web search capability (optional)
            timeout: Maximum wait time in seconds for polling (default: 180)

        Returns:
            ScrapeResult with ChatGPT response(s)

        Example:
            >>> result = await search.chatGPT(
            ...     prompt="What is Python?",
            ...     country="us",
            ...     webSearch=True,
            ...     timeout=180
            ... )
            >>>
            >>> # Batch prompts
            >>> result = await search.chatGPT(
            ...     prompt=["What is Python?", "What is JavaScript?"],
            ...     country=["us", "us"],
            ...     webSearch=[False, False]
            ... )
        """
        # Validate required parameters
        if not prompt:
            raise ValidationError("prompt parameter is required")

        # Normalize to lists for batch processing
        prompts = [prompt] if isinstance(prompt, str) else prompt
        batch_size = len(prompts)

        # Normalize all parameters to lists
        countries = self._normalize_param(country, batch_size, "US")
        secondary_prompts = self._normalize_param(secondaryPrompt, batch_size, None)
        web_searches = self._normalize_param(webSearch, batch_size, False)

        # Validate country codes
        for c in countries:
            if c and len(c) != 2:
                raise ValidationError(
                    f"Country code must be 2-letter format, got: {c}. " f"Examples: US, GB, FR, DE"
                )

        # Build payload (URL fixed to https://chatgpt.com per spec)
        payload = []
        for i in range(batch_size):
            item: Dict[str, Any] = {
                "url": "https://chatgpt.com",  # Fixed URL per API spec
                "prompt": prompts[i],
                "country": countries[i].upper() if countries[i] else "US",
                "web_search": web_searches[i] if isinstance(web_searches[i], bool) else False,
            }

            if secondary_prompts[i]:
                item["additional_prompt"] = secondary_prompts[i]

            payload.append(item)

        # Execute with standard async workflow
        result = await self._execute_async_mode(payload=payload, timeout=timeout)

        return result


    def chatGPT_sync(
        self,
        prompt: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        secondaryPrompt: Optional[Union[str, List[str]]] = None,
        webSearch: Optional[Union[bool, List[bool]]] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Send prompt(s) to ChatGPT (sync wrapper).

        See chatGPT() for full documentation.

        Example:
            >>> result = search.chatGPT_sync(
            ...     prompt="Explain async programming",
            ...     webSearch=True
            ... )
        """
        async def _run():
            async with self.engine:
                return await self.chatGPT(
                    prompt=prompt,
                    country=country,
                    secondaryPrompt=secondaryPrompt,
                    webSearch=webSearch,
                    timeout=timeout,
                )
        return asyncio.run(_run())

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _normalize_param(
        self, param: Optional[Union[Any, List[Any]]], target_length: int, default_value: Any = None
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

    async def _execute_async_mode(
        self,
        payload: List[Dict[str, Any]],
        timeout: int,
    ) -> ScrapeResult:
        """Execute using standard async workflow (/trigger endpoint with polling)."""
        # Use workflow executor for trigger/poll/fetch
        sdk_function = get_caller_function_name()

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=self.DATASET_ID,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
        )

        # Set fixed URL per spec
        result.url = "https://chatgpt.com"
        return result
