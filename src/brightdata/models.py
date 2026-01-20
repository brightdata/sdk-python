"""Unified result models for all Bright Data SDK operations."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional, List, Dict, Union, Literal
import json
from pathlib import Path


StatusType = Literal["ready", "error", "timeout", "in_progress"]
PlatformType = Optional[Literal["linkedin", "amazon", "chatgpt", "instagram", "facebook"]]
SearchEngineType = Optional[Literal["google", "bing", "yandex"]]


@dataclass
class BaseResult:
    """
    Base result class with common fields for all SDK operations.

    Provides consistent interface for success status, cost tracking, timing,
    and error handling across all SDK operations.

    Attributes:
        success: Whether the operation completed successfully.
        cost: Cost in USD for this operation. Must be non-negative if provided.
        error: Error message if operation failed, None otherwise.
        trigger_sent_at: Timestamp when the trigger request was sent to Bright Data (UTC-aware).
        data_fetched_at: Timestamp when data was fetched after polling completed (UTC-aware).
    """

    success: bool
    cost: Optional[float] = None
    error: Optional[str] = None
    trigger_sent_at: Optional[datetime] = None
    data_fetched_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate data after initialization."""
        if self.cost is not None and self.cost < 0:
            raise ValueError(f"Cost must be non-negative, got {self.cost}")

    def elapsed_ms(self) -> Optional[float]:
        """
        Calculate total elapsed time in milliseconds.

        Returns:
            Elapsed time in milliseconds, or None if timing data unavailable.
        """
        if self.trigger_sent_at and self.data_fetched_at:
            delta = self.data_fetched_at - self.trigger_sent_at
            return delta.total_seconds() * 1000
        return None

    def get_timing_breakdown(self) -> Dict[str, Optional[Union[float, str]]]:
        """
        Get detailed timing breakdown for debugging and optimization.

        Returns:
            Dictionary with timing information including:
            - total_elapsed_ms: Total elapsed time in milliseconds
            - trigger_sent_at: ISO format timestamp when trigger was sent
            - data_fetched_at: ISO format timestamp when data was fetched
        """
        return {
            "total_elapsed_ms": self.elapsed_ms(),
            "trigger_sent_at": self.trigger_sent_at.isoformat() if self.trigger_sent_at else None,
            "data_fetched_at": self.data_fetched_at.isoformat() if self.data_fetched_at else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for serialization.

        Converts datetime objects to ISO format strings for JSON compatibility.

        Returns:
            Dictionary representation of the result with serialized datetimes.
        """
        result = asdict(self)
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, list) and value and isinstance(value[0], datetime):
                result[key] = [v.isoformat() if isinstance(v, datetime) else v for v in value]
        return result

    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Serialize result to JSON string.

        Args:
            indent: Optional indentation level for pretty printing (2 or 4 recommended).

        Returns:
            JSON string representation of the result.

        Raises:
            TypeError: If result contains non-serializable data.
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def save_to_file(self, filepath: Union[str, Path], format: str = "json") -> None:
        """
        Save result data to file.

        Args:
            filepath: Path where to save the file. Must be a valid file path.
            format: File format. Currently only "json" is supported.

        Raises:
            ValueError: If format is not supported.
            OSError: If file cannot be written (permissions, disk full, etc.).
            IOError: If file I/O operation fails.
        """
        path = Path(filepath).resolve()

        if not path.parent.exists():
            raise OSError(f"Parent directory does not exist: {path.parent}")

        if format.lower() == "json":
            try:
                path.write_text(self.to_json(indent=2), encoding="utf-8")
            except OSError as e:
                raise OSError(f"Failed to write file {path}: {e}") from e
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json'.")

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "success" if self.success else "error"
        cost_str = f"${self.cost:.4f}" if self.cost else "N/A"
        elapsed = f"{self.elapsed_ms():.2f}ms" if self.elapsed_ms() else "N/A"
        return f"<{self.__class__.__name__} {status} cost={cost_str} elapsed={elapsed}>"


@dataclass
class ScrapeResult(BaseResult):
    """
    Result object for web scraping operations.

    Preserves original URL and provides platform-specific information
    for debugging and analytics.

    Attributes:
        url: Original URL that was scraped.
        status: Operation status: "ready", "error", "timeout", or "in_progress".
        data: Scraped data (dict, list, or raw content).
        snapshot_id: Bright Data snapshot ID for this scrape.
        platform: Platform detected: "linkedin", "amazon", "chatgpt", or None.
        method: Method used to obtain data: "web_scraper", "web_unlocker", "browser_api", or None.
        root_domain: Root domain extracted from URL.
        snapshot_id_received_at: Timestamp when snapshot ID was received.
        snapshot_polled_at: List of timestamps when snapshot status was polled.
        html_char_size: Size of HTML content in characters.
        row_count: Number of data rows extracted.
        field_count: Number of fields extracted.
    """

    url: str = ""
    status: StatusType = "ready"
    data: Optional[Any] = None
    snapshot_id: Optional[str] = None
    platform: PlatformType = None
    method: Optional[str] = None
    root_domain: Optional[str] = None
    snapshot_id_received_at: Optional[datetime] = None
    snapshot_polled_at: List[datetime] = field(default_factory=list)
    html_char_size: Optional[int] = None
    row_count: Optional[int] = None
    field_count: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate ScrapeResult-specific fields."""
        super().__post_init__()
        if self.status not in ("ready", "error", "timeout", "in_progress"):
            raise ValueError(
                f"Invalid status: {self.status}. Must be one of: ready, error, timeout, in_progress"
            )
        if self.html_char_size is not None and self.html_char_size < 0:
            raise ValueError(f"html_char_size must be non-negative, got {self.html_char_size}")
        if self.row_count is not None and self.row_count < 0:
            raise ValueError(f"row_count must be non-negative, got {self.row_count}")
        if self.field_count is not None and self.field_count < 0:
            raise ValueError(f"field_count must be non-negative, got {self.field_count}")

    def get_timing_breakdown(self) -> Dict[str, Optional[Union[float, str, int]]]:
        """
        Get detailed timing breakdown including polling information.

        Returns:
            Dictionary with timing information including:
            - All fields from BaseResult.get_timing_breakdown()
            - trigger_time_ms: Time from request to snapshot ID received
            - polling_time_ms: Time spent polling for results
            - poll_count: Number of polling attempts
            - snapshot_id_received_at: ISO format timestamp
        """
        base_breakdown = super().get_timing_breakdown()

        if self.snapshot_id_received_at and self.trigger_sent_at:
            trigger_time = (
                self.snapshot_id_received_at - self.trigger_sent_at
            ).total_seconds() * 1000
            base_breakdown["trigger_time_ms"] = trigger_time

        if self.data_fetched_at and self.snapshot_id_received_at:
            polling_time = (
                self.data_fetched_at - self.snapshot_id_received_at
            ).total_seconds() * 1000
            base_breakdown["polling_time_ms"] = polling_time

        base_breakdown["poll_count"] = len(self.snapshot_polled_at)
        base_breakdown["snapshot_id_received_at"] = (
            self.snapshot_id_received_at.isoformat() if self.snapshot_id_received_at else None
        )

        return base_breakdown

    def __repr__(self) -> str:
        """String representation with URL and platform."""
        base_repr = super().__repr__()
        url_preview = self.url[:50] + "..." if len(self.url) > 50 else self.url
        platform_str = f" platform={self.platform}" if self.platform else ""
        return f"<ScrapeResult {base_repr} url={url_preview}{platform_str}>"


@dataclass
class SearchResult(BaseResult):
    """
    Result object for search engine operations (SERP API).

    Preserves original query parameters and provides search-specific
    metadata for result analysis.

    Attributes:
        query: Original search query parameters as dictionary.
        data: Search results as list of result items.
        total_found: Total number of results found.
        search_engine: Search engine used: "google", "bing", "yandex", or None.
        country: Country code for search location (ISO 3166-1 alpha-2).
        page: Page number of results (1-indexed).
        results_per_page: Number of results per page.
    """

    query: Dict[str, Any] = field(default_factory=dict)
    data: Optional[List[Dict[str, Any]]] = None
    total_found: Optional[int] = None
    search_engine: SearchEngineType = None
    country: Optional[str] = None
    page: Optional[int] = None
    results_per_page: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate SearchResult-specific fields."""
        super().__post_init__()
        if self.total_found is not None and self.total_found < 0:
            raise ValueError(f"total_found must be non-negative, got {self.total_found}")
        if self.page is not None and self.page < 1:
            raise ValueError(f"page must be >= 1, got {self.page}")
        if self.results_per_page is not None and self.results_per_page < 1:
            raise ValueError(f"results_per_page must be >= 1, got {self.results_per_page}")

    def __repr__(self) -> str:
        """String representation with query info."""
        base_repr = super().__repr__()
        query_str = str(self.query)[:50] + "..." if len(str(self.query)) > 50 else str(self.query)
        total_str = f" total={self.total_found:,}" if self.total_found else ""
        return f"<SearchResult {base_repr} query={query_str}{total_str}>"


@dataclass
class CrawlResult(BaseResult):
    """
    Result object for web crawling operations.

    Provides information about crawled pages and domain structure
    for comprehensive web crawling analysis.

    Attributes:
        domain: Root domain that was crawled.
        pages: List of crawled pages with their data.
        total_pages: Total number of pages crawled.
        depth: Maximum crawl depth reached.
        start_url: Starting URL for the crawl.
        filter_pattern: URL filter pattern used.
        exclude_pattern: URL exclude pattern used.
        crawl_started_at: Timestamp when crawl started.
        crawl_completed_at: Timestamp when crawl completed.
    """

    domain: Optional[str] = None
    pages: List[Dict[str, Any]] = field(default_factory=list)
    total_pages: Optional[int] = None
    depth: Optional[int] = None
    start_url: Optional[str] = None
    filter_pattern: Optional[str] = None
    exclude_pattern: Optional[str] = None
    crawl_started_at: Optional[datetime] = None
    crawl_completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate CrawlResult-specific fields."""
        super().__post_init__()
        if self.total_pages is not None and self.total_pages < 0:
            raise ValueError(f"total_pages must be non-negative, got {self.total_pages}")
        if self.depth is not None and self.depth < 0:
            raise ValueError(f"depth must be non-negative, got {self.depth}")

    def get_timing_breakdown(self) -> Dict[str, Optional[Union[float, str]]]:
        """
        Get detailed timing breakdown including crawl duration.

        Returns:
            Dictionary with timing information including:
            - All fields from BaseResult.get_timing_breakdown()
            - crawl_duration_ms: Total crawl duration in milliseconds
            - crawl_started_at: ISO format timestamp
            - crawl_completed_at: ISO format timestamp
        """
        base_breakdown = super().get_timing_breakdown()

        if self.crawl_started_at and self.crawl_completed_at:
            crawl_duration = (
                self.crawl_completed_at - self.crawl_started_at
            ).total_seconds() * 1000
            base_breakdown["crawl_duration_ms"] = crawl_duration

        base_breakdown["crawl_started_at"] = (
            self.crawl_started_at.isoformat() if self.crawl_started_at else None
        )
        base_breakdown["crawl_completed_at"] = (
            self.crawl_completed_at.isoformat() if self.crawl_completed_at else None
        )

        return base_breakdown

    def __repr__(self) -> str:
        """String representation with domain and pages info."""
        base_repr = super().__repr__()
        domain_str = f" domain={self.domain}" if self.domain else ""
        pages_str = f" pages={len(self.pages)}" if self.pages else ""
        return f"<CrawlResult {base_repr}{domain_str}{pages_str}>"


Result = Union[BaseResult, ScrapeResult, SearchResult, CrawlResult]
