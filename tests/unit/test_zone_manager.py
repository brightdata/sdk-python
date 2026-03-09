"""Tests for core/zone_manager.py — Zone CRUD and ensure operations."""

import pytest

from brightdata.core.zone_manager import ZoneManager
from brightdata.exceptions.errors import ZoneError, AuthenticationError

from tests.conftest import MockResponse, MockContextManager


# ---------------------------------------------------------------------------
# List Zones
# ---------------------------------------------------------------------------


class TestListZones:
    @pytest.mark.asyncio
    async def test_returns_zones_list(self, mock_engine):
        zones_data = [{"name": "zone1", "type": "unblocker"}, {"name": "zone2", "type": "serp"}]
        mock_engine.get.return_value = MockContextManager(MockResponse(200, json_data=zones_data))

        zm = ZoneManager(mock_engine)
        zones = await zm.list_zones()

        assert zones == zones_data
        mock_engine.get.assert_called_once_with("/zone/get_active_zones")

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_none(self, mock_engine):
        mock_engine.get.return_value = MockContextManager(MockResponse(200, json_data=[]))

        zm = ZoneManager(mock_engine)
        zones = await zm.list_zones()

        assert zones == []

    @pytest.mark.asyncio
    async def test_returns_empty_list_on_null_response(self, mock_engine):
        mock_engine.get.return_value = MockContextManager(MockResponse(200, json_data=None))

        zm = ZoneManager(mock_engine)
        zones = await zm.list_zones()

        assert zones == []

    @pytest.mark.asyncio
    async def test_401_raises_authentication_error(self, mock_engine):
        mock_engine.get.return_value = MockContextManager(
            MockResponse(401, text_data="Invalid token")
        )

        zm = ZoneManager(mock_engine)
        with pytest.raises(AuthenticationError) as exc_info:
            await zm.list_zones()

        assert "401" in str(exc_info.value)
        assert "Invalid token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_403_raises_authentication_error(self, mock_engine):
        mock_engine.get.return_value = MockContextManager(MockResponse(403, text_data="Forbidden"))

        zm = ZoneManager(mock_engine)
        with pytest.raises(AuthenticationError) as exc_info:
            await zm.list_zones()

        assert "403" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_500_raises_zone_error(self, mock_engine):
        mock_engine.get.return_value = MockContextManager(
            MockResponse(500, text_data="Internal server error")
        )

        zm = ZoneManager(mock_engine)
        with pytest.raises(ZoneError) as exc_info:
            await zm.list_zones()

        assert "500" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Create Zone
# ---------------------------------------------------------------------------


class TestCreateZone:
    @pytest.mark.asyncio
    async def test_creates_unblocker_zone(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(MockResponse(201))

        zm = ZoneManager(mock_engine)
        await zm._create_zone("test_unblocker", "unblocker")

        mock_engine.post.assert_called_once()
        call_args = mock_engine.post.call_args
        assert call_args[0][0] == "/zone"
        payload = call_args[1]["json_data"]
        assert payload["zone"]["name"] == "test_unblocker"
        assert payload["zone"]["type"] == "unblocker"
        assert payload["plan"]["type"] == "unblocker"

    @pytest.mark.asyncio
    async def test_creates_serp_zone(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(MockResponse(200))

        zm = ZoneManager(mock_engine)
        await zm._create_zone("test_serp", "serp")

        payload = mock_engine.post.call_args[1]["json_data"]
        assert payload["zone"]["name"] == "test_serp"
        assert payload["zone"]["type"] == "serp"
        assert payload["plan"]["type"] == "unblocker"
        assert payload["plan"]["serp"] is True

    @pytest.mark.asyncio
    async def test_creates_browser_zone(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(MockResponse(201))

        zm = ZoneManager(mock_engine)
        await zm._create_zone("test_browser", "browser")

        payload = mock_engine.post.call_args[1]["json_data"]
        assert payload["zone"]["name"] == "test_browser"
        assert payload["zone"]["type"] == "browser"
        assert payload["plan"]["type"] == "browser"

    @pytest.mark.asyncio
    async def test_409_conflict_does_not_raise(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(MockResponse(409, text_data="Conflict"))

        zm = ZoneManager(mock_engine)
        await zm._create_zone("existing_zone", "unblocker")  # should not raise

    @pytest.mark.asyncio
    async def test_already_exists_message_does_not_raise(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(
            MockResponse(400, text_data="Zone already exists")
        )

        zm = ZoneManager(mock_engine)
        await zm._create_zone("existing_zone", "unblocker")  # should not raise

    @pytest.mark.asyncio
    async def test_duplicate_name_message_does_not_raise(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(
            MockResponse(400, text_data="Duplicate zone name")
        )

        zm = ZoneManager(mock_engine)
        await zm._create_zone("duplicate_zone", "unblocker")  # should not raise

    @pytest.mark.asyncio
    async def test_401_raises_authentication_error(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(
            MockResponse(401, text_data="Unauthorized")
        )

        zm = ZoneManager(mock_engine)
        with pytest.raises(AuthenticationError) as exc_info:
            await zm._create_zone("test_zone", "unblocker")

        assert "401" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_403_raises_authentication_error(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(MockResponse(403, text_data="Forbidden"))

        zm = ZoneManager(mock_engine)
        with pytest.raises(AuthenticationError) as exc_info:
            await zm._create_zone("test_zone", "unblocker")

        assert "403" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_400_bad_request_raises_zone_error(self, mock_engine):
        mock_engine.post.return_value = MockContextManager(
            MockResponse(400, text_data="Invalid zone configuration")
        )

        zm = ZoneManager(mock_engine)
        with pytest.raises(ZoneError) as exc_info:
            await zm._create_zone("test_zone", "unblocker")

        assert "400" in str(exc_info.value)
        assert "Invalid zone configuration" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Ensure Required Zones
# ---------------------------------------------------------------------------


class TestEnsureRequiredZones:
    @pytest.mark.asyncio
    async def test_skips_creation_when_all_exist(self, mock_engine):
        zones_data = [
            {"name": "sdk_unlocker", "type": "unblocker"},
            {"name": "sdk_serp", "type": "serp"},
        ]
        mock_engine.get.return_value = MockContextManager(MockResponse(200, json_data=zones_data))

        zm = ZoneManager(mock_engine)
        await zm.ensure_required_zones(web_unlocker_zone="sdk_unlocker", serp_zone="sdk_serp")

        mock_engine.get.assert_called()
        mock_engine.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_missing_zones(self, mock_engine):
        mock_engine.get.side_effect = [
            MockContextManager(MockResponse(200, json_data=[])),
            MockContextManager(
                MockResponse(
                    200,
                    json_data=[
                        {"name": "sdk_unlocker", "type": "unblocker"},
                        {"name": "sdk_serp", "type": "serp"},
                    ],
                )
            ),
        ]
        mock_engine.post.return_value = MockContextManager(MockResponse(201))

        zm = ZoneManager(mock_engine)
        await zm.ensure_required_zones(web_unlocker_zone="sdk_unlocker", serp_zone="sdk_serp")

        assert mock_engine.post.call_count == 2

    @pytest.mark.asyncio
    async def test_creates_only_web_unlocker(self, mock_engine):
        mock_engine.get.side_effect = [
            MockContextManager(MockResponse(200, json_data=[])),
            MockContextManager(MockResponse(200, json_data=[{"name": "sdk_unlocker"}])),
        ]
        mock_engine.post.return_value = MockContextManager(MockResponse(201))

        zm = ZoneManager(mock_engine)
        await zm.ensure_required_zones(web_unlocker_zone="sdk_unlocker")

        assert mock_engine.post.call_count == 1

    @pytest.mark.asyncio
    async def test_creates_unblocker_and_serp(self, mock_engine):
        mock_engine.get.side_effect = [
            MockContextManager(MockResponse(200, json_data=[])),
            MockContextManager(
                MockResponse(
                    200,
                    json_data=[
                        {"name": "sdk_unlocker"},
                        {"name": "sdk_serp"},
                    ],
                )
            ),
        ]
        mock_engine.post.return_value = MockContextManager(MockResponse(201))

        zm = ZoneManager(mock_engine)
        await zm.ensure_required_zones(web_unlocker_zone="sdk_unlocker", serp_zone="sdk_serp")

        assert mock_engine.post.call_count == 2

    @pytest.mark.asyncio
    async def test_verification_failure_logs_warning(self, mock_engine, caplog):
        mock_engine.get.side_effect = [
            MockContextManager(MockResponse(200, json_data=[])),  # initial list
            MockContextManager(MockResponse(200, json_data=[])),  # verify 1
            MockContextManager(MockResponse(200, json_data=[])),  # verify 2
            MockContextManager(MockResponse(200, json_data=[])),  # verify 3
            MockContextManager(MockResponse(200, json_data=[])),  # verify 4
            MockContextManager(MockResponse(200, json_data=[])),  # verify 5
        ]
        mock_engine.post.return_value = MockContextManager(MockResponse(201))

        zm = ZoneManager(mock_engine)
        await zm.ensure_required_zones(web_unlocker_zone="sdk_unlocker")

        assert any("Zone verification failed" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# Integration-style
# ---------------------------------------------------------------------------


class TestZoneManagerIntegration:
    @pytest.mark.asyncio
    async def test_full_workflow_no_creation_needed(self, mock_engine):
        zones_data = [{"name": "my_zone", "type": "unblocker", "status": "active"}]
        mock_engine.get.return_value = MockContextManager(MockResponse(200, json_data=zones_data))

        zm = ZoneManager(mock_engine)

        zones = await zm.list_zones()
        assert len(zones) == 1
        assert zones[0]["name"] == "my_zone"

        await zm.ensure_required_zones(web_unlocker_zone="my_zone")
        mock_engine.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_full_workflow_creates_then_lists(self, mock_engine):
        zones_after = [{"name": "new_zone", "type": "unblocker"}]
        mock_engine.get.side_effect = [
            MockContextManager(MockResponse(200, json_data=[])),
            MockContextManager(MockResponse(200, json_data=zones_after)),
            MockContextManager(MockResponse(200, json_data=zones_after)),
        ]
        mock_engine.post.return_value = MockContextManager(MockResponse(201))

        zm = ZoneManager(mock_engine)
        await zm.ensure_required_zones(web_unlocker_zone="new_zone")
        assert mock_engine.post.call_count == 1

        zones = await zm.list_zones()
        assert len(zones) == 1
        assert zones[0]["name"] == "new_zone"
