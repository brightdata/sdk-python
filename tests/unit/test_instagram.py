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

        # Defaults (180s = DEFAULT_TIMEOUT_SHORT, same as LinkedIn)
        assert sig.parameters["timeout"].default == 180

    def test_posts_method_signature(self):
        """Test posts method has correct signature."""
        import inspect

        scraper = InstagramScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts)

        assert "url" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 180

    def test_comments_method_signature(self):
        """Test comments method has correct signature."""
        import inspect

        scraper = InstagramScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.comments)

        assert "url" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 180

    def test_reels_method_signature(self):
        """Test reels method has correct signature."""
        import inspect

        scraper = InstagramScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reels)

        assert "url" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 180


class TestInstagramSearchScraper:
    """Test Instagram search scraper (parameter-based discovery)."""

    def test_instagram_search_scraper_has_profiles_method(self):
        """Test Instagram search scraper has profiles method for username discovery."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "profiles")
        assert callable(scraper.profiles)

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

    def test_instagram_search_scraper_has_reels_all_method(self):
        """Test Instagram search scraper has reels_all method."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "reels_all")
        assert callable(scraper.reels_all)

    def test_search_profiles_method_signature(self):
        """Test search profiles method has correct signature."""
        import inspect

        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.profiles)

        # Required: user_name parameter (NOT url)
        assert "user_name" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 180

    def test_search_posts_method_signature(self):
        """Test search posts method has correct signature."""
        import inspect

        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts)

        # Required: url parameter
        assert "url" in sig.parameters

        # Optional filters
        assert "num_of_posts" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "post_type" in sig.parameters
        assert "posts_to_not_include" in sig.parameters
        assert "timeout" in sig.parameters

        # Defaults (180s = DEFAULT_TIMEOUT_SHORT)
        assert sig.parameters["timeout"].default == 180

    def test_search_reels_method_signature(self):
        """Test search reels method has correct signature."""
        import inspect

        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reels)

        assert "url" in sig.parameters
        assert "num_of_posts" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 180

    def test_search_reels_all_method_signature(self):
        """Test search reels_all method has correct signature."""
        import inspect

        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reels_all)

        assert "url" in sig.parameters
        assert "num_of_posts" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 180


class TestInstagramDatasetIDs:
    """Test Instagram has correct dataset IDs."""

    def test_scraper_has_all_dataset_ids(self):
        """Test scraper has dataset IDs for all types."""
        scraper = InstagramScraper(bearer_token="test_token_123456789")

        assert scraper.DATASET_ID  # Default: Profiles
        assert scraper.DATASET_ID_POSTS
        assert scraper.DATASET_ID_COMMENTS
        assert scraper.DATASET_ID_REELS

        # All should start with gd_
        assert scraper.DATASET_ID.startswith("gd_")
        assert scraper.DATASET_ID_POSTS.startswith("gd_")
        assert scraper.DATASET_ID_COMMENTS.startswith("gd_")
        assert scraper.DATASET_ID_REELS.startswith("gd_")

    def test_search_scraper_has_dataset_ids(self):
        """Test search scraper has dataset IDs."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert scraper.DATASET_ID_PROFILES
        assert scraper.DATASET_ID_POSTS
        assert scraper.DATASET_ID_REELS

        assert scraper.DATASET_ID_PROFILES.startswith("gd_")
        assert scraper.DATASET_ID_POSTS.startswith("gd_")
        assert scraper.DATASET_ID_REELS.startswith("gd_")

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

        assert hasattr(client.search.instagram, "profiles")
        assert hasattr(client.search.instagram, "posts")
        assert hasattr(client.search.instagram, "reels")
        assert hasattr(client.search.instagram, "reels_all")

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


class TestInstagramDiscoveryExtraParams:
    """Test Instagram discovery uses extra_params correctly."""

    def test_search_scraper_has_execute_discovery_method(self):
        """Test search scraper has internal _execute_discovery method."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "_execute_discovery")
        assert callable(scraper._execute_discovery)

    def test_search_scraper_has_context_manager(self):
        """Test search scraper supports async context manager."""
        scraper = InstagramSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "__aenter__")
        assert hasattr(scraper, "__aexit__")
