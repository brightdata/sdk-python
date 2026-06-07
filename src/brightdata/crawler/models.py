"""Result and job models for the Crawl API."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CrawlResult:
    """
    Result object for Crawl API operations.

    The Bright Data Crawl API returns one record per URL, with every output
    format (markdown, html2text, page_html, ...) bundled in the same record.
    `data` is the list of those records.
    """

    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    page_count: int = 0
    snapshot_id: Optional[str] = None  # None on sync path, set on async path
    trigger_sent_at: Optional[datetime] = None
    data_fetched_at: Optional[datetime] = None
    error: Optional[str] = None

    def __repr__(self) -> str:
        sid = f" snapshot_id={self.snapshot_id}" if self.snapshot_id else ""
        if self.success:
            return f"<CrawlResult success pages={self.page_count}{sid}>"
        return f"<CrawlResult failed error={self.error!r}{sid}>"


@dataclass
class CrawlJob:
    """
    Handle for an async crawl in flight.

    Returned by `CrawlerService.trigger()`. Pass `snapshot_id` to `status()`
    and `download()` to drive the lifecycle manually.
    """

    snapshot_id: str
    trigger_sent_at: datetime

    def __repr__(self) -> str:
        return f"<CrawlJob snapshot_id={self.snapshot_id}>"
