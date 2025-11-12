"""
ChatGPT Search Service - Prompt-based discovery.

API Specification:
- client.search.chatGPT(prompt, country, secondaryPrompt, webSearch, sync, timeout)

All parameters accept str | array<str> or bool | array<bool>
"""

import asyncio
from typing import Union, List, Optional, Dict, Any
from datetime import datetime, timezone

from ...core.engine import AsyncEngine
from ...models import ScrapeResult
from ...exceptions import ValidationError, APIError


class ChatGPTSearchService:
    """
    ChatGPT Search Service for prompt-based discovery.
    
    Sends prompts to ChatGPT and retrieves structured responses.
    Supports batch processing and web search capabilities.
    
    Example:
        >>> search = ChatGPTSearchService(bearer_token="token")
        >>> result = search.chatGPT(
        ...     prompt="Explain Python async programming",
        ...     country="us",
        ...     webSearch=True,
        ...     sync=True
        ... )
    """
    
    DATASET_ID = "gd_m7aof0k82r803d5bjm"  # ChatGPT dataset
    
    SCRAPE_URL = "https://api.brightdata.com/datasets/v3/scrape"  # Sync
    TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"  # Async
    STATUS_URL = "https://api.brightdata.com/datasets/v3/progress"
    RESULT_URL = "https://api.brightdata.com/datasets/v3/snapshot"
    
    def __init__(self, bearer_token: str):
        """Initialize ChatGPT search service."""
        self.bearer_token = bearer_token
        self.engine = AsyncEngine(bearer_token)
    
    # ============================================================================
    # CHATGPT PROMPT DISCOVERY
    # ============================================================================
    
    async def chatGPT_async(
        self,
        prompt: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        secondaryPrompt: Optional[Union[str, List[str]]] = None,
        webSearch: Optional[Union[bool, List[bool]]] = None,
        sync: bool = True,
        timeout: int = 65,
    ) -> ScrapeResult:
        """
        Send prompt(s) to ChatGPT (async).
        
        Args:
            prompt: Prompt(s) to send to ChatGPT (required)
            country: Country code(s) in 2-letter format (optional)
            secondaryPrompt: Secondary prompt(s) for continued conversation (optional)
            webSearch: Enable web search capability (optional)
            sync: Synchronous mode - True for immediate, False for polling (default: True)
            timeout: Timeout in seconds (default: 65 for sync, 30 for async)
        
        Returns:
            ScrapeResult with ChatGPT response(s)
        
        Example:
            >>> result = await search.chatGPT_async(
            ...     prompt="What is Python?",
            ...     country="us",
            ...     webSearch=True,
            ...     sync=True
            ... )
            >>> 
            >>> # Batch prompts
            >>> result = await search.chatGPT_async(
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
                    f"Country code must be 2-letter format, got: {c}. "
                    f"Examples: US, GB, FR, DE"
                )
        
        # Build payload
        payload = []
        for i in range(batch_size):
            item: Dict[str, Any] = {
                "prompt": prompts[i],
                "country": countries[i].upper() if countries[i] else "US",
                "web_search": web_searches[i] if isinstance(web_searches[i], bool) else False,
            }
            
            if secondary_prompts[i]:
                item["additional_prompt"] = secondary_prompts[i]
            
            payload.append(item)
        
        # Adjust timeout based on sync mode
        actual_timeout = timeout if sync else (timeout if timeout != 65 else 30)
        
        # Execute with appropriate mode
        async with self.engine:
            if sync:
                result = await self._execute_sync_mode(
                    payload=payload,
                    timeout=actual_timeout
                )
            else:
                result = await self._execute_async_mode(
                    payload=payload,
                    timeout=actual_timeout
                )
            
            return result
    
    def chatGPT(
        self,
        prompt: Union[str, List[str]],
        country: Optional[Union[str, List[str]]] = None,
        secondaryPrompt: Optional[Union[str, List[str]]] = None,
        webSearch: Optional[Union[bool, List[bool]]] = None,
        sync: bool = True,
        timeout: int = 65,
    ) -> ScrapeResult:
        """
        Send prompt(s) to ChatGPT (sync).
        
        See chatGPT_async() for full documentation.
        
        Example:
            >>> result = search.chatGPT(
            ...     prompt="Explain async programming",
            ...     webSearch=True
            ... )
        """
        return asyncio.run(self.chatGPT_async(
            prompt=prompt,
            country=country,
            secondaryPrompt=secondaryPrompt,
            webSearch=webSearch,
            sync=sync,
            timeout=timeout
        ))
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _normalize_param(
        self,
        param: Optional[Union[Any, List[Any]]],
        target_length: int,
        default_value: Any = None
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
    
    async def _execute_sync_mode(
        self,
        payload: List[Dict[str, Any]],
        timeout: int,
    ) -> ScrapeResult:
        """Execute using sync mode (/scrape endpoint - immediate)."""
        request_sent_at = datetime.now(timezone.utc)
        
        params = {"dataset_id": self.DATASET_ID}
        
        async with self.engine._session.post(
            self.SCRAPE_URL,
            json=payload,
            params=params,
            headers=self.engine._session.headers,
            timeout=timeout
        ) as response:
            data_received_at = datetime.now(timezone.utc)
            
            if response.status == 200:
                data = await response.json()
                row_count = len(data) if isinstance(data, list) else None
                cost = (row_count * 0.005) if row_count else None  # ChatGPT cost
                
                return ScrapeResult(
                    success=True,
                    url="https://chatgpt.com",  # Fixed URL per spec
                    status="ready",
                    data=data,
                    cost=cost,
                    platform="chatgpt",
                    request_sent_at=request_sent_at,
                    data_received_at=data_received_at,
                    row_count=row_count,
                )
            else:
                error_text = await response.text()
                return ScrapeResult(
                    success=False,
                    url="https://chatgpt.com",
                    status="error",
                    error=f"ChatGPT search failed (HTTP {response.status}): {error_text}",
                    platform="chatgpt",
                    request_sent_at=request_sent_at,
                    data_received_at=data_received_at,
                )
    
    async def _execute_async_mode(
        self,
        payload: List[Dict[str, Any]],
        timeout: int,
    ) -> ScrapeResult:
        """Execute using async mode (/trigger endpoint - polling)."""
        request_sent_at = datetime.now(timezone.utc)
        
        # Trigger
        params = {
            "dataset_id": self.DATASET_ID,
            "include_errors": "true",
        }
        
        async with self.engine._session.post(
            self.TRIGGER_URL,
            json=payload,
            params=params,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                snapshot_id = data.get("snapshot_id")
            else:
                error_text = await response.text()
                return ScrapeResult(
                    success=False,
                    url="https://chatgpt.com",
                    status="error",
                    error=f"Trigger failed (HTTP {response.status}): {error_text}",
                    platform="chatgpt",
                    request_sent_at=request_sent_at,
                    data_received_at=datetime.now(timezone.utc),
                )
        
        if not snapshot_id:
            return ScrapeResult(
                success=False,
                url="https://chatgpt.com",
                status="error",
                error="No snapshot_id returned",
                platform="chatgpt",
                request_sent_at=request_sent_at,
                data_received_at=datetime.now(timezone.utc),
            )
        
        snapshot_id_received_at = datetime.now(timezone.utc)
        
        # Use shared polling utility
        from ...utils.polling import poll_until_ready
        
        result = await poll_until_ready(
            get_status_func=self._get_status_async,
            fetch_result_func=self._fetch_result_async,
            snapshot_id=snapshot_id,
            poll_interval=10,
            poll_timeout=timeout,
            request_sent_at=request_sent_at,
            snapshot_id_received_at=snapshot_id_received_at,
            platform="chatgpt",
            cost_per_record=0.005,
        )
        
        # Set fixed URL per spec
        result.url = "https://chatgpt.com"
        return result
    
    async def _get_status_async(self, snapshot_id: str) -> str:
        """Get snapshot status."""
        url = f"{self.STATUS_URL}/{snapshot_id}"
        
        async with self.engine._session.get(
            url,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("status", "unknown")
            return "error"
    
    async def _fetch_result_async(self, snapshot_id: str) -> Any:
        """Fetch snapshot results."""
        url = f"{self.RESULT_URL}/{snapshot_id}"
        params = {"format": "json"}
        
        async with self.engine._session.get(
            url,
            params=params,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise APIError(
                    f"Failed to fetch results (HTTP {response.status}): {error_text}",
                    status_code=response.status
                )

