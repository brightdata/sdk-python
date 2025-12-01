"""Unit tests for result models."""

from datetime import datetime, timezone
from brightdata.models import (
    BaseResult,
    ScrapeResult,
    SearchResult,
    CrawlResult,
)


class TestBaseResult:
    """Tests for BaseResult class."""

    def test_creation(self):
        """Test basic creation of BaseResult."""
        result = BaseResult(success=True)
        assert result.success is True
        assert result.cost is None
        assert result.error is None

    def test_elapsed_ms(self):
        """Test elapsed time calculation."""
        now = datetime.now(timezone.utc)
        result = BaseResult(
            success=True,
            trigger_sent_at=now,
            data_fetched_at=now,
        )
        elapsed = result.elapsed_ms()
        assert elapsed is not None
        assert elapsed >= 0

    def test_elapsed_ms_with_delta(self):
        """Test elapsed time with actual time difference."""
        start = datetime(2025, 1, 1, 12, 0, 0)
        end = datetime(2025, 1, 1, 12, 0, 1)
        result = BaseResult(
            success=True,
            trigger_sent_at=start,
            data_fetched_at=end,
        )
        assert result.elapsed_ms() == 1000.0

    def test_get_timing_breakdown(self):
        """Test timing breakdown generation."""
        now = datetime.now(timezone.utc)
        result = BaseResult(
            success=True,
            trigger_sent_at=now,
            data_fetched_at=now,
        )
        breakdown = result.get_timing_breakdown()
        assert "total_elapsed_ms" in breakdown
        assert "trigger_sent_at" in breakdown
        assert "data_fetched_at" in breakdown

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = BaseResult(success=True, cost=0.001)
        data = result.to_dict()
        assert data["success"] is True
        assert data["cost"] == 0.001

    def test_to_json(self):
        """Test JSON serialization."""
        result = BaseResult(success=True, cost=0.001)
        json_str = result.to_json()
        assert isinstance(json_str, str)
        assert "success" in json_str
        assert "0.001" in json_str

    def test_save_to_file(self, tmp_path):
        """Test saving to file."""
        result = BaseResult(success=True, cost=0.001)
        filepath = tmp_path / "result.json"
        result.save_to_file(filepath)

        assert filepath.exists()
        content = filepath.read_text()
        assert "success" in content
        assert "0.001" in content


class TestScrapeResult:
    """Tests for ScrapeResult class."""

    def test_creation(self):
        """Test basic creation of ScrapeResult."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
        )
        assert result.success is True
        assert result.url == "https://example.com"
        assert result.status == "ready"

    def test_with_platform(self):
        """Test ScrapeResult with platform."""
        result = ScrapeResult(
            success=True,
            url="https://www.linkedin.com/in/test",
            status="ready",
            platform="linkedin",
        )
        assert result.platform == "linkedin"

    def test_timing_breakdown_with_polling(self):
        """Test timing breakdown includes polling information."""
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


class TestSearchResult:
    """Tests for SearchResult class."""

    def test_creation(self):
        """Test basic creation of SearchResult."""
        query = {"q": "python", "engine": "google"}
        result = SearchResult(
            success=True,
            query=query,
        )
        assert result.success is True
        assert result.query == query
        assert result.total_found is None

    def test_with_total_found(self):
        """Test SearchResult with total results."""
        result = SearchResult(
            success=True,
            query={"q": "python"},
            total_found=1000,
            search_engine="google",
        )
        assert result.total_found == 1000
        assert result.search_engine == "google"


class TestCrawlResult:
    """Tests for CrawlResult class."""

    def test_creation(self):
        """Test basic creation of CrawlResult."""
        result = CrawlResult(
            success=True,
            domain="example.com",
        )
        assert result.success is True
        assert result.domain == "example.com"
        assert result.pages == []

    def test_with_pages(self):
        """Test CrawlResult with crawled pages."""
        pages = [
            {"url": "https://example.com/page1", "data": {}},
            {"url": "https://example.com/page2", "data": {}},
        ]
        result = CrawlResult(
            success=True,
            domain="example.com",
            pages=pages,
            total_pages=2,
        )
        assert len(result.pages) == 2
        assert result.total_pages == 2

    def test_timing_breakdown_with_crawl_duration(self):
        """Test timing breakdown includes crawl duration."""
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


class TestInterfaceRequirements:
    """Test all interface requirements are met."""

    def test_common_fields(self):
        """Test common fields across all results."""
        result = BaseResult(success=True, cost=0.001, error=None)
        assert hasattr(result, "success")
        assert hasattr(result, "cost")
        assert hasattr(result, "error")
        assert hasattr(result, "trigger_sent_at")
        assert hasattr(result, "data_fetched_at")

    def test_common_methods(self):
        """Test common methods across all results."""
        result = BaseResult(success=True)
        assert hasattr(result, "elapsed_ms")
        assert hasattr(result, "to_json")
        assert hasattr(result, "save_to_file")
        assert hasattr(result, "get_timing_breakdown")

    def test_scrape_specific_fields(self):
        """Test ScrapeResult specific fields."""
        scrape = ScrapeResult(success=True, url="https://example.com", status="ready")
        assert hasattr(scrape, "url")
        assert hasattr(scrape, "platform")
        assert hasattr(scrape, "method")

    def test_search_specific_fields(self):
        """Test SearchResult specific fields."""
        search = SearchResult(success=True, query={"q": "test"})
        assert hasattr(search, "query")
        assert hasattr(search, "total_found")

    def test_crawl_specific_fields(self):
        """Test CrawlResult specific fields."""
        crawl = CrawlResult(success=True, domain="example.com")
        assert hasattr(crawl, "domain")
        assert hasattr(crawl, "pages")


class TestMethodFieldTracking:
    """Tests for method field tracking in results."""

    def test_scrape_result_accepts_method_parameter(self):
        """Test ScrapeResult accepts method parameter."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="web_scraper",
        )
        assert result.method == "web_scraper"

    def test_scrape_result_method_can_be_web_unlocker(self):
        """Test ScrapeResult method can be 'web_unlocker'."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="web_unlocker",
        )
        assert result.method == "web_unlocker"

    def test_scrape_result_method_can_be_browser_api(self):
        """Test ScrapeResult method can be 'browser_api'."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="browser_api",
        )
        assert result.method == "browser_api"

    def test_scrape_result_method_defaults_to_none(self):
        """Test ScrapeResult method defaults to None."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
        )
        assert result.method is None

    def test_method_included_in_to_dict(self):
        """Test method field is included in to_dict output."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="web_scraper",
        )
        data = result.to_dict()
        assert "method" in data
        assert data["method"] == "web_scraper"

    def test_method_included_in_json(self):
        """Test method field is included in JSON output."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="web_unlocker",
        )
        json_str = result.to_json()
        assert "method" in json_str
        assert "web_unlocker" in json_str

    def test_method_persists_through_serialization(self):
        """Test method field persists through serialization."""
        import json

        result = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="browser_api",
        )

        # Serialize to dict and back
        data = result.to_dict()
        assert data["method"] == "browser_api"

        # Serialize to JSON and parse
        json_str = result.to_json()
        parsed = json.loads(json_str)
        assert parsed["method"] == "browser_api"


class TestMethodFieldIntegration:
    """Test method field integration with scrapers."""

    def test_method_field_tracks_scraping_approach(self):
        """Test method field effectively tracks scraping approach."""
        # Test all three methods
        methods = ["web_scraper", "web_unlocker", "browser_api"]

        for method in methods:
            result = ScrapeResult(
                success=True,
                url="https://example.com",
                status="ready",
                method=method,
            )
            assert result.method == method
            assert result.method in ["web_scraper", "web_unlocker", "browser_api"]

    def test_method_field_helps_identify_data_source(self):
        """Test method field helps identify data source."""
        # Different methods might have different characteristics
        web_scraper = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="web_scraper",
            platform="linkedin",
        )

        web_unlocker = ScrapeResult(
            success=True,
            url="https://example.com",
            status="ready",
            method="web_unlocker",
        )

        # Both valid, but method provides context
        assert web_scraper.method == "web_scraper"
        assert web_unlocker.method == "web_unlocker"
        assert web_scraper.method != web_unlocker.method
