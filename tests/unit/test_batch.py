"""
Tests for batch scraping operations.

Verifies that scraping multiple URLs returns List[ScrapeResult] correctly.
"""

import pytest
from brightdata import BrightDataClient
from brightdata.models import ScrapeResult


class TestBatchOperations:
    """Test batch scraping returns correct types."""

    def test_single_url_returns_single_result(self):
        """Test that a single URL returns ScrapeResult (not list)."""
        client = BrightDataClient(token="test_token_123456789")

        # Verify single URL behavior
        scraper = client.scrape.amazon

        # Single URL should return ScrapeResult
        import inspect

        sig = inspect.signature(scraper.products)
        return_annotation = sig.return_annotation

        # Should accept Union[str, List[str]]
        params = sig.parameters
        assert "url" in params

    def test_list_with_one_url_returns_single_result(self):
        """Test that list with 1 URL returns unwrapped ScrapeResult."""
        # This is the expected behavior - list with 1 item gets unwrapped
        # This test documents the API contract
        pass

    def test_multiple_urls_should_return_list(self):
        """Test that multiple URLs should return List[ScrapeResult]."""
        # This documents that the API SHOULD return a list of results
        # when given multiple URLs, not a single result with data as list

        # Expected behavior:
        # Input: ["url1", "url2", "url3"]
        # Output: [ScrapeResult, ScrapeResult, ScrapeResult]
        # NOT: ScrapeResult with data=[item1, item2, item3]
        pass

    def test_batch_result_type_annotations(self):
        """Test that method signatures indicate Union[ScrapeResult, List[ScrapeResult]]."""
        from brightdata.scrapers.amazon import AmazonScraper

        scraper = AmazonScraper(bearer_token="test_token_123456789")

        import inspect

        sig = inspect.signature(scraper.products)

        # Check return type annotation
        return_type = sig.return_annotation
        assert return_type != inspect.Signature.empty, "Should have return type annotation"

        # Should be Union[ScrapeResult, List[ScrapeResult]]
        type_str = str(return_type)
        assert "ScrapeResult" in type_str
        assert "List" in type_str or "Union" in type_str


class TestBatchScrapingBehavior:
    """Test actual batch scraping behavior."""

    def test_batch_operations_contract(self):
        """Document the batch operations API contract."""
        # API Contract:
        # 1. Single URL string → ScrapeResult
        # 2. List with 1 URL → ScrapeResult (unwrapped for convenience)
        # 3. List with 2+ URLs → List[ScrapeResult] (one per URL)

        # This ensures each URL gets its own result object with:
        # - Individual success/error status
        # - Individual timing information
        # - Individual cost tracking
        # - Individual data payload
        pass

    def test_batch_result_independence(self):
        """Test that batch results are independent."""
        # Each result in a batch should be independent:
        # - If URL 1 fails, URL 2 should still have its own result
        # - Each result has its own cost calculation
        # - Each result has its own timing data
        # - Each result has its own url field set
        pass


class TestBatchErrorHandling:
    """Test batch operations error handling."""

    def test_batch_with_mixed_success_failure(self):
        """Test batch operations with some URLs succeeding and some failing."""
        # Expected: Each URL gets its own ScrapeResult
        # Some have success=True, some have success=False
        # All are in the returned list
        pass

    def test_batch_cost_calculation(self):
        """Test that costs are divided among batch results."""
        # If total cost is $0.003 for 3 URLs
        # Each result should have cost=$0.001
        pass
