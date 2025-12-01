"""Unit tests for BrightDataClient."""

import os
import pytest
from unittest.mock import patch
from brightdata import BrightDataClient, BrightData
from brightdata.exceptions import ValidationError


class TestClientInitialization:
    """Test client initialization and configuration."""

    def test_client_with_explicit_token(self):
        """Test client initialization with explicit token."""
        client = BrightDataClient(token="test_token_123456789")

        assert client.token == "test_token_123456789"
        assert client.timeout == 30  # Default timeout
        assert client.web_unlocker_zone == "sdk_unlocker"
        assert client.serp_zone == "sdk_serp"
        assert client.browser_zone == "sdk_browser"

    def test_client_with_custom_config(self):
        """Test client with custom configuration."""
        client = BrightDataClient(
            token="custom_token_123456789",
            timeout=60,
            web_unlocker_zone="my_unlocker",
            serp_zone="my_serp",
            browser_zone="my_browser",
        )

        assert client.timeout == 60
        assert client.web_unlocker_zone == "my_unlocker"
        assert client.serp_zone == "my_serp"
        assert client.browser_zone == "my_browser"

    def test_client_loads_from_brightdata_api_token(self):
        """Test client loads token from BRIGHTDATA_API_TOKEN."""
        with patch.dict(os.environ, {"BRIGHTDATA_API_TOKEN": "env_token_123456789"}):
            client = BrightDataClient()
            assert client.token == "env_token_123456789"

    def test_client_prioritizes_explicit_token_over_env(self):
        """Test explicit token takes precedence over environment."""
        with patch.dict(os.environ, {"BRIGHTDATA_API_TOKEN": "env_token_123456789"}):
            client = BrightDataClient(token="explicit_token_123456789")
            assert client.token == "explicit_token_123456789"

    def test_client_raises_error_without_token(self):
        """Test client raises ValidationError when no token provided."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                BrightDataClient()

            assert "API token required" in str(exc_info.value)
            assert "BRIGHTDATA_API_TOKEN" in str(exc_info.value)

    def test_client_raises_error_for_invalid_token_format(self):
        """Test client raises ValidationError for invalid token format."""
        with pytest.raises(ValidationError) as exc_info:
            BrightDataClient(token="short")

        assert "Invalid token format" in str(exc_info.value)

    def test_client_raises_error_for_non_string_token(self):
        """Test client raises ValidationError for non-string token."""
        with pytest.raises(ValidationError) as exc_info:
            BrightDataClient(token=12345)

        assert "Invalid token format" in str(exc_info.value)

    def test_client_loads_customer_id_from_env(self):
        """Test client loads customer ID from environment."""
        with patch.dict(
            os.environ,
            {
                "BRIGHTDATA_API_TOKEN": "test_token_123456789",
                "BRIGHTDATA_CUSTOMER_ID": "customer_123",
            },
        ):
            client = BrightDataClient()
            assert client.customer_id == "customer_123"

    def test_client_accepts_customer_id_parameter(self):
        """Test client accepts customer ID as parameter."""
        client = BrightDataClient(token="test_token_123456789", customer_id="explicit_customer_123")
        assert client.customer_id == "explicit_customer_123"


class TestClientTokenManagement:
    """Test token management and validation."""

    def test_token_is_stripped(self):
        """Test token whitespace is stripped."""
        client = BrightDataClient(token="  token_with_spaces_123  ")
        assert client.token == "token_with_spaces_123"

    def test_env_token_is_stripped(self):
        """Test environment token whitespace is stripped."""
        with patch.dict(os.environ, {"BRIGHTDATA_API_TOKEN": "  env_token_123456789  "}):
            client = BrightDataClient()
            assert client.token == "env_token_123456789"


class TestClientServiceProperties:
    """Test hierarchical service access properties."""

    def test_scrape_service_property(self):
        """Test scrape service property returns ScrapeService."""
        client = BrightDataClient(token="test_token_123456789")

        scrape_service = client.scrape
        assert scrape_service is not None

        # All scrapers should now work
        assert scrape_service.generic is not None
        assert scrape_service.amazon is not None
        assert scrape_service.linkedin is not None
        assert scrape_service.chatgpt is not None

    def test_scrape_service_is_cached(self):
        """Test scrape service is cached (returns same instance)."""
        client = BrightDataClient(token="test_token_123456789")

        service1 = client.scrape
        service2 = client.scrape
        assert service1 is service2

    def test_search_service_property(self):
        """Test search service property returns SearchService."""
        client = BrightDataClient(token="test_token_123456789")

        search_service = client.search
        assert search_service is not None

        # All search methods should exist and be callable
        assert callable(search_service.google)
        assert callable(search_service.google_async)
        assert callable(search_service.bing)
        assert callable(search_service.bing_async)
        assert callable(search_service.yandex)
        assert callable(search_service.yandex_async)

    def test_crawler_service_property(self):
        """Test crawler service property returns CrawlerService."""
        client = BrightDataClient(token="test_token_123456789")

        crawler_service = client.crawler
        assert crawler_service is not None
        assert hasattr(crawler_service, "discover")
        assert hasattr(crawler_service, "sitemap")


class TestClientBackwardCompatibility:
    """Test backward compatibility with old API."""

    def test_brightdata_alias_exists(self):
        """Test BrightData alias exists for backward compatibility."""

        client = BrightData(token="test_token_123456789")
        assert isinstance(client, BrightDataClient)

    def test_scrape_url_method_exists(self):
        """Test scrape_url method exists for backward compatibility."""
        client = BrightDataClient(token="test_token_123456789")
        assert hasattr(client, "scrape_url")
        assert hasattr(client, "scrape_url_async")


class TestClientRepr:
    """Test client string representation."""

    def test_repr_shows_token_preview(self):
        """Test __repr__ shows token preview."""
        client = BrightDataClient(token="1234567890abcdefghij")
        repr_str = repr(client)

        assert "BrightDataClient" in repr_str
        assert "1234567890" in repr_str  # First 10 chars
        assert "fghij" in repr_str  # Last 5 chars
        assert "abcde" not in repr_str  # Middle should not be shown

    def test_repr_shows_status(self):
        """Test __repr__ shows connection status."""
        client = BrightDataClient(token="test_token_123456789")
        repr_str = repr(client)

        assert "status" in repr_str.lower()


class TestClientConfiguration:
    """Test client configuration options."""

    def test_auto_create_zones_default_true(self):
        """Test auto_create_zones defaults to True."""
        client = BrightDataClient(token="test_token_123456789")
        assert client.auto_create_zones is True

    def test_auto_create_zones_can_be_enabled(self):
        """Test auto_create_zones can be enabled."""
        client = BrightDataClient(token="test_token_123456789", auto_create_zones=True)
        assert client.auto_create_zones is True

    def test_zones_ensured_flag_starts_false(self):
        """Test _zones_ensured flag starts as False."""
        client = BrightDataClient(token="test_token_123456789")
        assert client._zones_ensured is False

    def test_zone_manager_starts_as_none(self):
        """Test zone manager starts as None."""
        client = BrightDataClient(token="test_token_123456789")
        assert client._zone_manager is None

    def test_default_timeout_is_30(self):
        """Test default timeout is 30 seconds."""
        client = BrightDataClient(token="test_token_123456789")
        assert client.timeout == 30

    def test_custom_timeout_is_respected(self):
        """Test custom timeout is respected."""
        client = BrightDataClient(token="test_token_123456789", timeout=120)
        assert client.timeout == 120


class TestClientErrorMessages:
    """Test client error messages are clear and helpful."""

    def test_missing_token_error_is_helpful(self):
        """Test missing token error provides helpful guidance."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                BrightDataClient()

            error_msg = str(exc_info.value)
            assert "API token required" in error_msg
            assert "BrightDataClient(token=" in error_msg
            assert "BRIGHTDATA_API_TOKEN" in error_msg
            assert "https://brightdata.com" in error_msg

    def test_invalid_token_format_error_is_clear(self):
        """Test invalid token format error is clear."""
        with pytest.raises(ValidationError) as exc_info:
            BrightDataClient(token="bad")

        error_msg = str(exc_info.value)
        assert "Invalid token format" in error_msg
        assert "at least 10 characters" in error_msg


class TestClientContextManager:
    """Test client context manager support."""

    def test_client_supports_async_context_manager(self):
        """Test client supports async context manager protocol."""
        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client, "__aenter__")
        assert hasattr(client, "__aexit__")
        assert callable(client.__aenter__)
        assert callable(client.__aexit__)
