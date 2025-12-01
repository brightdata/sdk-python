"""Unit tests for Facebook scraper."""

from brightdata import BrightDataClient
from brightdata.scrapers.facebook import FacebookScraper


class TestFacebookScraperURLBased:
    """Test Facebook scraper (URL-based extraction)."""

    def test_facebook_scraper_has_posts_by_profile_method(self):
        """Test Facebook scraper has posts_by_profile method."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "posts_by_profile")
        assert hasattr(scraper, "posts_by_profile_async")
        assert callable(scraper.posts_by_profile)
        assert callable(scraper.posts_by_profile_async)

    def test_facebook_scraper_has_posts_by_group_method(self):
        """Test Facebook scraper has posts_by_group method."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "posts_by_group")
        assert hasattr(scraper, "posts_by_group_async")
        assert callable(scraper.posts_by_group)
        assert callable(scraper.posts_by_group_async)

    def test_facebook_scraper_has_posts_by_url_method(self):
        """Test Facebook scraper has posts_by_url method."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "posts_by_url")
        assert hasattr(scraper, "posts_by_url_async")
        assert callable(scraper.posts_by_url)
        assert callable(scraper.posts_by_url_async)

    def test_facebook_scraper_has_comments_method(self):
        """Test Facebook scraper has comments method."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "comments")
        assert hasattr(scraper, "comments_async")
        assert callable(scraper.comments)
        assert callable(scraper.comments_async)

    def test_facebook_scraper_has_reels_method(self):
        """Test Facebook scraper has reels method."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "reels")
        assert hasattr(scraper, "reels_async")
        assert callable(scraper.reels)
        assert callable(scraper.reels_async)

    def test_posts_by_profile_method_signature(self):
        """Test posts_by_profile method has correct signature."""
        import inspect

        scraper = FacebookScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts_by_profile)

        # Required: url parameter
        assert "url" in sig.parameters

        # Optional filters
        assert "num_of_posts" in sig.parameters
        assert "posts_to_not_include" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "timeout" in sig.parameters

        # Defaults
        assert sig.parameters["timeout"].default == 240

    def test_posts_by_group_method_signature(self):
        """Test posts_by_group method has correct signature."""
        import inspect

        scraper = FacebookScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts_by_group)

        # Required: url
        assert "url" in sig.parameters

        # Optional filters
        assert "num_of_posts" in sig.parameters
        assert "posts_to_not_include" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "timeout" in sig.parameters

        # Defaults
        assert sig.parameters["timeout"].default == 240

    def test_posts_by_url_method_signature(self):
        """Test posts_by_url method has correct signature."""
        import inspect

        scraper = FacebookScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts_by_url)

        assert "url" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 240

    def test_comments_method_signature(self):
        """Test comments method has correct signature."""
        import inspect

        scraper = FacebookScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.comments)

        assert "url" in sig.parameters
        assert "num_of_comments" in sig.parameters
        assert "comments_to_not_include" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 240

    def test_reels_method_signature(self):
        """Test reels method has correct signature."""
        import inspect

        scraper = FacebookScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reels)

        assert "url" in sig.parameters
        assert "num_of_posts" in sig.parameters
        assert "posts_to_not_include" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 240


class TestFacebookDatasetIDs:
    """Test Facebook has correct dataset IDs."""

    def test_scraper_has_all_dataset_ids(self):
        """Test scraper has dataset IDs for all types."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert scraper.DATASET_ID  # Default: Posts by Profile
        assert scraper.DATASET_ID_POSTS_PROFILE
        assert scraper.DATASET_ID_POSTS_GROUP
        assert scraper.DATASET_ID_POSTS_URL
        assert scraper.DATASET_ID_COMMENTS
        assert scraper.DATASET_ID_REELS

        # All should start with gd_
        assert scraper.DATASET_ID.startswith("gd_")
        assert scraper.DATASET_ID_POSTS_PROFILE.startswith("gd_")
        assert scraper.DATASET_ID_POSTS_GROUP.startswith("gd_")
        assert scraper.DATASET_ID_POSTS_URL.startswith("gd_")
        assert scraper.DATASET_ID_COMMENTS.startswith("gd_")
        assert scraper.DATASET_ID_REELS.startswith("gd_")

    def test_scraper_has_platform_name(self):
        """Test scraper has correct platform name."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert scraper.PLATFORM_NAME == "facebook"

    def test_scraper_has_cost_per_record(self):
        """Test scraper has cost per record."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "COST_PER_RECORD")
        assert isinstance(scraper.COST_PER_RECORD, (int, float))
        assert scraper.COST_PER_RECORD > 0


class TestFacebookScraperRegistration:
    """Test Facebook scraper is registered correctly."""

    def test_facebook_is_registered(self):
        """Test Facebook scraper is in registry."""
        from brightdata.scrapers.registry import is_platform_supported, get_registered_platforms

        assert is_platform_supported("facebook")
        assert "facebook" in get_registered_platforms()

    def test_can_get_facebook_scraper_from_registry(self):
        """Test can get Facebook scraper from registry."""
        from brightdata.scrapers.registry import get_scraper_for

        scraper_class = get_scraper_for("facebook")
        assert scraper_class is not None
        assert scraper_class.__name__ == "FacebookScraper"


class TestFacebookClientIntegration:
    """Test Facebook scraper integration with BrightDataClient."""

    def test_client_has_facebook_scraper_access(self):
        """Test client provides access to Facebook scraper."""
        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client, "scrape")
        assert hasattr(client.scrape, "facebook")

    def test_client_facebook_scraper_has_all_methods(self):
        """Test client.scrape.facebook has all Facebook methods."""
        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client.scrape.facebook, "posts_by_profile")
        assert hasattr(client.scrape.facebook, "posts_by_group")
        assert hasattr(client.scrape.facebook, "posts_by_url")
        assert hasattr(client.scrape.facebook, "comments")
        assert hasattr(client.scrape.facebook, "reels")

    def test_facebook_scraper_instance_from_client(self):
        """Test Facebook scraper instance is FacebookScraper."""
        client = BrightDataClient(token="test_token_123456789")

        assert isinstance(client.scrape.facebook, FacebookScraper)


class TestFacebookScraperConfiguration:
    """Test Facebook scraper configuration."""

    def test_scraper_initialization_with_token(self):
        """Test scraper can be initialized with bearer token."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert scraper.bearer_token == "test_token_123456789"

    def test_scraper_has_engine(self):
        """Test scraper has engine instance."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "engine")
        assert scraper.engine is not None

    def test_scraper_has_api_client(self):
        """Test scraper has API client."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "api_client")
        assert scraper.api_client is not None

    def test_scraper_has_workflow_executor(self):
        """Test scraper has workflow executor."""
        scraper = FacebookScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "workflow_executor")
        assert scraper.workflow_executor is not None


class TestFacebookScraperExports:
    """Test Facebook scraper is properly exported."""

    def test_facebook_scraper_in_module_exports(self):
        """Test FacebookScraper is in scrapers module __all__."""
        from brightdata import scrapers

        assert "FacebookScraper" in scrapers.__all__

    def test_can_import_facebook_scraper_directly(self):
        """Test can import FacebookScraper directly."""
        from brightdata.scrapers import FacebookScraper as FB

        assert FB is not None
        assert FB.__name__ == "FacebookScraper"

    def test_can_import_from_facebook_submodule(self):
        """Test can import from facebook submodule."""
        from brightdata.scrapers.facebook import FacebookScraper as FB

        assert FB is not None
        assert FB.__name__ == "FacebookScraper"
