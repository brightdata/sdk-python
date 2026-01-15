"""Unit tests for Instagram scraper."""

from brightdata import BrightDataClient
from brightdata.scrapers.instagram import InstagramScraper, InstagramSearchScraper


class TestInstagramScraperURLBased:
    """Test Instagram scraper (URL-based extraction)."""

    def test_instagram_scraper_has_profiles_method(self):
        """Test Instagram scraper has profiles method (async-first API)."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "profiles")
        assert callable(scraper.profiles)

    def test_instagram_scraper_has_posts_method(self):
        """Test Instagram scraper has posts method (async-first API)."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "posts")
        assert callable(scraper.posts)

    def test_instagram_scraper_has_comments_method(self):
        """Test Instagram scraper has comments method (async-first API)."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "comments")
        assert callable(scraper.comments)

    def test_instagram_scraper_has_reels_method(self):
        """Test Instagram scraper has reels method (async-first API)."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "reels")
        assert callable(scraper.reels)

    def test_profiles_method_signature(self):
        """Test profiles method has correct signature."""
        import inspect

        scraper = InstagramScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.profiles)

        # Required: url parameter
        assert "url" in sig.parameters
        assert "timeout" in sig.parameters

        # Defaults
        assert sig.parameters["timeout"].default == 240

    def test_posts_method_signature(self):
        """Test posts method has correct signature."""
        import inspect

        scraper = InstagramScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts)

        assert "url" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 240

    def test_comments_method_signature(self):
        """Test comments method has correct signature."""
        import inspect

        scraper = InstagramScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.comments)

        assert "url" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 240

    def test_reels_method_signature(self):
        """Test reels method has correct signature."""
        import inspect

        scraper = InstagramScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reels)

        assert "url" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 240


class TestInstagramSearchScraper:
    """Test Instagram search scraper (parameter-based discovery)."""

    def test_instagram_search_scraper_has_posts_method(self):
        """Test Instagram search scraper has posts method (async-first API)."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "posts")
        assert callable(scraper.posts)

    def test_instagram_search_scraper_has_reels_method(self):
        """Test Instagram search scraper has reels method (async-first API)."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "reels")
        assert callable(scraper.reels)

    def test_search_posts_method_signature(self):
        """Test search posts method has correct signature."""
        import inspect

        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts)

        # Required: url parameter
        assert "url" in sig.parameters

        # Optional filters
        assert "num_of_posts" in sig.parameters
        assert "posts_to_not_include" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "post_type" in sig.parameters
        assert "timeout" in sig.parameters

        # Defaults
        assert sig.parameters["timeout"].default == 240

    def test_search_reels_method_signature(self):
        """Test search reels method has correct signature."""
        import inspect

        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reels)

        assert "url" in sig.parameters
        assert "num_of_posts" in sig.parameters
        assert "posts_to_not_include" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 240


class TestInstagramDatasetIDs:
    """Test Instagram has correct dataset IDs."""

    def test_scraper_has_all_dataset_ids(self):
        """Test scraper has dataset IDs for all types."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert scraper.DATASET_ID  # Default: Profiles
        assert scraper.DATASET_ID_PROFILES
        assert scraper.DATASET_ID_POSTS
        assert scraper.DATASET_ID_COMMENTS
        assert scraper.DATASET_ID_REELS

        # All should start with gd_
        assert scraper.DATASET_ID.startswith("gd_")
        assert scraper.DATASET_ID_PROFILES.startswith("gd_")
        assert scraper.DATASET_ID_POSTS.startswith("gd_")
        assert scraper.DATASET_ID_COMMENTS.startswith("gd_")
        assert scraper.DATASET_ID_REELS.startswith("gd_")

    def test_search_scraper_has_dataset_ids(self):
        """Test search scraper has dataset IDs."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert scraper.DATASET_ID_POSTS_DISCOVER
        assert scraper.DATASET_ID_REELS_DISCOVER

        assert scraper.DATASET_ID_POSTS_DISCOVER.startswith("gd_")
        assert scraper.DATASET_ID_REELS_DISCOVER.startswith("gd_")

    def test_scraper_has_platform_name(self):
        """Test scraper has correct platform name."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert scraper.PLATFORM_NAME == "instagram"

    def test_scraper_has_cost_per_record(self):
        """Test scraper has cost per record."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "COST_PER_RECORD")
        assert isinstance(scraper.COST_PER_RECORD, (int, float))
        assert scraper.COST_PER_RECORD > 0


class TestInstagramScraperRegistration:
    """Test Instagram scraper is registered correctly."""

    def test_instagram_is_registered(self):
        """Test Instagram scraper is in registry."""
        from brightdata.scrapers.registry import is_platform_supported, get_registered_platforms

        assert is_platform_supported("instagram")
        assert "instagram" in get_registered_platforms()

    def test_can_get_instagram_scraper_from_registry(self):
        """Test can get Instagram scraper from registry."""
        from brightdata.scrapers.registry import get_scraper_for

        scraper_class = get_scraper_for("instagram")
        assert scraper_class is not None
        assert scraper_class.__name__ == "InstagramScraper"


class TestInstagramClientIntegration:
    """Test Instagram scraper integration with BrightDataClient."""

    def test_client_has_instagram_scraper_access(self):
        """Test client provides access to Instagram scraper."""
        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client, "scrape")
        assert hasattr(client.scrape, "instagram")

    def test_client_instagram_scraper_has_all_methods(self):
        """Test client.scrape.instagram has all Instagram methods."""
        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client.scrape.instagram, "profiles")
        assert hasattr(client.scrape.instagram, "posts")
        assert hasattr(client.scrape.instagram, "comments")
        assert hasattr(client.scrape.instagram, "reels")

    def test_instagram_scraper_instance_from_client(self):
        """Test Instagram scraper instance is InstagramScraper."""
        client = BrightDataClient(token="test_token_123456789")

        assert isinstance(client.scrape.instagram, InstagramScraper)

    def test_client_has_instagram_search_access(self):
        """Test client provides access to Instagram search."""
        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client, "search")
        assert hasattr(client.search, "instagram")

    def test_client_instagram_search_has_methods(self):
        """Test client.search.instagram has discovery methods."""
        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client.search.instagram, "posts")
        assert hasattr(client.search.instagram, "reels")

    def test_instagram_search_instance_from_client(self):
        """Test Instagram search instance is InstagramSearchScraper."""
        client = BrightDataClient(token="test_token_123456789")

        assert isinstance(client.search.instagram, InstagramSearchScraper)


class TestInstagramScraperConfiguration:
    """Test Instagram scraper configuration."""

    def test_scraper_initialization_with_token(self):
        """Test scraper can be initialized with bearer token."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert scraper.bearer_token == "test_token_123456789"

    def test_search_scraper_initialization_with_token(self):
        """Test search scraper can be initialized with bearer token."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert scraper.bearer_token == "test_token_123456789"

    def test_scraper_has_engine(self):
        """Test scraper has engine instance."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "engine")
        assert scraper.engine is not None

    def test_search_scraper_has_engine(self):
        """Test search scraper has engine instance."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "engine")
        assert scraper.engine is not None

    def test_scraper_has_api_client(self):
        """Test scraper has API client."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "api_client")
        assert scraper.api_client is not None

    def test_scraper_has_workflow_executor(self):
        """Test scraper has workflow executor."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "workflow_executor")
        assert scraper.workflow_executor is not None


class TestInstagramScraperExports:
    """Test Instagram scraper is properly exported."""

    def test_instagram_scraper_in_module_exports(self):
        """Test InstagramScraper is in scrapers module __all__."""
        from brightdata import scrapers

        assert "InstagramScraper" in scrapers.__all__

    def test_instagram_search_scraper_in_module_exports(self):
        """Test InstagramSearchScraper is in scrapers module __all__."""
        from brightdata import scrapers

        assert "InstagramSearchScraper" in scrapers.__all__

    def test_can_import_instagram_scraper_directly(self):
        """Test can import InstagramScraper directly."""
        from brightdata.scrapers import InstagramScraper as IG

        assert IG is not None
        assert IG.__name__ == "InstagramScraper"

    def test_can_import_instagram_search_scraper_directly(self):
        """Test can import InstagramSearchScraper directly."""
        from brightdata.scrapers import InstagramSearchScraper as IGSearch

        assert IGSearch is not None
        assert IGSearch.__name__ == "InstagramSearchScraper"

    def test_can_import_from_instagram_submodule(self):
        """Test can import from instagram submodule."""
        from brightdata.scrapers.instagram import InstagramScraper as IG
        from brightdata.scrapers.instagram import InstagramSearchScraper as IGSearch

        assert IG is not None
        assert IG.__name__ == "InstagramScraper"
        assert IGSearch is not None
        assert IGSearch.__name__ == "InstagramSearchScraper"


class TestInstagramDiscoverExtraParams:
    """Test Instagram discover endpoints include required extra_params."""

    def test_workflow_executor_execute_accepts_extra_params(self):
        """Test WorkflowExecutor.execute accepts extra_params parameter."""
        import inspect
        from brightdata.scrapers.workflow import WorkflowExecutor

        sig = inspect.signature(WorkflowExecutor.execute)
        assert "extra_params" in sig.parameters

    def test_api_client_trigger_accepts_extra_params(self):
        """Test DatasetAPIClient.trigger accepts extra_params parameter."""
        import inspect
        from brightdata.scrapers.api_client import DatasetAPIClient

        sig = inspect.signature(DatasetAPIClient.trigger)
        assert "extra_params" in sig.parameters

    def test_discover_posts_passes_extra_params(self):
        """Test Instagram search posts passes discovery extra_params to workflow executor."""
        from unittest.mock import AsyncMock, patch

        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        # Mock the workflow executor's execute method
        with patch.object(scraper.workflow_executor, "execute", new_callable=AsyncMock) as mock_execute:
            # Set up mock return value
            from brightdata.models import ScrapeResult

            mock_execute.return_value = ScrapeResult(
                success=True,
                data=[{"test": "data"}],
                platform="instagram",
            )

            # Call the posts method (need to run async)
            import asyncio

            asyncio.run(scraper.posts(url="https://instagram.com/test"))

            # Verify execute was called with extra_params
            mock_execute.assert_called_once()
            call_kwargs = mock_execute.call_args.kwargs
            assert "extra_params" in call_kwargs
            assert call_kwargs["extra_params"] == {"type": "discover_new", "discover_by": "url"}

    def test_discover_reels_passes_extra_params(self):
        """Test Instagram search reels passes discovery extra_params to workflow executor."""
        from unittest.mock import AsyncMock, patch

        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        # Mock the workflow executor's execute method
        with patch.object(scraper.workflow_executor, "execute", new_callable=AsyncMock) as mock_execute:
            # Set up mock return value
            from brightdata.models import ScrapeResult

            mock_execute.return_value = ScrapeResult(
                success=True,
                data=[{"test": "data"}],
                platform="instagram",
            )

            # Call the reels method (need to run async)
            import asyncio

            asyncio.run(scraper.reels(url="https://instagram.com/test"))

            # Verify execute was called with extra_params
            mock_execute.assert_called_once()
            call_kwargs = mock_execute.call_args.kwargs
            assert "extra_params" in call_kwargs
            assert call_kwargs["extra_params"] == {"type": "discover_new", "discover_by": "url"}
