"""Tests for web_unlocker/async_client.py — Trigger, status, and fetch operations."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from brightdata.web_unlocker.async_client import AsyncUnblockerClient
from brightdata.exceptions import APIError

from tests.conftest import MockContextManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    eng = MagicMock()
    eng.BASE_URL = "https://api.brightdata.com"
    return eng


@pytest.fixture
def client(engine):
    return AsyncUnblockerClient(engine)


# ---------------------------------------------------------------------------
# Trigger
# ---------------------------------------------------------------------------


class TestTrigger:
    @pytest.mark.asyncio
    async def test_returns_response_id(self, client, engine):
        response = MagicMock()
        response.headers.get.return_value = "test_response_id_123"
        engine.post_to_url = MagicMock(return_value=MockContextManager(response))

        response_id = await client.trigger(zone="test_zone", url="https://example.com")

        assert response_id == "test_response_id_123"
        engine.post_to_url.assert_called_once()
        call_args = engine.post_to_url.call_args
        assert call_args[0][0] == "https://api.brightdata.com/unblocker/req"
        assert call_args[1]["params"] == {"zone": "test_zone"}
        assert call_args[1]["json_data"]["url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_passes_additional_params(self, client, engine):
        response = MagicMock()
        response.headers.get.return_value = "response_id_456"
        engine.post_to_url = MagicMock(return_value=MockContextManager(response))

        response_id = await client.trigger(
            zone="my_zone", url="https://google.com/search?q=test", format="raw", country="US"
        )

        assert response_id == "response_id_456"
        payload = engine.post_to_url.call_args[1]["json_data"]
        assert payload["url"] == "https://google.com/search?q=test"
        assert payload["format"] == "raw"
        assert payload["country"] == "US"

    @pytest.mark.asyncio
    async def test_returns_none_when_no_response_id(self, client, engine):
        response = MagicMock()
        response.headers.get.return_value = None
        engine.post_to_url = MagicMock(return_value=MockContextManager(response))

        response_id = await client.trigger(zone="test_zone", url="https://example.com")
        assert response_id is None


# ---------------------------------------------------------------------------
# Get Status
# ---------------------------------------------------------------------------


class TestGetStatus:
    @pytest.mark.asyncio
    async def test_200_returns_ready(self, client, engine):
        response = MagicMock()
        response.status = 200
        engine.get_from_url = MagicMock(return_value=MockContextManager(response))

        status = await client.get_status(zone="test_zone", response_id="abc123")

        assert status == "ready"
        call_args = engine.get_from_url.call_args
        assert call_args[0][0] == "https://api.brightdata.com/unblocker/get_result"
        assert call_args[1]["params"]["zone"] == "test_zone"
        assert call_args[1]["params"]["response_id"] == "abc123"

    @pytest.mark.asyncio
    async def test_202_returns_pending(self, client, engine):
        response = MagicMock()
        response.status = 202
        engine.get_from_url = MagicMock(return_value=MockContextManager(response))

        status = await client.get_status(zone="test_zone", response_id="xyz789")
        assert status == "pending"

    @pytest.mark.asyncio
    async def test_error_codes_return_error(self, client, engine):
        for error_code in [400, 404, 500, 503]:
            response = MagicMock()
            response.status = error_code
            engine.get_from_url = MagicMock(return_value=MockContextManager(response))

            status = await client.get_status(zone="test_zone", response_id="err123")
            assert status == "error", f"Expected 'error' for HTTP {error_code}"


# ---------------------------------------------------------------------------
# Fetch Result
# ---------------------------------------------------------------------------


class TestFetchResult:
    @pytest.mark.asyncio
    async def test_200_returns_json(self, client, engine):
        expected_data = {"general": {"search_engine": "google"}, "organic": [{"title": "Result 1"}]}
        response = MagicMock()
        response.status = 200
        response.json = AsyncMock(return_value=expected_data)
        engine.get_from_url = MagicMock(return_value=MockContextManager(response))

        data = await client.fetch_result(zone="test_zone", response_id="fetch123")

        assert data == expected_data
        response.json.assert_called_once()

    @pytest.mark.asyncio
    async def test_202_raises_api_error(self, client, engine):
        response = MagicMock()
        response.status = 202
        engine.get_from_url = MagicMock(return_value=MockContextManager(response))

        with pytest.raises(APIError) as exc_info:
            await client.fetch_result(zone="test_zone", response_id="pending123")

        assert "not ready yet" in str(exc_info.value).lower()
        assert "202" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_500_raises_api_error(self, client, engine):
        response = MagicMock()
        response.status = 500
        response.text = AsyncMock(return_value="Internal Server Error")
        engine.get_from_url = MagicMock(return_value=MockContextManager(response))

        with pytest.raises(APIError) as exc_info:
            await client.fetch_result(zone="test_zone", response_id="error123")

        assert "500" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Constants and init
# ---------------------------------------------------------------------------


class TestClientSetup:
    def test_endpoint_constants(self, client):
        assert client.TRIGGER_ENDPOINT == "/unblocker/req"
        assert client.FETCH_ENDPOINT == "/unblocker/get_result"

    def test_stores_engine_reference(self):
        engine = MagicMock()
        c = AsyncUnblockerClient(engine)
        assert c.engine is engine
