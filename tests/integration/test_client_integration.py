"""Integration tests for BrightDataClient API calls."""

import os
import pytest
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    env_file = Path(__file__).parent.parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

from brightdata import BrightDataClient
from brightdata.exceptions import AuthenticationError


@pytest.fixture
def api_token():
    """Get API token from environment or skip tests."""
    token = os.getenv("BRIGHTDATA_API_TOKEN")
    if not token:
        pytest.skip("API token not found. Set BRIGHTDATA_API_TOKEN to run integration tests.")
    return token


@pytest.fixture
def client(api_token):
    """Create client instance for testing."""
    return BrightDataClient(token=api_token)


@pytest.fixture
async def async_client(api_token):
    """Create async client instance for testing."""
    async with BrightDataClient(token=api_token) as client:
        yield client


class TestConnectionTesting:
    """Test connection testing functionality."""

    @pytest.mark.asyncio
    async def test_connection_with_valid_token(self, async_client):
        """Test connection succeeds with valid token."""
        is_valid = await async_client.test_connection()

        assert is_valid is True
        assert async_client._is_connected is True

    @pytest.mark.asyncio
    async def test_connection_with_invalid_token(self):
        """Test connection returns False with invalid token."""
        client = BrightDataClient(token="invalid_token_123456789", auto_create_zones=False)

        async with client:
            # test_connection() never raises - returns False for invalid tokens
            is_valid = await client.test_connection()
            assert is_valid is False

    def test_connection_sync_with_valid_token(self, client):
        """Test synchronous connection test."""
        is_valid = client.test_connection_sync()

        assert is_valid is True


class TestAccountInfo:
    """Test account information retrieval."""

    @pytest.mark.asyncio
    async def test_get_account_info_success(self, async_client):
        """Test getting account info with valid token."""
        info = await async_client.get_account_info()

        assert isinstance(info, dict)
        assert "zones" in info
        assert "zone_count" in info
        assert "token_valid" in info
        assert "retrieved_at" in info

        assert info["token_valid"] is True
        assert isinstance(info["zones"], list)
        assert info["zone_count"] == len(info["zones"])

    @pytest.mark.asyncio
    async def test_get_account_info_returns_zones(self, async_client):
        """Test account info includes zones list."""
        info = await async_client.get_account_info()

        zones = info.get("zones", [])
        assert isinstance(zones, list)

        # If zones exist, check structure
        if zones:
            for zone in zones:
                assert isinstance(zone, dict)
                # Zones should have at least a name
                assert "name" in zone or "zone" in zone

    @pytest.mark.asyncio
    async def test_get_account_info_with_invalid_token(self):
        """Test getting account info fails with invalid token."""
        client = BrightDataClient(token="invalid_token_123456789", auto_create_zones=False)

        async with client:
            with pytest.raises(AuthenticationError) as exc_info:
                await client.get_account_info()

            assert "Invalid token" in str(exc_info.value) or "401" in str(exc_info.value)

    def test_get_account_info_sync(self, client):
        """Test synchronous account info retrieval."""
        info = client.get_account_info_sync()

        assert isinstance(info, dict)
        assert "zones" in info
        assert "token_valid" in info

    @pytest.mark.asyncio
    async def test_account_info_is_cached(self, async_client):
        """Test account info is cached after first retrieval."""
        # First call
        info1 = await async_client.get_account_info()

        # Second call should return cached version
        info2 = await async_client.get_account_info()

        assert info1 is info2  # Same object reference
        assert info1["retrieved_at"] == info2["retrieved_at"]

    @pytest.mark.asyncio
    async def test_account_info_includes_customer_id(self, api_token):
        """Test account info includes customer ID if provided."""
        customer_id = os.getenv("BRIGHTDATA_CUSTOMER_ID")

        async with BrightDataClient(token=api_token, customer_id=customer_id) as client:
            info = await client.get_account_info()

            if customer_id:
                assert info.get("customer_id") == customer_id


class TestClientInitializationWithValidation:
    """Test client initialization with token validation."""

    def test_client_with_validate_token_true_and_valid_token(self, api_token):
        """Test client initialization validates token when requested."""
        # Should not raise any exception
        client = BrightDataClient(token=api_token, validate_token=True)
        assert client.token == api_token

    def test_client_with_validate_token_true_and_invalid_token(self):
        """Test client raises error on init if token is invalid and validation enabled."""
        with pytest.raises(AuthenticationError):
            BrightDataClient(token="invalid_token_123456789", validate_token=True)

    def test_client_with_validate_token_false_accepts_any_token(self):
        """Test client accepts any token format when validation disabled."""
        # Should not raise exception even with invalid token
        client = BrightDataClient(token="invalid_token_123456789", validate_token=False)
        assert client.token == "invalid_token_123456789"


class TestLegacyAPICompatibility:
    """Test backward compatibility with old flat API."""

    @pytest.mark.asyncio
    async def test_scrape_url_async_works(self, async_client):
        """Test legacy scrape_url_async method works."""
        # Simple test URL
        result = await async_client.scrape_url_async(url="https://httpbin.org/html")

        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "data")

    def test_scrape_url_sync_works(self, client):
        """Test legacy scrape_url method works synchronously."""
        result = client.scrape_url(url="https://httpbin.org/html")

        assert result is not None
        assert hasattr(result, "success")


class TestClientErrorHandling:
    """Test client error handling in various scenarios."""

    @pytest.mark.asyncio
    async def test_connection_test_returns_false_on_network_error(self):
        """Test connection test returns False (not exception) on network errors."""
        client = BrightDataClient(token="test_token_123456789", auto_create_zones=False)

        async with client:
            # Should return False, not raise exception
            is_valid = await client.test_connection()
            # With invalid token, should return False
            assert is_valid is False

    def test_sync_connection_test_returns_false_on_error(self):
        """Test sync connection test returns False on errors."""
        client = BrightDataClient(token="test_token_123456789")

        # Should return False, not raise exception
        is_valid = client.test_connection_sync()
        assert is_valid is False
