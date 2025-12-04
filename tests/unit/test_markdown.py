"""Tests for markdown output formatter."""

import pytest
from brightdata.models import ScrapeResult, SearchResult
from brightdata.formatters import MarkdownFormatter, FormatterRegistry


class TestMarkdownFormatter:
    """Test markdown formatting functionality."""

    def test_formatter_registered(self):
        """Test markdown formatter is registered."""
        assert FormatterRegistry.is_registered("markdown")
        assert FormatterRegistry.is_registered("md")  # Alias

    def test_format_success_result(self):
        """Test markdown formatting for successful result."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            data={"title": "Test", "price": 99.99},
            cost=0.001,
            platform="test",
        )

        md = result.to_markdown()

        assert "# Result: ✅ Success" in md
        assert "## Metadata" in md
        assert "## Data" in md
        assert "| Field | Value |" in md
        assert "$0.0010 USD" in md

    def test_format_failed_result(self):
        """Test markdown formatting for failed result."""
        result = ScrapeResult(success=False, url="", error="API Error: 404 Not Found", data=None)

        md = result.to_markdown()

        assert "# Result: ❌ Failed" in md
        assert "## Error" in md
        assert "⚠️ API Error: 404 Not Found" in md

    def test_format_list_data_as_table(self):
        """Test list data is formatted as markdown table."""
        result = ScrapeResult(
            success=True,
            url="",
            data=[
                {"name": "Product 1", "price": 10.99, "rating": 4.5},
                {"name": "Product 2", "price": 20.99, "rating": 4.8},
                {"name": "Product 3", "price": 15.99, "rating": 4.2},
            ],
        )

        md = result.to_markdown()

        # Should have markdown table
        assert "|" in md
        assert "| --- |" in md or "|---|" in md
        assert "Product 1" in md
        assert "Product 2" in md

    def test_format_dict_data_as_table(self):
        """Test dict data is formatted as markdown table."""
        result = ScrapeResult(
            success=True,
            url="",
            data={
                "title": "Test Product",
                "price": 99.99,
                "rating": 4.5,
                "reviews": 100,
            },
        )

        md = result.to_markdown()

        assert "| Key | Value |" in md
        assert "`title`" in md
        assert "Test Product" in md

    def test_save_to_file_markdown(self, tmp_path):
        """Test saving result as markdown file."""
        result = ScrapeResult(success=True, url="", data={"test": "data"}, cost=0.001)

        output_file = tmp_path / "result.md"
        result.save_to_file(output_file, format="markdown")

        assert output_file.exists()

        content = output_file.read_text()
        assert "# Result:" in content
        assert "## Metadata" in content

    def test_markdown_handles_large_data(self):
        """Test markdown formatter limits data for readability."""
        # Create 50 items
        large_data = [{"id": i, "name": f"Item {i}"} for i in range(50)]

        result = ScrapeResult(success=True, url="", data=large_data)

        md = result.to_markdown()

        # Should limit to 10 rows
        assert "Item 0" in md
        assert "Item 9" in md or "Item 10" in md
        assert "... and" in md  # Indicates truncation

    def test_markdown_metadata_fields(self):
        """Test markdown includes all metadata fields."""
        result = ScrapeResult(
            success=True,
            url="https://example.com",
            data=[],
            cost=0.005,
            platform="amazon",
            method="web_scraper",
            snapshot_id="s_abc123",
        )

        md = result.to_markdown()

        assert "Platform" in md
        assert "amazon" in md
        assert "Method" in md
        assert "web_scraper" in md
        assert "Snapshot ID" in md
        assert "s_abc123" in md
        assert "Cost" in md
        assert "$0.0050 USD" in md

    def test_search_result_markdown(self):
        """Test Search results format correctly."""
        result = SearchResult(
            success=True,
            query="python tutorial",
            data=[{"position": 1, "title": "Python Docs", "url": "https://python.org"}],
        )

        md = result.to_markdown()

        assert "# Result: ✅ Success" in md
        assert "Python Docs" in md


class TestFormatterRegistry:
    """Test formatter registry functionality."""

    def test_list_all_formats(self):
        """Test listing all available formats."""
        formats = FormatterRegistry.list_formats()

        assert "json" in formats
        assert "pretty" in formats
        assert "minimal" in formats
        assert "markdown" in formats
        assert "md" in formats

    def test_get_formatter_by_name(self):
        """Test getting formatter by name."""
        formatter = FormatterRegistry.get_formatter("markdown")
        assert isinstance(formatter, MarkdownFormatter)

    def test_unknown_format_raises_error(self):
        """Test unknown format raises helpful error."""
        with pytest.raises(ValueError) as exc_info:
            FormatterRegistry.get_formatter("unknown")

        assert "Unknown format" in str(exc_info.value)
        assert "Available formats:" in str(exc_info.value)

    def test_format_names_case_insensitive(self):
        """Test format names are case-insensitive."""
        formatter1 = FormatterRegistry.get_formatter("MARKDOWN")
        formatter2 = FormatterRegistry.get_formatter("markdown")
        formatter3 = FormatterRegistry.get_formatter("MarkDown")

        assert isinstance(formatter1, MarkdownFormatter)
        assert isinstance(formatter2, MarkdownFormatter)
        assert isinstance(formatter3, MarkdownFormatter)
