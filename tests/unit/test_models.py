"""Tests for result models — Creation, timing, serialization, and method tracking."""

import json
from datetime import datetime, timezone


from brightdata.models import (
    BaseResult,
    ScrapeResult,
    SearchResult,
    CrawlResult,
)


# ---------------------------------------------------------------------------
# BaseResult
# ---------------------------------------------------------------------------


class TestBaseResult:
    def test_creation_defaults(self):
        result = BaseResult(success=True)
        assert result.success is True
        assert result.cost is None
        assert result.error is None

    def test_elapsed_ms_zero_delta(self):
        now = datetime.now(timezone.utc)
        result = BaseResult(success=True, trigger_sent_at=now, data_fetched_at=now)
        elapsed = result.elapsed_ms()
        assert elapsed is not None
        assert elapsed >= 0

    def test_elapsed_ms_one_second(self):
        start = datetime(2025, 1, 1, 12, 0, 0)
        end = datetime(2025, 1, 1, 12, 0, 1)
        result = BaseResult(success=True, trigger_sent_at=start, data_fetched_at=end)
        assert result.elapsed_ms() == 1000.0

    def test_timing_breakdown_keys(self):
        now = datetime.now(timezone.utc)
        result = BaseResult(success=True, trigger_sent_at=now, data_fetched_at=now)
        breakdown = result.get_timing_breakdown()
        assert "total_elapsed_ms" in breakdown
        assert "trigger_sent_at" in breakdown
        assert "data_fetched_at" in breakdown

    def test_to_dict(self):
        result = BaseResult(success=True, cost=0.001)
        data = result.to_dict()
        assert data["success"] is True
        assert data["cost"] == 0.001

    def test_to_json(self):
        result = BaseResult(success=True, cost=0.001)
        json_str = result.to_json()
        assert isinstance(json_str, str)
        assert "success" in json_str
        assert "0.001" in json_str

    def test_save_to_file(self, tmp_path):
        result = BaseResult(success=True, cost=0.001)
        filepath = tmp_path / "result.json"
        result.save_to_file(filepath)

        assert filepath.exists()
        content = filepath.read_text()
        assert "success" in content
        assert "0.001" in content


# ---------------------------------------------------------------------------
# ScrapeResult
# ---------------------------------------------------------------------------


class TestScrapeResult:
    def test_creation(self):
        result = ScrapeResult(success=True, url="https://example.com", status="ready")
        assert result.success is True
        assert result.url == "https://example.com"
        assert result.status == "ready"

    def test_with_platform(self):
        result = ScrapeResult(
            success=True,
            url="https://www.linkedin.com/in/test",
            status="ready",
            platform="linkedin",
        )
        assert result.platform == "linkedin"

    def test_timing_breakdown_with_polling(self):
        start = datetime(2025, 1, 1, 12, 0, 0)
        snapshot_received = datetime(2025, 1, 1, 12, 0, 1)
        end = datetime(2025, 1, 1, 12, 0, 5)

        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            trigger_sent_at=start,
            snapshot_id_received_at=snapshot_received,
            data_fetched_at=end,
            snapshot_polled_at=[snapshot_received, end],
        )

        breakdown = result.get_timing_breakdown()
        assert "trigger_time_ms" in breakdown
        assert "polling_time_ms" in breakdown
        assert breakdown["poll_count"] == 2


# ---------------------------------------------------------------------------
# SearchResult
# ---------------------------------------------------------------------------


class TestSearchResult:
    def test_creation(self):
        result = SearchResult(success=True, query={"q": "python", "engine": "google"})
        assert result.success is True
        assert result.query == {"q": "python", "engine": "google"}
        assert result.total_found is None

    def test_with_total_found(self):
        result = SearchResult(
            success=True,
            query={"q": "python"},
            total_found=1000,
            search_engine="google",
        )
        assert result.total_found == 1000
        assert result.search_engine == "google"


# ---------------------------------------------------------------------------
# CrawlResult
# ---------------------------------------------------------------------------


class TestCrawlResult:
    def test_creation(self):
        result = CrawlResult(success=True, domain="example.com")
        assert result.success is True
        assert result.domain == "example.com"
        assert result.pages == []

    def test_with_pages(self):
        pages = [
            {"url": "https://example.com/page1", "data": {}},
            {"url": "https://example.com/page2", "data": {}},
        ]
        result = CrawlResult(success=True, domain="example.com", pages=pages, total_pages=2)
        assert len(result.pages) == 2
        assert result.total_pages == 2

    def test_timing_breakdown_with_crawl_duration(self):
        crawl_start = datetime(2025, 1, 1, 12, 0, 0)
        crawl_end = datetime(2025, 1, 1, 12, 5, 0)

        result = CrawlResult(
            success=True,
            domain="example.com",
            crawl_started_at=crawl_start,
            crawl_completed_at=crawl_end,
        )

        breakdown = result.get_timing_breakdown()
        assert "crawl_duration_ms" in breakdown
        assert breakdown["crawl_duration_ms"] == 300000.0


# ---------------------------------------------------------------------------
# Method field tracking
# ---------------------------------------------------------------------------


class TestMethodFieldTracking:
    def test_accepts_method_parameter(self):
        result = ScrapeResult(
            success=True, url="https://example.com", status="ready", method="web_scraper"
        )
        assert result.method == "web_scraper"

    def test_method_web_unlocker(self):
        result = ScrapeResult(
            success=True, url="https://example.com", status="ready", method="web_unlocker"
        )
        assert result.method == "web_unlocker"

    def test_method_browser_api(self):
        result = ScrapeResult(
            success=True, url="https://example.com", status="ready", method="browser_api"
        )
        assert result.method == "browser_api"

    def test_method_defaults_to_none(self):
        result = ScrapeResult(success=True, url="https://example.com", status="ready")
        assert result.method is None

    def test_method_in_to_dict(self):
        result = ScrapeResult(
            success=True, url="https://example.com", status="ready", method="web_scraper"
        )
        data = result.to_dict()
        assert data["method"] == "web_scraper"

    def test_method_in_json(self):
        result = ScrapeResult(
            success=True, url="https://example.com", status="ready", method="web_unlocker"
        )
        json_str = result.to_json()
        assert "web_unlocker" in json_str

    def test_method_persists_through_serialization(self):
        result = ScrapeResult(
            success=True, url="https://example.com", status="ready", method="browser_api"
        )
        data = result.to_dict()
        assert data["method"] == "browser_api"

        parsed = json.loads(result.to_json())
        assert parsed["method"] == "browser_api"

    def test_all_methods_valid(self):
        for method in ["web_scraper", "web_unlocker", "browser_api"]:
            result = ScrapeResult(
                success=True, url="https://example.com", status="ready", method=method
            )
            assert result.method == method

    def test_method_distinguishes_data_source(self):
        ws = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="web_scraper",
            platform="linkedin",
        )
        wu = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="web_unlocker",
        )
        assert ws.method != wu.method
