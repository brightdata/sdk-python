"""Unit tests for AsyncUnblockerClient."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from brightdata.api.async_unblocker import AsyncUnblockerClient
from brightdata.exceptions import APIError


class MockAsyncContextManager:
    """Helper to mock async context managers."""

    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestAsyncUnblockerClient:
    """Test AsyncUnblockerClient functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MagicMock()
        self.engine.BASE_URL = "https://api.brightdata.com"
        self.client = AsyncUnblockerClient(self.engine)

    @pytest.mark.asyncio
    async def test_trigger_success(self):
        """Test successful trigger returns response_id from header."""
        # Mock response with x-response-id header
        response = MagicMock()
        response.headers.get.return_value = "test_response_id_123"

        # Mock post_to_url to return async context manager
        self.engine.post_to_url = MagicMock(
            return_value=MockAsyncContextManager(response)
        )

        # Trigger request
        response_id = await self.client.trigger(
            zone="test_zone",
            url="https://example.com"
        )

        # Verify response_id returned
        assert response_id == "test_response_id_123"

        # Verify correct endpoint called
        self.engine.post_to_url.assert_called_once()
        call_args = self.engine.post_to_url.call_args
        assert call_args[0][0] == "https://api.brightdata.com/unblocker/req"
        assert call_args[1]["params"] == {"zone": "test_zone"}
        assert call_args[1]["json_data"]["url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_trigger_with_additional_params(self):
        """Test trigger passes additional parameters correctly."""
        response = MagicMock()
        response.headers.get.return_value = "response_id_456"

        self.engine.post_to_url = MagicMock(
            return_value=MockAsyncContextManager(response)
        )

        # Trigger with additional params
        response_id = await self.client.trigger(
            zone="my_zone",
            url="https://google.com/search?q=test",
            format="raw",
            country="US"
        )

        assert response_id == "response_id_456"

        # Verify params merged into payload
        call_args = self.engine.post_to_url.call_args
        payload = call_args[1]["json_data"]
        assert payload["url"] == "https://google.com/search?q=test"
        assert payload["format"] == "raw"
        assert payload["country"] == "US"

    @pytest.mark.asyncio
    async def test_trigger_no_response_id(self):
        """Test trigger returns None when no response_id header."""
        response = MagicMock()
        response.headers.get.return_value = None  # No x-response-id

        self.engine.post_to_url = MagicMock(
            return_value=MockAsyncContextManager(response)
        )

        response_id = await self.client.trigger(
            zone="test_zone",
            url="https://example.com"
        )

        assert response_id is None

    @pytest.mark.asyncio
    async def test_get_status_ready(self):
        """Test get_status returns 'ready' for HTTP 200."""
        response = MagicMock()
        response.status = 200

        self.engine.get_from_url = MagicMock(
            return_value=MockAsyncContextManager(response)
        )

        status = await self.client.get_status(
            zone="test_zone",
            response_id="abc123"
        )

        assert status == "ready"

        # Verify correct endpoint and params
        call_args = self.engine.get_from_url.call_args
        assert call_args[0][0] == "https://api.brightdata.com/unblocker/get_result"
        assert call_args[1]["params"]["zone"] == "test_zone"
        assert call_args[1]["params"]["response_id"] == "abc123"

    @pytest.mark.asyncio
    async def test_get_status_pending(self):
        """Test get_status returns 'pending' for HTTP 202."""
        response = MagicMock()
        response.status = 202

        self.engine.get_from_url = MagicMock(
            return_value=MockAsyncContextManager(response)
        )

        status = await self.client.get_status(
            zone="test_zone",
            response_id="xyz789"
        )

        assert status == "pending"

    @pytest.mark.asyncio
    async def test_get_status_error(self):
        """Test get_status returns 'error' for non-200/202 status."""
        # Test various error codes
        for error_code in [400, 404, 500, 503]:
            response = MagicMock()
            response.status = error_code

            self.engine.get_from_url = MagicMock(
                return_value=MockAsyncContextManager(response)
            )

            status = await self.client.get_status(
                zone="test_zone",
                response_id="err123"
            )

            assert status == "error", f"Expected 'error' for HTTP {error_code}"

    @pytest.mark.asyncio
    async def test_fetch_result_success(self):
        """Test fetch_result returns parsed JSON for HTTP 200."""
        expected_data = {
            "general": {"search_engine": "google"},
            "organic": [{"title": "Result 1"}]
        }

        response = MagicMock()
        response.status = 200
        response.json = AsyncMock(return_value=expected_data)

        self.engine.get_from_url = MagicMock(
            return_value=MockAsyncContextManager(response)
        )

        data = await self.client.fetch_result(
            zone="test_zone",
            response_id="fetch123"
        )

        assert data == expected_data
        response.json.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_result_not_ready(self):
        """Test fetch_result raises APIError for HTTP 202 (pending)."""
        response = MagicMock()
        response.status = 202

        self.engine.get_from_url = MagicMock(
            return_value=MockAsyncContextManager(response)
        )

        with pytest.raises(APIError) as exc_info:
            await self.client.fetch_result(
                zone="test_zone",
                response_id="pending123"
            )

        assert "not ready yet" in str(exc_info.value).lower()
        assert "202" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_result_error(self):
        """Test fetch_result raises APIError for error status codes."""
        response = MagicMock()
        response.status = 500
        response.text = AsyncMock(return_value="Internal Server Error")

        self.engine.get_from_url = MagicMock(
            return_value=MockAsyncContextManager(response)
        )

        with pytest.raises(APIError) as exc_info:
            await self.client.fetch_result(
                zone="test_zone",
                response_id="error123"
            )

        error_msg = str(exc_info.value)
        assert "500" in error_msg
        assert "Internal Server Error" in error_msg

    @pytest.mark.asyncio
    async def test_endpoint_constants(self):
        """Test that endpoint constants are correct."""
        assert self.client.TRIGGER_ENDPOINT == "/unblocker/req"
        assert self.client.FETCH_ENDPOINT == "/unblocker/get_result"

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initializes with AsyncEngine."""
        engine = MagicMock()
        client = AsyncUnblockerClient(engine)

        assert client.engine is engine
