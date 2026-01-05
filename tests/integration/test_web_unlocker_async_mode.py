"""Integration tests for Web Unlocker async mode.

These tests verify that:
1. Sync mode still works (backwards compatibility)
2. Async mode works end-to-end
3. Default mode is sync
4. Both modes return the same normalized data structure
"""

import os
import pytest
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

from brightdata import BrightDataClient


@pytest.fixture
def api_token():
    """Get API token from environment or skip tests."""
    token = os.getenv("BRIGHTDATA_API_TOKEN")
    if not token:
        pytest.skip("API token not found. Set BRIGHTDATA_API_TOKEN to run integration tests.")
    return token


@pytest.fixture
async def async_client(api_token):
    """Create async client instance for testing."""
    async with BrightDataClient(token=api_token) as client:
        yield client


class TestWebUnlockerAsyncMode:
    """Test Web Unlocker async mode functionality."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_scrape_sync_mode_explicit(self, async_client):
        """Test sync mode still works when explicitly specified."""
        result = await async_client.scrape_url(
            url="https://example.com",
            zone=async_client.web_unlocker_zone,
            mode="sync"  # Explicit sync
        )

        assert result.success is True, f"Scrape failed: {result.error}"
        assert result.data is not None
        assert isinstance(result.data, str)
        assert len(result.data) > 0, "No data returned"
        assert result.method == "web_unlocker"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_scrape_default_is_sync(self, async_client):
        """Test default mode is sync (backwards compatibility)."""
        result = await async_client.scrape_url(
            url="https://example.com",
            zone=async_client.web_unlocker_zone
            # No mode parameter - should default to sync
        )

        assert result.success is True, f"Scrape failed: {result.error}"
        assert result.data is not None
        assert isinstance(result.data, str)

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_scrape_async_mode(self, async_client):
        """Test async mode with polling."""
        result = await async_client.scrape_url(
            url="https://example.com",
            zone=async_client.web_unlocker_zone,
            mode="async",
            poll_interval=2,   # Check every 2 seconds
            poll_timeout=30    # Give up after 30 seconds
        )

        assert result.success is True, f"Async scrape failed: {result.error}"
        assert result.data is not None
        assert isinstance(result.data, str)
        assert len(result.data) > 0, "No data from async mode"
        assert result.method == "web_unlocker"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_async_mode_returns_same_structure_as_sync(self, async_client):
        """Test that async mode returns same normalized structure as sync."""
        url = "https://example.com"

        # Run sync mode
        sync_result = await async_client.scrape_url(
            url=url,
            zone=async_client.web_unlocker_zone,
            mode="sync"
        )

        # Run async mode
        async_result = await async_client.scrape_url(
            url=url,
            zone=async_client.web_unlocker_zone,
            mode="async",
            poll_interval=2,
            poll_timeout=30
        )

        # Both should succeed
        assert sync_result.success is True
        assert async_result.success is True

        # Both should have data
        assert sync_result.data is not None
        assert async_result.data is not None

        # Both should be strings (raw HTML)
        assert isinstance(sync_result.data, str)
        assert isinstance(async_result.data, str)

        # Both should have content
        assert len(sync_result.data) > 0
        assert len(async_result.data) > 0

        # Both should have the same method
        assert sync_result.method == "web_unlocker"
        assert async_result.method == "web_unlocker"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_async_mode_with_short_timeout(self, async_client):
        """Test async mode timeout handling."""
        # Use very short timeout to force timeout error
        result = await async_client.scrape_url(
            url="https://example.com",
            zone=async_client.web_unlocker_zone,
            mode="async",
            poll_interval=1,
            poll_timeout=1  # Very short timeout
        )

        # Should fail with timeout error
        assert result.success is False
        assert result.error is not None
        assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_async_mode_multiple_urls(self, async_client):
        """Test async mode with multiple URLs (batch processing)."""
        urls = [
            "https://example.com",
            "https://www.example.org",
            "https://www.example.net"
        ]

        results = await async_client.scrape_url(
            url=urls,
            zone=async_client.web_unlocker_zone,
            mode="async",
            poll_interval=2,
            poll_timeout=60  # Longer timeout for multiple URLs
        )

        # Should get results for all URLs
        assert len(results) == 3

        # Check each result
        for i, result in enumerate(results):
            assert result.success is True, f"URL {i} failed: {result.error}"
            assert result.data is not None
            assert isinstance(result.data, str)
            assert len(result.data) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_sync_mode_with_country(self, async_client):
        """Test sync mode with country parameter."""
        result = await async_client.scrape_url(
            url="https://example.com",
            zone=async_client.web_unlocker_zone,
            country="US",
            mode="sync"
        )

        assert result.success is True
        assert result.data is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_async_mode_with_country(self, async_client):
        """Test async mode with country parameter."""
        result = await async_client.scrape_url(
            url="https://example.com",
            zone=async_client.web_unlocker_zone,
            country="US",
            mode="async",
            poll_interval=2,
            poll_timeout=30
        )

        assert result.success is True
        assert result.data is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_async_mode_with_json_response(self, async_client):
        """Test async mode with JSON response format."""
        result = await async_client.scrape_url(
            url="https://httpbin.org/json",
            zone=async_client.web_unlocker_zone,
            response_format="json",
            mode="async",
            poll_interval=2,
            poll_timeout=30
        )

        assert result.success is True
        assert result.data is not None
        # When response_format="json", data should be a dict
        if result.success:
            assert isinstance(result.data, (dict, list))


class TestWebUnlockerAsyncModeTiming:
    """Test async mode timing and performance characteristics."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_async_mode_has_timing_metadata(self, async_client):
        """Test that async mode populates timing metadata."""
        result = await async_client.scrape_url(
            url="https://example.com",
            zone=async_client.web_unlocker_zone,
            mode="async",
            poll_interval=2,
            poll_timeout=30
        )

        assert result.success is True

        # Check timing metadata
        assert result.trigger_sent_at is not None
        assert result.data_fetched_at is not None

        # Data fetch should be after trigger
        assert result.data_fetched_at >= result.trigger_sent_at
