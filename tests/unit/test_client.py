"""Tests for client.py — BrightDataClient init, services, context manager, API methods."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from brightdata.client import BrightDataClient
from brightdata.exceptions import ValidationError, AuthenticationError, APIError
from brightdata.scrapers.service import ScrapeService
from brightdata.serp.service import SearchService
from brightdata.crawler.service import CrawlerService
from brightdata.datasets import DatasetsClient

from tests.conftest import MockResponse, MockContextManager


# ---------------------------------------------------------------------------
# Token loading
# ---------------------------------------------------------------------------


class TestTokenLoading:
    def test_accepts_explicit_token(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.token == "tok_1234567890"

    def test_strips_whitespace(self):
        c = BrightDataClient(token="  tok_1234567890  ")
        assert c.token == "tok_1234567890"

    @patch.dict("os.environ", {"BRIGHTDATA_API_TOKEN": "env_token_12345"})
    def test_reads_from_env(self):
        c = BrightDataClient()
        assert c.token == "env_token_12345"

    def test_raises_without_token(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValidationError, match="API token required"):
                BrightDataClient()

    def test_rejects_short_token(self):
        with pytest.raises(ValidationError, match="at least 10 characters"):
            BrightDataClient(token="short")

    def test_rejects_non_string_token(self):
        with pytest.raises(ValidationError):
            BrightDataClient(token=12345678901)  # type: ignore

    def test_explicit_token_takes_precedence(self):
        with patch.dict("os.environ", {"BRIGHTDATA_API_TOKEN": "env_token_12345"}):
            c = BrightDataClient(token="explicit_token_12345")
            assert c.token == "explicit_token_12345"


# ---------------------------------------------------------------------------
# Init configuration
# ---------------------------------------------------------------------------


class TestInitConfig:
    def test_default_timeout(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.timeout == 30

    def test_custom_timeout(self):
        c = BrightDataClient(token="tok_1234567890", timeout=120)
        assert c.timeout == 120

    def test_default_zone_names(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.web_unlocker_zone == "sdk_unlocker"
        assert c.serp_zone == "sdk_serp"

    def test_custom_zone_names(self):
        c = BrightDataClient(
            token="tok_1234567890",
            web_unlocker_zone="my_unlocker",
            serp_zone="my_serp",
        )
        assert c.web_unlocker_zone == "my_unlocker"
        assert c.serp_zone == "my_serp"

    def test_creates_engine(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.engine is not None
        assert c.engine.bearer_token == "tok_1234567890"

    def test_services_none_before_access(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c._scrape_service is None
        assert c._search_service is None
        assert c._crawler_service is None
        assert c._datasets_client is None

    def test_auto_create_zones_default_true(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.auto_create_zones is True

    def test_auto_create_zones_can_disable(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        assert c.auto_create_zones is False


# ---------------------------------------------------------------------------
# Service properties (lazy init)
# ---------------------------------------------------------------------------


class TestServiceProperties:
    def test_scrape_returns_scrape_service(self):
        c = BrightDataClient(token="tok_1234567890")
        s = c.scrape
        assert isinstance(s, ScrapeService)

    def test_scrape_returns_same_instance(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.scrape is c.scrape

    def test_search_returns_search_service(self):
        c = BrightDataClient(token="tok_1234567890")
        s = c.search
        assert isinstance(s, SearchService)

    def test_search_returns_same_instance(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.search is c.search

    def test_crawler_returns_crawler_service(self):
        c = BrightDataClient(token="tok_1234567890")
        s = c.crawler
        assert isinstance(s, CrawlerService)

    def test_crawler_returns_same_instance(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.crawler is c.crawler

    def test_datasets_returns_datasets_client(self):
        c = BrightDataClient(token="tok_1234567890")
        d = c.datasets
        assert isinstance(d, DatasetsClient)

    def test_datasets_returns_same_instance(self):
        c = BrightDataClient(token="tok_1234567890")
        assert c.datasets is c.datasets


# ---------------------------------------------------------------------------
# Browser property
# ---------------------------------------------------------------------------


class TestBrowserProperty:
    def test_raises_without_credentials(self):
        with patch.dict("os.environ", {}, clear=False):
            # Ensure env vars are not set
            import os

            os.environ.pop("BRIGHTDATA_BROWSERAPI_USERNAME", None)
            os.environ.pop("BRIGHTDATA_BROWSERAPI_PASSWORD", None)

            c = BrightDataClient(token="tok_1234567890")
            with pytest.raises(ValidationError, match="Browser API credentials"):
                _ = c.browser

    def test_accepts_explicit_credentials(self):
        c = BrightDataClient(
            token="tok_1234567890",
            browser_username="brd-user",
            browser_password="pass123",
        )
        b = c.browser
        assert b is not None

    @patch.dict(
        "os.environ",
        {
            "BRIGHTDATA_BROWSERAPI_USERNAME": "env-user",
            "BRIGHTDATA_BROWSERAPI_PASSWORD": "env-pass",
        },
    )
    def test_reads_credentials_from_env(self):
        c = BrightDataClient(token="tok_1234567890")
        b = c.browser
        assert b is not None

    def test_returns_same_instance(self):
        c = BrightDataClient(
            token="tok_1234567890",
            browser_username="brd-user",
            browser_password="pass123",
        )
        assert c.browser is c.browser


# ---------------------------------------------------------------------------
# _ensure_initialized
# ---------------------------------------------------------------------------


class TestEnsureInitialized:
    def test_raises_if_no_session(self):
        c = BrightDataClient(token="tok_1234567890")
        with pytest.raises(RuntimeError, match="not initialized"):
            c._ensure_initialized()


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestContextManager:
    @pytest.mark.asyncio
    async def test_aenter_creates_session(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            assert c.engine._session is not None

    @pytest.mark.asyncio
    async def test_aexit_closes_session(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            session = c.engine._session
        assert c.engine._session is None
        assert session.closed

    @pytest.mark.asyncio
    async def test_returns_self(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c as client:
            assert client is c

    @pytest.mark.asyncio
    async def test_validate_token_on_enter_success(self):
        c = BrightDataClient(
            token="tok_1234567890",
            validate_token=True,
            auto_create_zones=False,
        )
        with patch.object(c, "test_connection", new_callable=AsyncMock, return_value=True):
            with patch.object(c, "_ensure_zones", new_callable=AsyncMock):
                async with c:
                    pass  # should not raise

    @pytest.mark.asyncio
    async def test_validate_token_on_enter_failure(self):
        c = BrightDataClient(
            token="tok_1234567890",
            validate_token=True,
            auto_create_zones=False,
        )
        with patch.object(c, "test_connection", new_callable=AsyncMock, return_value=False):
            with pytest.raises(AuthenticationError, match="Token validation failed"):
                async with c:
                    pass


# ---------------------------------------------------------------------------
# test_connection
# ---------------------------------------------------------------------------


class TestTestConnection:
    @pytest.mark.asyncio
    async def test_returns_true_on_200(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c.engine.get_from_url = MagicMock(
                return_value=MockContextManager(MockResponse(200, json_data=[]))
            )
            result = await c.test_connection()
            assert result is True
            assert c._is_connected is True

    @pytest.mark.asyncio
    async def test_returns_false_on_401(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c.engine.get_from_url = MagicMock(return_value=MockContextManager(MockResponse(401)))
            result = await c.test_connection()
            assert result is False
            assert c._is_connected is False

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c.engine.get_from_url = MagicMock(side_effect=OSError("Network down"))
            result = await c.test_connection()
            assert result is False


# ---------------------------------------------------------------------------
# get_account_info
# ---------------------------------------------------------------------------


class TestGetAccountInfo:
    @pytest.mark.asyncio
    async def test_returns_account_info(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            zones = [{"name": "zone1"}, {"name": "zone2"}]
            c.engine.get_from_url = MagicMock(
                return_value=MockContextManager(MockResponse(200, json_data=zones))
            )
            info = await c.get_account_info()

            assert info["zone_count"] == 2
            assert info["token_valid"] is True
            assert len(info["zones"]) == 2

    @pytest.mark.asyncio
    async def test_caches_result(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c.engine.get_from_url = MagicMock(
                return_value=MockContextManager(MockResponse(200, json_data=[{"name": "z"}]))
            )
            info1 = await c.get_account_info()
            info2 = await c.get_account_info()

            assert info1 is info2
            # Should only call API once
            c.engine.get_from_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_bypasses_cache(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c.engine.get_from_url = MagicMock(
                return_value=MockContextManager(MockResponse(200, json_data=[]))
            )
            await c.get_account_info()
            await c.get_account_info(refresh=True)

            assert c.engine.get_from_url.call_count == 2

    @pytest.mark.asyncio
    async def test_401_raises_auth_error(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c.engine.get_from_url = MagicMock(
                return_value=MockContextManager(MockResponse(401, text_data="Unauthorized"))
            )
            with pytest.raises(AuthenticationError, match="Invalid token"):
                await c.get_account_info()

    @pytest.mark.asyncio
    async def test_500_raises_api_error(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c.engine.get_from_url = MagicMock(
                return_value=MockContextManager(MockResponse(500, text_data="Server Error"))
            )
            with pytest.raises(APIError, match="Failed to get account info"):
                await c.get_account_info()

    @pytest.mark.asyncio
    async def test_empty_zones_warns(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c.engine.get_from_url = MagicMock(
                return_value=MockContextManager(MockResponse(200, json_data=[]))
            )
            with pytest.warns(UserWarning, match="No active zones"):
                await c.get_account_info()


# ---------------------------------------------------------------------------
# list_zones / delete_zone
# ---------------------------------------------------------------------------


class TestZoneOperations:
    @pytest.mark.asyncio
    async def test_list_zones_delegates_to_zone_manager(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c._zone_manager = AsyncMock()
            c._zone_manager.list_zones = AsyncMock(return_value=[{"name": "z1"}])

            zones = await c.list_zones()

            assert zones == [{"name": "z1"}]

    @pytest.mark.asyncio
    async def test_list_zones_creates_zone_manager(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            # Mock engine to avoid real HTTP
            c.engine.get = MagicMock(
                return_value=MockContextManager(MockResponse(200, json_data=[]))
            )
            zones = await c.list_zones()
            assert c._zone_manager is not None

    @pytest.mark.asyncio
    async def test_delete_zone_delegates(self):
        c = BrightDataClient(token="tok_1234567890", auto_create_zones=False)
        async with c:
            c._zone_manager = AsyncMock()
            c._zone_manager.delete_zone = AsyncMock()

            await c.delete_zone("test_zone")

            c._zone_manager.delete_zone.assert_called_once_with("test_zone")


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------


class TestRepr:
    def test_includes_token_preview(self):
        c = BrightDataClient(token="tok_1234567890_abcde")
        r = repr(c)
        assert "tok_12345" in r
        assert "abcde" in r

    def test_shows_not_tested_by_default(self):
        c = BrightDataClient(token="tok_1234567890")
        assert "Not tested" in repr(c)
