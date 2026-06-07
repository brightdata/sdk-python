"""
Crawler service — Bright Data Crawl API.

Two endpoints back the same `dataset_id=gd_m6gjtfmeh43we6cqc`:

* `POST /datasets/v3/scrape?notify=false` — returns the result inline in a
  single round-trip. Used by `crawl()`. Good for small / quick crawls.
* `POST /datasets/v3/trigger?notify=false` — returns `{"snapshot_id": ...}`;
  poll `/datasets/v3/progress/<id>` until ready, then GET
  `/datasets/v3/snapshot/<id>?format=json`. Used by `trigger()` /
  `status()` / `download()`. Good for large / long-running crawls.

Both endpoints take the same body shape: `{"input": [{"url": "..."}, ...]}`.

All methods are async-only. For sync usage, use SyncBrightDataClient.
"""

import asyncio
import json
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from .models import CrawlJob, CrawlResult
from ..exceptions import APIError, ValidationError
from ..utils.function_detection import get_caller_function_name
from ..utils.validation import validate_url, validate_url_list

if TYPE_CHECKING:
    from ..client import BrightDataClient


class CrawlerService:
    """
    Web crawler service namespace — Bright Data Crawl API.

    Example:
        >>> async with BrightDataClient() as client:
        ...     # Sync path — one call, blocks until done
        ...     result = await client.crawler.crawl(urls="https://example.com")
        ...     print(result.data[0]["markdown"])
        ...
        ...     # Async path — trigger and poll separately
        ...     job = await client.crawler.trigger(urls=["https://example.com"])
        ...     status = await client.crawler.status(job.snapshot_id)
        ...     result = await client.crawler.download(job.snapshot_id)
    """

    DATASET_ID = "gd_m6gjtfmeh43we6cqc"

    ENDPOINT_SCRAPE = "/datasets/v3/scrape"
    ENDPOINT_TRIGGER = "/datasets/v3/trigger"
    ENDPOINT_PROGRESS = "/datasets/v3/progress"
    ENDPOINT_SNAPSHOT = "/datasets/v3/snapshot"

    DEFAULT_POLL_INTERVAL = 5
    DEFAULT_POLL_TIMEOUT = 600

    TERMINAL_STATUSES = {"ready", "failed", "error"}

    def __init__(self, client: "BrightDataClient"):
        """Initialize crawler service with client reference."""
        self._client = client

    # ------------------------------------------------------------------
    # Sync path — POST /scrape
    # ------------------------------------------------------------------

    async def crawl(
        self,
        urls: Union[str, List[str]],
        include_errors: bool = True,
    ) -> CrawlResult:
        """
        Crawl one or more URLs synchronously.

        Issues a single `POST /datasets/v3/scrape` and returns the inline
        result. The API returns one record per URL with every output format
        bundled (`url`, `markdown`, `html2text`, `page_html`, ...).

        Args:
            urls: One URL or a list of URLs.
            include_errors: If True, the API includes per-URL error
                records alongside successful ones (default: True).

        Returns:
            CrawlResult. `result.data` is a List[Dict], one entry per URL.

        Raises:
            ValidationError: If URLs are invalid.

        Note:
            Other failures (HTTP errors, network errors) are returned in
            `result.error` with `success=False` — not raised.
        """
        url_list = self._normalize_urls(urls)
        return await self._scrape_sync(
            urls=url_list,
            include_errors=include_errors,
            sdk_function=get_caller_function_name(),
        )

    # ------------------------------------------------------------------
    # Async path — POST /trigger, GET /progress, GET /snapshot
    # ------------------------------------------------------------------

    async def trigger(
        self,
        urls: Union[str, List[str]],
        include_errors: bool = True,
    ) -> CrawlJob:
        """
        Start an async crawl and return a job handle.

        Issues a single `POST /datasets/v3/trigger` and returns the
        `snapshot_id` wrapped in a `CrawlJob`. Use `status()` to poll and
        `download()` to fetch results.

        Raises:
            ValidationError: If URLs are invalid.
            APIError: If the API rejects the trigger.
        """
        url_list = self._normalize_urls(urls)
        trigger_sent_at = datetime.now(timezone.utc)
        sdk_function = get_caller_function_name()

        params = {
            "dataset_id": self.DATASET_ID,
            "notify": "false",
            "include_errors": "true" if include_errors else "false",
        }
        if sdk_function:
            params["sdk_function"] = sdk_function

        body = {"input": [{"url": url} for url in url_list]}

        async with self._client.engine.post_to_url(
            self._url(self.ENDPOINT_TRIGGER),
            json_data=body,
            params=params,
        ) as response:
            if response.status != HTTPStatus.OK:
                error_text = await response.text()
                raise APIError(
                    f"Trigger failed (HTTP {response.status}): {error_text}",
                    status_code=response.status,
                )
            data = await response.json()
            snapshot_id = data.get("snapshot_id")
            if not snapshot_id:
                raise APIError(
                    f"Trigger response missing snapshot_id: {data}",
                    status_code=response.status,
                )

        return CrawlJob(snapshot_id=snapshot_id, trigger_sent_at=trigger_sent_at)

    async def status(self, snapshot_id: str) -> str:
        """
        Get the status of an async crawl.

        Issues `GET /datasets/v3/progress/<snapshot_id>`.

        Returns:
            Status string. Common values: `"running"`, `"ready"`, `"failed"`.

        Raises:
            ValidationError: If `snapshot_id` is empty.
            APIError: If the API call fails.
        """
        self._validate_snapshot_id(snapshot_id)

        async with self._client.engine.get_from_url(
            f"{self._url(self.ENDPOINT_PROGRESS)}/{snapshot_id}",
        ) as response:
            if response.status != HTTPStatus.OK:
                error_text = await response.text()
                raise APIError(
                    f"Status check failed (HTTP {response.status}): {error_text}",
                    status_code=response.status,
                )
            data = await response.json()
            return str(data.get("status", "unknown"))

    async def download(
        self,
        snapshot_id: str,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        poll_timeout: int = DEFAULT_POLL_TIMEOUT,
    ) -> CrawlResult:
        """
        Wait for an async crawl to finish, then fetch the result.

        Polls `GET /datasets/v3/progress/<snapshot_id>` until status is
        terminal (`ready` / `failed` / `error`) or `poll_timeout` is hit.
        On `ready`, fetches `GET /datasets/v3/snapshot/<snapshot_id>?format=json`.

        Args:
            snapshot_id: Snapshot ID returned by `trigger()`.
            poll_interval: Seconds between status checks (default: 5).
            poll_timeout: Max seconds to wait before giving up (default: 600).

        Returns:
            CrawlResult. Errors (failed snapshot, timeout, HTTP error on
            fetch) are returned with `success=False` — not raised. Validation
            errors on `snapshot_id` raise immediately.

        Raises:
            ValidationError: If `snapshot_id` is empty.
        """
        self._validate_snapshot_id(snapshot_id)
        trigger_sent_at = datetime.now(timezone.utc)
        deadline = asyncio.get_event_loop().time() + poll_timeout

        while True:
            try:
                current = await self.status(snapshot_id)
            except APIError as exc:
                return CrawlResult(
                    success=False,
                    snapshot_id=snapshot_id,
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=datetime.now(timezone.utc),
                    error=f"Status check failed: {exc}",
                )

            if current == "ready":
                return await self._fetch_snapshot(snapshot_id, trigger_sent_at)

            if current in self.TERMINAL_STATUSES:  # failed / error
                return CrawlResult(
                    success=False,
                    snapshot_id=snapshot_id,
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=datetime.now(timezone.utc),
                    error=f"Snapshot ended with status={current!r}",
                )

            if asyncio.get_event_loop().time() >= deadline:
                return CrawlResult(
                    success=False,
                    snapshot_id=snapshot_id,
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=datetime.now(timezone.utc),
                    error=(
                        f"Polling timeout after {poll_timeout}s "
                        f"(last status={current!r}, snapshot_id={snapshot_id})"
                    ),
                )

            await asyncio.sleep(poll_interval)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _scrape_sync(
        self,
        urls: List[str],
        include_errors: bool,
        sdk_function: Optional[str],
    ) -> CrawlResult:
        """POST /scrape and return the inline result wrapped in CrawlResult."""
        trigger_sent_at = datetime.now(timezone.utc)

        params = {
            "dataset_id": self.DATASET_ID,
            "notify": "false",
            "include_errors": "true" if include_errors else "false",
        }
        if sdk_function:
            params["sdk_function"] = sdk_function

        body = {"input": [{"url": url} for url in urls]}

        try:
            async with self._client.engine.post_to_url(
                self._url(self.ENDPOINT_SCRAPE),
                json_data=body,
                params=params,
            ) as response:
                data_fetched_at = datetime.now(timezone.utc)

                if response.status != HTTPStatus.OK:
                    error_text = await response.text()
                    return CrawlResult(
                        success=False,
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                        error=f"HTTP {response.status}: {error_text}",
                    )

                records = self._parse_records(await response.text())
                return CrawlResult(
                    success=True,
                    data=records,
                    page_count=len(records),
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=data_fetched_at,
                )
        except (ValidationError, APIError):
            raise
        except Exception as exc:
            return CrawlResult(
                success=False,
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=datetime.now(timezone.utc),
                error=f"Unexpected error: {exc}",
            )

    async def _fetch_snapshot(
        self,
        snapshot_id: str,
        trigger_sent_at: datetime,
    ) -> CrawlResult:
        """GET /snapshot/<id>?format=json and wrap the records in CrawlResult."""
        try:
            async with self._client.engine.get_from_url(
                f"{self._url(self.ENDPOINT_SNAPSHOT)}/{snapshot_id}",
                params={"format": "json"},
            ) as response:
                data_fetched_at = datetime.now(timezone.utc)

                if response.status != HTTPStatus.OK:
                    error_text = await response.text()
                    return CrawlResult(
                        success=False,
                        snapshot_id=snapshot_id,
                        trigger_sent_at=trigger_sent_at,
                        data_fetched_at=data_fetched_at,
                        error=f"Snapshot fetch failed (HTTP {response.status}): {error_text}",
                    )

                records = self._parse_records(await response.text())
                return CrawlResult(
                    success=True,
                    data=records,
                    page_count=len(records),
                    snapshot_id=snapshot_id,
                    trigger_sent_at=trigger_sent_at,
                    data_fetched_at=data_fetched_at,
                )
        except Exception as exc:
            return CrawlResult(
                success=False,
                snapshot_id=snapshot_id,
                trigger_sent_at=trigger_sent_at,
                data_fetched_at=datetime.now(timezone.utc),
                error=f"Snapshot fetch error: {exc}",
            )

    @staticmethod
    def _parse_records(text: str) -> List[Dict[str, Any]]:
        """
        Parse the response body into a list of crawl records.

        `/scrape` returns either a single object (one URL in) or a JSON array
        (multi-URL or via /snapshot). It can also come back as NDJSON in some
        snapshot formats. Be permissive about all three.
        """
        text = text.strip()
        if not text:
            return []

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            records: List[Dict[str, Any]] = []
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    records.append(obj)
                elif isinstance(obj, list):
                    records.extend(item for item in obj if isinstance(item, dict))
            return records

        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            return [parsed]
        return []

    @staticmethod
    def _normalize_urls(urls: Union[str, List[str]]) -> List[str]:
        """Validate and normalize input to a non-empty list of URLs."""
        if isinstance(urls, str):
            validate_url(urls)
            return [urls]
        if isinstance(urls, list):
            if not urls:
                raise ValidationError("urls list cannot be empty")
            validate_url_list(urls)
            return urls
        raise ValidationError(
            f"urls must be a string or list of strings, got {type(urls).__name__}"
        )

    @staticmethod
    def _validate_snapshot_id(snapshot_id: str) -> None:
        if not isinstance(snapshot_id, str) or not snapshot_id.strip():
            raise ValidationError("snapshot_id must be a non-empty string")

    def _url(self, path: str) -> str:
        return f"{self._client.engine.BASE_URL}{path}"
