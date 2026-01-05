"""Integration tests for SERP async mode.

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


class TestSERPAsyncMode:
    """Test SERP async mode functionality."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_google_search_sync_mode_explicit(self, async_client):
        """Test sync mode still works when explicitly specified."""
        result = await async_client.search.google(
            query="python programming",
            zone=async_client.serp_zone,
            mode="sync"  # Explicit sync
        )

        assert result.success is True, f"Search failed: {result.error}"
        assert result.data is not None
        assert len(result.data) > 0, "No search results returned"
        assert result.search_engine == "google"
        assert result.query["q"] == "python programming"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_google_search_default_is_sync(self, async_client):
        """Test default mode is sync (backwards compatibility)."""
        result = await async_client.search.google(
            query="test query",
            zone=async_client.serp_zone
            # No mode parameter - should default to sync
        )

        assert result.success is True, f"Search failed: {result.error}"
        assert result.data is not None
        assert len(result.data) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_google_search_async_mode(self, async_client):
        """Test async mode with polling."""
        result = await async_client.search.google(
            query="python programming",
            zone=async_client.serp_zone,
            mode="async",
            poll_interval=2,   # Check every 2 seconds
            poll_timeout=30    # Give up after 30 seconds
        )

        assert result.success is True, f"Async search failed: {result.error}"
        assert result.data is not None
        assert len(result.data) > 0, "No search results from async mode"
        assert result.search_engine == "google"
        assert result.query["q"] == "python programming"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_async_mode_returns_same_structure_as_sync(self, async_client):
        """Test that async mode returns same normalized structure as sync."""
        query = "machine learning"

        # Run sync mode
        sync_result = await async_client.search.google(
            query=query,
            zone=async_client.serp_zone,
            mode="sync"
        )

        # Run async mode
        async_result = await async_client.search.google(
            query=query,
            zone=async_client.serp_zone,
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

        # Both should be lists
        assert isinstance(sync_result.data, list)
        assert isinstance(async_result.data, list)

        # Both should have results
        assert len(sync_result.data) > 0
        assert len(async_result.data) > 0

        # Structure should be the same (both have rank, title, link, etc.)
        if len(sync_result.data) > 0 and len(async_result.data) > 0:
            sync_first = sync_result.data[0]
            async_first = async_result.data[0]

            # Check that both have the same fields
            assert "rank" in sync_first
            assert "rank" in async_first
            assert "title" in sync_first or "snippet" in sync_first
            assert "title" in async_first or "snippet" in async_first

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_async_mode_with_short_timeout(self, async_client):
        """Test async mode timeout handling."""
        # Use very short timeout to force timeout error
        result = await async_client.search.google(
            query="test",
            zone=async_client.serp_zone,
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
    async def test_async_mode_multiple_queries(self, async_client):
        """Test async mode with multiple queries (batch processing)."""
        queries = ["python", "javascript", "golang"]

        results = await async_client.search.google(
            query=queries,
            zone=async_client.serp_zone,
            mode="async",
            poll_interval=2,
            poll_timeout=60  # Longer timeout for multiple queries
        )

        # Should get results for all queries
        assert len(results) == 3

        # Check each result
        for i, result in enumerate(results):
            assert result.success is True, f"Query {i} failed: {result.error}"
            assert result.data is not None
            assert len(result.data) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_sync_mode_with_location(self, async_client):
        """Test sync mode with location parameter."""
        result = await async_client.search.google(
            query="restaurants",
            zone=async_client.serp_zone,
            location="US",
            mode="sync"
        )

        assert result.success is True
        assert result.data is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_async_mode_with_location(self, async_client):
        """Test async mode with location parameter."""
        result = await async_client.search.google(
            query="restaurants",
            zone=async_client.serp_zone,
            location="US",
            mode="async",
            poll_interval=2,
            poll_timeout=30
        )

        assert result.success is True
        assert result.data is not None


class TestSERPAsyncModeTiming:
    """Test async mode timing and performance characteristics."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_async_mode_has_timing_metadata(self, async_client):
        """Test that async mode populates timing metadata."""
        result = await async_client.search.google(
            query="test",
            zone=async_client.serp_zone,
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
