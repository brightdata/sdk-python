"""
Discover API service — AI-powered web search with relevance ranking.

Provides access to Bright Data's Discover API, which performs web searches
with AI-powered relevance ranking based on stated intent.
"""

import asyncio
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from ..core.engine import AsyncEngine
from ..exceptions import APIError
from .models import DiscoverResult, DiscoverJob


class DiscoverService:
    """
    Bright Data Discover API — AI-powered web search with relevance ranking.

    The Discover API differs from SERP scraping: it uses an `intent` parameter
    to separate what you're searching for from why, enabling AI-powered
    relevance ranking and optional full-page content extraction.

    Example:
        >>> async with BrightDataClient() as client:
        ...     result = await client.discover(
        ...         query="artificial intelligence trends 2026",
        ...         intent="latest AI technology developments",
        ...     )
        ...     for item in result.data:
        ...         print(f"[{item['relevance_score']:.2f}] {item['title']}")
    """

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def search(
        self,
        query: str,
        intent: Optional[str] = None,
        include_content: bool = False,
        country: Optional[str] = None,
        city: Optional[str] = None,
        language: Optional[str] = None,
        filter_keywords: Optional[List[str]] = None,
        num_results: Optional[int] = None,
        format: str = "json",
        timeout: int = 60,
        poll_interval: int = 2,
    ) -> DiscoverResult:
        """
        Search the web with AI-powered relevance ranking.

        Triggers a search, polls until complete, and returns results.

        Args:
            query: Search query string.
            intent: Why you're searching — guides AI relevance ranking.
            include_content: If True, returns page content as markdown.
            country: Country code for localized results (e.g., "us").
            city: City for localized results (e.g., "new york").
            language: Language code for localized results.
            filter_keywords: Filter results by keywords.
            num_results: Number of results to return.
            format: Response format (default: "json").
            timeout: Max seconds to wait for results (default: 60).
            poll_interval: Seconds between status checks (default: 2).

        Returns:
            DiscoverResult with ranked search results.

        Raises:
            APIError: If the API request fails.
            TimeoutError: If polling exceeds timeout.
        """
        trigger_time = datetime.now(timezone.utc)

        task_id = await self._trigger(
            query=query,
            intent=intent,
            include_content=include_content,
            country=country,
            city=city,
            language=language,
            filter_keywords=filter_keywords,
            num_results=num_results,
            format=format,
        )

        response_data = await self._poll_until_done(task_id, timeout, poll_interval)
        fetch_time = datetime.now(timezone.utc)

        results = response_data.get("results", [])
        duration = response_data.get("duration_seconds")

        return DiscoverResult(
            success=True,
            query=query,
            intent=intent,
            data=results,
            duration_seconds=duration,
            total_results=len(results),
            task_id=task_id,
            trigger_sent_at=trigger_time,
            data_fetched_at=fetch_time,
        )

    async def trigger(
        self,
        query: str,
        intent: Optional[str] = None,
        include_content: bool = False,
        country: Optional[str] = None,
        city: Optional[str] = None,
        language: Optional[str] = None,
        filter_keywords: Optional[List[str]] = None,
        num_results: Optional[int] = None,
        format: str = "json",
    ) -> DiscoverJob:
        """
        Trigger a search and return a job for manual polling.

        Use this when you want to do other work while waiting for results.

        Args:
            query: Search query string.
            intent: Why you're searching — guides AI relevance ranking.
            include_content: If True, returns page content as markdown.
            country: Country code for localized results.
            city: City for localized results.
            language: Language code for localized results.
            filter_keywords: Filter results by keywords.
            num_results: Number of results to return.
            format: Response format (default: "json").

        Returns:
            DiscoverJob for manual polling and fetching.

        Raises:
            APIError: If the trigger request fails.
        """
        task_id = await self._trigger(
            query=query,
            intent=intent,
            include_content=include_content,
            country=country,
            city=city,
            language=language,
            filter_keywords=filter_keywords,
            num_results=num_results,
            format=format,
        )

        return DiscoverJob(
            task_id=task_id,
            _service=self,
            query=query,
            intent=intent,
        )

    async def _trigger(
        self,
        query: str,
        intent: Optional[str] = None,
        include_content: bool = False,
        country: Optional[str] = None,
        city: Optional[str] = None,
        language: Optional[str] = None,
        filter_keywords: Optional[List[str]] = None,
        num_results: Optional[int] = None,
        format: str = "json",
    ) -> str:
        """POST /discover, return task_id."""
        payload: Dict[str, Any] = {"query": query}

        if intent:
            payload["intent"] = intent
        if include_content:
            payload["include_content"] = True
        if country:
            payload["country"] = country
        if city:
            payload["city"] = city
        if language:
            payload["language"] = language
        if filter_keywords:
            payload["filter_keywords"] = filter_keywords
        if num_results is not None:
            payload["num_results"] = num_results
        if format:
            payload["format"] = format

        async with self._engine.post("/discover", json_data=payload) as response:
            if response.status >= 400:
                text = await response.text()
                raise APIError(
                    f"Discover trigger failed (HTTP {response.status}): {text}",
                    status_code=response.status,
                )

            data = await response.json()
            task_id = data.get("task_id")
            if not task_id:
                raise APIError("No task_id in discover response")
            return task_id

    async def _poll_once(self, task_id: str) -> Dict[str, Any]:
        """GET /discover?task_id=<task_id>, return response data."""
        async with self._engine.get("/discover", params={"task_id": task_id}) as response:
            if response.status >= 400:
                text = await response.text()
                raise APIError(
                    f"Discover poll failed (HTTP {response.status}): {text}",
                    status_code=response.status,
                )
            return await response.json()

    async def _poll_until_done(
        self, task_id: str, timeout: int, poll_interval: int
    ) -> Dict[str, Any]:
        """Poll GET /discover?task_id=<task_id> until done or timeout."""
        start = time.time()

        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(f"Discover task {task_id} timed out after {timeout}s")

            response_data = await self._poll_once(task_id)
            status = response_data.get("status", "processing")

            if status == "done":
                return response_data
            elif status in ("error", "failed"):
                error_msg = response_data.get("error", "Unknown error")
                raise APIError(f"Discover task failed: {error_msg}")

            await asyncio.sleep(poll_interval)
