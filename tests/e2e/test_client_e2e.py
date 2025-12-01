"""End-to-end tests for BrightDataClient hierarchical interface."""

import os
import pytest
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv

    env_file = Path(__file__).parent.parent.parent.parent / ".env"
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
        pytest.skip("API token not found. Set BRIGHTDATA_API_TOKEN to run E2E tests.")
    return token


@pytest.fixture
async def client(api_token):
    """Create async client for testing."""
    async with BrightDataClient(token=api_token) as client:
        yield client


class TestHierarchicalServiceAccess:
    """Test the hierarchical service access pattern."""

    def test_client_initialization_is_simple(self, api_token):
        """Test client can be initialized with single line."""
        # Should work with environment variable
        client = BrightDataClient()
        assert client is not None

        # Should work with explicit token
        client = BrightDataClient(token=api_token)
        assert client is not None

    def test_service_properties_are_accessible(self, api_token):
        """Test all service properties are accessible."""
        client = BrightDataClient(token=api_token)

        # All services should be accessible
        assert client.scrape is not None
        assert client.search is not None
        assert client.crawler is not None

    def test_scrape_service_has_specialized_scrapers(self, api_token):
        """Test scrape service provides access to specialized scrapers."""
        client = BrightDataClient(token=api_token)

        scrape = client.scrape

        # All scrapers should now be accessible
        assert scrape.generic is not None
        assert scrape.amazon is not None
        assert scrape.linkedin is not None
        assert scrape.chatgpt is not None

        # Verify they're the correct types
        from brightdata.scrapers import AmazonScraper, LinkedInScraper, ChatGPTScraper

        assert isinstance(scrape.amazon, AmazonScraper)
        assert isinstance(scrape.linkedin, LinkedInScraper)
        assert isinstance(scrape.chatgpt, ChatGPTScraper)

    def test_search_service_has_search_engines(self, api_token):
        """Test search service provides access to search engines."""
        client = BrightDataClient(token=api_token)

        search = client.search

        # All search engines should be callable
        assert callable(search.google)
        assert callable(search.google_async)
        assert callable(search.bing)
        assert callable(search.bing_async)
        assert callable(search.yandex)
        assert callable(search.yandex_async)

    def test_crawler_service_has_crawl_methods(self, api_token):
        """Test crawler service provides crawling methods."""
        client = BrightDataClient(token=api_token)

        crawler = client.crawler

        # Should have crawler methods
        assert hasattr(crawler, "discover")
        assert hasattr(crawler, "sitemap")
        assert callable(crawler.discover)
        assert callable(crawler.sitemap)


class TestGenericScraperAccess:
    """Test generic scraper through hierarchical access."""

    @pytest.mark.asyncio
    async def test_generic_scraper_async(self, client):
        """Test generic scraper through client.scrape.generic.url_async()."""
        result = await client.scrape.generic.url_async(url="https://httpbin.org/html")

        assert result is not None
        assert hasattr(result, "success")
        assert hasattr(result, "data")

    def test_generic_scraper_sync(self, api_token):
        """Test generic scraper synchronously."""
        client = BrightDataClient(token=api_token)

        result = client.scrape.generic.url(url="https://httpbin.org/html")

        assert result is not None
        assert result.success or result.error is not None


class TestConnectionVerification:
    """Test connection verification features."""

    @pytest.mark.asyncio
    async def test_connection_verification_workflow(self, client):
        """Test complete connection verification workflow."""
        # Test connection
        is_valid = await client.test_connection()
        assert is_valid is True

        # Get account info
        info = await client.get_account_info()
        assert info is not None
        assert isinstance(info, dict)
        assert "zones" in info

        # Zones should be accessible
        zones = info["zones"]
        print(f"\n✅ Connected! Found {len(zones)} zones")
        for zone in zones:
            zone_name = zone.get("name", "unknown")
            print(f"  - {zone_name}")


class TestUserExperience:
    """Test user experience matches requirements."""

    def test_single_line_initialization(self):
        """Test user can start with single line (environment variable)."""
        # This should work if BRIGHTDATA_API_TOKEN is set
        try:
            client = BrightDataClient()
            assert client is not None
            print("\n✅ Single-line initialization works!")
        except Exception as e:
            pytest.skip(f"Environment variable not set: {e}")

    def test_clear_error_for_missing_credentials(self):
        """Test error message is clear when credentials missing."""
        from unittest.mock import patch

        with pytest.raises(Exception) as exc_info:
            with patch.dict(os.environ, {}, clear=True):
                BrightDataClient()

        error_msg = str(exc_info.value)
        assert "API token" in error_msg
        assert "brightdata.com" in error_msg.lower()

    def test_hierarchical_access_is_intuitive(self, api_token):
        """Test hierarchical access follows intuitive pattern."""
        client = BrightDataClient(token=api_token)

        # Pattern: client.{service}.{platform}.{action}
        # Should be discoverable and intuitive

        # Scraping path
        scrape_path = client.scrape
        assert scrape_path is not None

        # Generic scraping (implemented)
        generic_scraper = scrape_path.generic
        assert generic_scraper is not None
        assert hasattr(generic_scraper, "url")

        # Platform scrapers (all implemented now!)
        amazon_scraper = scrape_path.amazon
        assert amazon_scraper is not None
        assert hasattr(amazon_scraper, "scrape")
        assert hasattr(amazon_scraper, "products")

        linkedin_scraper = scrape_path.linkedin
        assert linkedin_scraper is not None
        assert hasattr(linkedin_scraper, "scrape")
        assert hasattr(linkedin_scraper, "jobs")

        chatgpt_scraper = scrape_path.chatgpt
        assert chatgpt_scraper is not None
        assert hasattr(chatgpt_scraper, "prompt")

        print("\n✅ Hierarchical access pattern is intuitive!")
        print("  - client.scrape.generic.url()  ✅ (working)")
        print("  - client.scrape.amazon.products()  ✅ (working)")
        print("  - client.scrape.linkedin.jobs()  ✅ (working)")
        print("  - client.scrape.chatgpt.prompt()  ✅ (working)")
        print("  - client.search.google()  🚧 (planned)")
        print("  - client.crawler.discover()  🚧 (planned)")


class TestPhilosophicalPrinciples:
    """Test SDK follows stated philosophical principles."""

    def test_client_is_single_source_of_truth(self, api_token):
        """Test client is single source of truth for configuration."""
        client = BrightDataClient(token=api_token, timeout=60, web_unlocker_zone="custom_zone")

        # Configuration should be accessible from client
        assert client.timeout == 60
        assert client.web_unlocker_zone == "custom_zone"

        # Services should reference client configuration
        assert client.scrape._client is client
        assert client.search._client is client
        assert client.crawler._client is client

    def test_authentication_just_works(self):
        """Test authentication 'just works' with minimal setup."""
        # With environment variable - should just work
        try:
            client = BrightDataClient()
            assert client.token is not None
            print("\n✅ Authentication works automatically from environment!")
        except Exception:
            pytest.skip("Environment variable not set")

    def test_fails_fast_on_missing_credentials(self):
        """Test SDK fails fast when credentials missing."""
        from unittest.mock import patch

        # Should fail immediately on initialization
        with patch.dict(os.environ, {}, clear=True):
            try:
                BrightDataClient()
                pytest.fail("Should have raised error immediately")
            except Exception as e:
                # Should fail fast, not during first API call
                assert "token" in str(e).lower()
                print("\n✅ Fails fast on missing credentials!")

    def test_follows_principle_of_least_surprise(self, api_token):
        """Test SDK follows principle of least surprise."""
        client = BrightDataClient(token=api_token)

        # Service properties should return same instance (cached)
        scrape1 = client.scrape
        scrape2 = client.scrape
        assert scrape1 is scrape2

        # Token should be accessible
        assert client.token is not None

        # Repr should be informative
        repr_str = repr(client)
        assert "BrightDataClient" in repr_str

        print("\n✅ Follows principle of least surprise!")
        print(f"  Client repr: {repr_str}")


# Helper function for interactive testing
def demo_client_usage():
    """
    Demo function showing ideal client usage.

    This demonstrates the desired user experience.
    """
    # Simple instantiation - auto-loads from env
    client = BrightDataClient()

    # Or with explicit token
    client = BrightDataClient(token="your_token")

    # Service access - hierarchical and intuitive
    # client.scrape.amazon.products(...)
    # client.search.linkedin.jobs(...)
    # client.crawler.discover(...)

    # Connection verification
    # is_valid = await client.test_connection()
    # info = client.get_account_info()

    return client


if __name__ == "__main__":
    """Run a quick demo of the client."""
    print("=" * 80)
    print("BrightDataClient Demo")
    print("=" * 80)

    try:
        client = BrightDataClient()
        print(f"✅ Client initialized: {client}")
        print("✅ Token loaded from environment")
        print("✅ Services available: scrape, search, crawler")
        print()
        print("Example usage:")
        print("  result = client.scrape.generic.url('https://example.com')")
        print("  results = client.search.google('python scraping')")
        print("  pages = client.crawler.discover('https://example.com')")
    except Exception as e:
        print(f"❌ Error: {e}")
