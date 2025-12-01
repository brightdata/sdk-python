"""Unit tests for ZoneManager."""

import pytest
from unittest.mock import MagicMock
from brightdata.core.zone_manager import ZoneManager
from brightdata.exceptions.errors import ZoneError, AuthenticationError


class MockResponse:
    """Mock aiohttp response for testing."""

    def __init__(self, status: int, json_data=None, text_data=""):
        self.status = status
        self._json_data = json_data
        self._text_data = text_data

    async def json(self):
        return self._json_data

    async def text(self):
        return self._text_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_engine():
    """Create a mock engine for testing."""
    engine = MagicMock()
    return engine


class TestZoneManagerListZones:
    """Tests for listing zones."""

    @pytest.mark.asyncio
    async def test_list_zones_success(self, mock_engine):
        """Test successful zone listing."""
        zones_data = [{"name": "zone1", "type": "unblocker"}, {"name": "zone2", "type": "serp"}]
        mock_engine.get.return_value = MockResponse(200, json_data=zones_data)

        zone_manager = ZoneManager(mock_engine)
        zones = await zone_manager.list_zones()

        assert zones == zones_data
        mock_engine.get.assert_called_once_with("/zone/get_active_zones")

    @pytest.mark.asyncio
    async def test_list_zones_empty(self, mock_engine):
        """Test listing zones when none exist."""
        mock_engine.get.return_value = MockResponse(200, json_data=[])

        zone_manager = ZoneManager(mock_engine)
        zones = await zone_manager.list_zones()

        assert zones == []

    @pytest.mark.asyncio
    async def test_list_zones_null_response(self, mock_engine):
        """Test listing zones when API returns null."""
        mock_engine.get.return_value = MockResponse(200, json_data=None)

        zone_manager = ZoneManager(mock_engine)
        zones = await zone_manager.list_zones()

        assert zones == []

    @pytest.mark.asyncio
    async def test_list_zones_auth_error_401(self, mock_engine):
        """Test listing zones with 401 authentication error."""
        mock_engine.get.return_value = MockResponse(401, text_data="Invalid token")

        zone_manager = ZoneManager(mock_engine)
        with pytest.raises(AuthenticationError) as exc_info:
            await zone_manager.list_zones()

        assert "401" in str(exc_info.value)
        assert "Invalid token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_zones_auth_error_403(self, mock_engine):
        """Test listing zones with 403 forbidden error."""
        mock_engine.get.return_value = MockResponse(403, text_data="Forbidden")

        zone_manager = ZoneManager(mock_engine)
        with pytest.raises(AuthenticationError) as exc_info:
            await zone_manager.list_zones()

        assert "403" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_zones_api_error(self, mock_engine):
        """Test listing zones with general API error."""
        mock_engine.get.return_value = MockResponse(500, text_data="Internal server error")

        zone_manager = ZoneManager(mock_engine)
        with pytest.raises(ZoneError) as exc_info:
            await zone_manager.list_zones()

        assert "500" in str(exc_info.value)


class TestZoneManagerCreateZone:
    """Tests for zone creation."""

    @pytest.mark.asyncio
    async def test_create_unblocker_zone_success(self, mock_engine):
        """Test creating an unblocker zone successfully."""
        mock_engine.post.return_value = MockResponse(201)

        zone_manager = ZoneManager(mock_engine)
        await zone_manager._create_zone("test_unblocker", "unblocker")

        # Verify the POST was called with correct payload
        mock_engine.post.assert_called_once()
        call_args = mock_engine.post.call_args
        assert call_args[0][0] == "/zone"
        payload = call_args[1]["json_data"]
        assert payload["zone"]["name"] == "test_unblocker"
        assert payload["zone"]["type"] == "unblocker"
        assert payload["plan"]["type"] == "unblocker"

    @pytest.mark.asyncio
    async def test_create_serp_zone_success(self, mock_engine):
        """Test creating a SERP zone successfully."""
        mock_engine.post.return_value = MockResponse(200)

        zone_manager = ZoneManager(mock_engine)
        await zone_manager._create_zone("test_serp", "serp")

        # Verify the POST was called with correct payload
        call_args = mock_engine.post.call_args
        payload = call_args[1]["json_data"]
        assert payload["zone"]["name"] == "test_serp"
        assert payload["zone"]["type"] == "serp"
        assert payload["plan"]["type"] == "unblocker"
        assert payload["plan"]["serp"] is True

    @pytest.mark.asyncio
    async def test_create_browser_zone_success(self, mock_engine):
        """Test creating a browser zone successfully."""
        mock_engine.post.return_value = MockResponse(201)

        zone_manager = ZoneManager(mock_engine)
        await zone_manager._create_zone("test_browser", "browser")

        call_args = mock_engine.post.call_args
        payload = call_args[1]["json_data"]
        assert payload["zone"]["name"] == "test_browser"
        assert payload["zone"]["type"] == "browser"
        assert payload["plan"]["type"] == "browser"

    @pytest.mark.asyncio
    async def test_create_zone_already_exists_409(self, mock_engine):
        """Test creating a zone that already exists (409)."""
        mock_engine.post.return_value = MockResponse(409, text_data="Conflict")

        zone_manager = ZoneManager(mock_engine)
        # Should not raise an exception
        await zone_manager._create_zone("existing_zone", "unblocker")

    @pytest.mark.asyncio
    async def test_create_zone_already_exists_message(self, mock_engine):
        """Test creating a zone with duplicate message in response."""
        mock_engine.post.return_value = MockResponse(400, text_data="Zone already exists")

        zone_manager = ZoneManager(mock_engine)
        # Should not raise an exception
        await zone_manager._create_zone("existing_zone", "unblocker")

    @pytest.mark.asyncio
    async def test_create_zone_duplicate_message(self, mock_engine):
        """Test creating a zone with duplicate name error."""
        mock_engine.post.return_value = MockResponse(400, text_data="Duplicate zone name")

        zone_manager = ZoneManager(mock_engine)
        # Should not raise an exception
        await zone_manager._create_zone("duplicate_zone", "unblocker")

    @pytest.mark.asyncio
    async def test_create_zone_auth_error_401(self, mock_engine):
        """Test zone creation with authentication error."""
        mock_engine.post.return_value = MockResponse(401, text_data="Unauthorized")

        zone_manager = ZoneManager(mock_engine)
        with pytest.raises(AuthenticationError) as exc_info:
            await zone_manager._create_zone("test_zone", "unblocker")

        assert "401" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_zone_auth_error_403(self, mock_engine):
        """Test zone creation with forbidden error."""
        mock_engine.post.return_value = MockResponse(403, text_data="Forbidden")

        zone_manager = ZoneManager(mock_engine)
        with pytest.raises(AuthenticationError) as exc_info:
            await zone_manager._create_zone("test_zone", "unblocker")

        assert "403" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_zone_bad_request(self, mock_engine):
        """Test zone creation with bad request error."""
        mock_engine.post.return_value = MockResponse(400, text_data="Invalid zone configuration")

        zone_manager = ZoneManager(mock_engine)
        with pytest.raises(ZoneError) as exc_info:
            await zone_manager._create_zone("test_zone", "unblocker")

        assert "400" in str(exc_info.value)
        assert "Invalid zone configuration" in str(exc_info.value)


class TestZoneManagerEnsureZones:
    """Tests for ensuring zones exist."""

    @pytest.mark.asyncio
    async def test_ensure_zones_all_exist(self, mock_engine):
        """Test ensuring zones when all already exist."""
        zones_data = [
            {"name": "sdk_unlocker", "type": "unblocker"},
            {"name": "sdk_serp", "type": "serp"},
        ]
        mock_engine.get.return_value = MockResponse(200, json_data=zones_data)

        zone_manager = ZoneManager(mock_engine)
        await zone_manager.ensure_required_zones(
            web_unlocker_zone="sdk_unlocker", serp_zone="sdk_serp"
        )

        # Should only call GET to list zones, not POST to create
        mock_engine.get.assert_called()
        mock_engine.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_zones_create_missing(self, mock_engine):
        """Test ensuring zones when some need to be created."""
        # First call: existing zones (empty)
        # After creation: zones exist
        mock_engine.get.side_effect = [
            MockResponse(200, json_data=[]),  # Initial list
            MockResponse(
                200,
                json_data=[  # Verification list
                    {"name": "sdk_unlocker", "type": "unblocker"},
                    {"name": "sdk_serp", "type": "serp"},
                ],
            ),
        ]
        mock_engine.post.return_value = MockResponse(201)

        zone_manager = ZoneManager(mock_engine)
        await zone_manager.ensure_required_zones(
            web_unlocker_zone="sdk_unlocker", serp_zone="sdk_serp"
        )

        # Should create both zones
        assert mock_engine.post.call_count == 2

    @pytest.mark.asyncio
    async def test_ensure_zones_only_web_unlocker(self, mock_engine):
        """Test ensuring only web unlocker zone."""
        mock_engine.get.side_effect = [
            MockResponse(200, json_data=[]),
            MockResponse(200, json_data=[{"name": "sdk_unlocker"}]),
        ]
        mock_engine.post.return_value = MockResponse(201)

        zone_manager = ZoneManager(mock_engine)
        await zone_manager.ensure_required_zones(web_unlocker_zone="sdk_unlocker")

        # Should only create web unlocker zone
        assert mock_engine.post.call_count == 1

    @pytest.mark.asyncio
    async def test_ensure_zones_with_browser(self, mock_engine):
        """Test ensuring unblocker and SERP zones (browser zones NOT auto-created)."""
        mock_engine.get.side_effect = [
            MockResponse(200, json_data=[]),
            MockResponse(200, json_data=[{"name": "sdk_unlocker"}, {"name": "sdk_serp"}]),
        ]
        mock_engine.post.return_value = MockResponse(201)

        zone_manager = ZoneManager(mock_engine)
        await zone_manager.ensure_required_zones(
            web_unlocker_zone="sdk_unlocker",
            serp_zone="sdk_serp",
            browser_zone="sdk_browser",  # This is passed but NOT created (by design)
        )

        # Should only create unblocker + SERP zones (browser zones require manual setup)
        assert mock_engine.post.call_count == 2

    @pytest.mark.asyncio
    async def test_ensure_zones_verification_fails(self, mock_engine, caplog):
        """Test zone creation when verification fails (logs warning but doesn't raise)."""
        # Zones never appear in verification (max_attempts = 5, so need 6 total responses)
        mock_engine.get.side_effect = [
            MockResponse(200, json_data=[]),  # Initial list
            MockResponse(200, json_data=[]),  # Verification attempt 1
            MockResponse(200, json_data=[]),  # Verification attempt 2
            MockResponse(200, json_data=[]),  # Verification attempt 3
            MockResponse(200, json_data=[]),  # Verification attempt 4
            MockResponse(200, json_data=[]),  # Verification attempt 5 (final)
        ]
        mock_engine.post.return_value = MockResponse(201)

        zone_manager = ZoneManager(mock_engine)
        # Verification failure should log warning but NOT raise exception
        await zone_manager.ensure_required_zones(web_unlocker_zone="sdk_unlocker")

        # Should have logged warning about verification failure
        assert any("Zone verification failed" in record.message for record in caplog.records)


class TestZoneManagerIntegration:
    """Integration-style tests for ZoneManager."""

    @pytest.mark.asyncio
    async def test_full_workflow_no_zones_to_create(self, mock_engine):
        """Test full workflow when zones already exist."""
        zones_data = [{"name": "my_zone", "type": "unblocker", "status": "active"}]
        mock_engine.get.return_value = MockResponse(200, json_data=zones_data)

        zone_manager = ZoneManager(mock_engine)

        # List zones
        zones = await zone_manager.list_zones()
        assert len(zones) == 1
        assert zones[0]["name"] == "my_zone"

        # Ensure zones (should not create any)
        await zone_manager.ensure_required_zones(web_unlocker_zone="my_zone")
        mock_engine.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_full_workflow_create_zones(self, mock_engine):
        """Test full workflow creating new zones."""
        zones_after = [{"name": "new_zone", "type": "unblocker"}]
        mock_engine.get.side_effect = [
            MockResponse(200, json_data=[]),  # Initial list (empty)
            MockResponse(200, json_data=zones_after),  # After creation (verification)
            MockResponse(200, json_data=zones_after),  # List zones again
        ]
        mock_engine.post.return_value = MockResponse(201)

        zone_manager = ZoneManager(mock_engine)

        # Ensure zones (should create)
        await zone_manager.ensure_required_zones(web_unlocker_zone="new_zone")

        # Verify zone was created
        assert mock_engine.post.call_count == 1

        # List zones again
        zones = await zone_manager.list_zones()
        assert len(zones) == 1
        assert zones[0]["name"] == "new_zone"
