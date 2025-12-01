"""Unit tests for base scraper and platform scrapers."""

import pytest
from unittest.mock import patch
from brightdata.scrapers import (
    BaseWebScraper,
    AmazonScraper,
    LinkedInScraper,
    ChatGPTScraper,
    register,
    get_scraper_for,
    get_registered_platforms,
    is_platform_supported,
)
from brightdata.exceptions import ValidationError


class TestBaseWebScraper:
    """Test BaseWebScraper abstract base class."""

    def test_base_scraper_requires_dataset_id(self):
        """Test base scraper requires DATASET_ID to be defined."""

        class TestScraper(BaseWebScraper):
            # Missing DATASET_ID
            pass

        with pytest.raises(NotImplementedError) as exc_info:
            TestScraper(bearer_token="test_token_123456789")

        assert "DATASET_ID" in str(exc_info.value)

    def test_base_scraper_requires_token(self):
        """Test base scraper requires bearer token."""

        class TestScraper(BaseWebScraper):
            DATASET_ID = "test_dataset_123"

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                TestScraper()

            assert "token" in str(exc_info.value).lower()

    def test_base_scraper_accepts_token_from_env(self):
        """Test base scraper loads token from environment."""

        class TestScraper(BaseWebScraper):
            DATASET_ID = "test_dataset_123"
            PLATFORM_NAME = "test"

        with patch.dict("os.environ", {"BRIGHTDATA_API_TOKEN": "env_token_123456789"}):
            scraper = TestScraper()
            assert scraper.bearer_token == "env_token_123456789"

    def test_base_scraper_has_required_attributes(self):
        """Test base scraper has all required class attributes."""

        class TestScraper(BaseWebScraper):
            DATASET_ID = "test_123"
            PLATFORM_NAME = "test"

        scraper = TestScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "DATASET_ID")
        assert hasattr(scraper, "PLATFORM_NAME")
        assert hasattr(scraper, "MIN_POLL_TIMEOUT")
        assert hasattr(scraper, "COST_PER_RECORD")
        assert hasattr(scraper, "engine")

    def test_base_scraper_has_scrape_methods(self):
        """Test base scraper has scrape methods."""

        class TestScraper(BaseWebScraper):
            DATASET_ID = "test_123"

        scraper = TestScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "scrape")
        assert hasattr(scraper, "scrape_async")
        assert callable(scraper.scrape)
        assert callable(scraper.scrape_async)

    def test_base_scraper_has_normalize_result_method(self):
        """Test base scraper has normalize_result method."""

        class TestScraper(BaseWebScraper):
            DATASET_ID = "test_123"

        scraper = TestScraper(bearer_token="test_token_123456789")

        # Should return data as-is by default
        test_data = {"key": "value"}
        normalized = scraper.normalize_result(test_data)
        assert normalized == test_data

    def test_base_scraper_repr(self):
        """Test base scraper string representation."""

        class TestScraper(BaseWebScraper):
            DATASET_ID = "test_dataset_123"
            PLATFORM_NAME = "testplatform"

        scraper = TestScraper(bearer_token="test_token_123456789")
        repr_str = repr(scraper)

        assert "testplatform" in repr_str.lower()
        assert "test_dataset_123" in repr_str


class TestRegistryPattern:
    """Test registry pattern and auto-discovery."""

    def test_register_decorator_works(self):
        """Test @register decorator adds scraper to registry."""

        @register("testplatform")
        class TestScraper(BaseWebScraper):
            DATASET_ID = "test_123"
            PLATFORM_NAME = "testplatform"

        # Should be in registry
        scraper_class = get_scraper_for("https://testplatform.com/page")
        assert scraper_class is TestScraper

    def test_get_scraper_for_amazon_url(self):
        """Test get_scraper_for returns AmazonScraper for Amazon URLs."""
        scraper_class = get_scraper_for("https://www.amazon.com/dp/B123")
        assert scraper_class is AmazonScraper

    def test_get_scraper_for_linkedin_url(self):
        """Test get_scraper_for returns LinkedInScraper for LinkedIn URLs."""
        scraper_class = get_scraper_for("https://linkedin.com/in/johndoe")
        assert scraper_class is LinkedInScraper

    def test_get_scraper_for_chatgpt_url(self):
        """Test get_scraper_for returns ChatGPTScraper for ChatGPT URLs."""
        scraper_class = get_scraper_for("https://chatgpt.com/c/abc123")
        assert scraper_class is ChatGPTScraper

    def test_get_scraper_for_unknown_domain_returns_none(self):
        """Test get_scraper_for returns None for unknown domains."""
        scraper_class = get_scraper_for("https://unknown-domain-xyz.com/page")
        assert scraper_class is None

    def test_get_registered_platforms(self):
        """Test get_registered_platforms returns all registered platforms."""
        platforms = get_registered_platforms()

        assert isinstance(platforms, list)
        assert "amazon" in platforms
        assert "linkedin" in platforms
        assert "chatgpt" in platforms

    def test_is_platform_supported_for_known_platform(self):
        """Test is_platform_supported returns True for known platforms."""
        assert is_platform_supported("https://amazon.com/dp/B123") is True
        assert is_platform_supported("https://linkedin.com/in/john") is True

    def test_is_platform_supported_for_unknown_platform(self):
        """Test is_platform_supported returns False for unknown platforms."""
        assert is_platform_supported("https://unknown.com/page") is False


class TestAmazonScraper:
    """Test AmazonScraper platform-specific features."""

    def test_amazon_scraper_has_correct_attributes(self):
        """Test AmazonScraper has correct dataset ID and platform name."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")

        assert scraper.PLATFORM_NAME == "amazon"
        assert scraper.DATASET_ID == "gd_l7q7dkf244hwjntr0"
        assert scraper.MIN_POLL_TIMEOUT == 240
        assert scraper.COST_PER_RECORD == 0.001  # Uses DEFAULT_COST_PER_RECORD

    def test_amazon_scraper_has_products_method(self):
        """Test AmazonScraper has products search method."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "products")
        assert hasattr(scraper, "products_async")
        assert callable(scraper.products)

    def test_amazon_scraper_has_reviews_method(self):
        """Test AmazonScraper has reviews method."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "reviews")
        assert hasattr(scraper, "reviews_async")
        assert callable(scraper.reviews)

    def test_amazon_scraper_registered_in_registry(self):
        """Test AmazonScraper is registered for 'amazon' domain."""
        scraper_class = get_scraper_for("https://amazon.com/dp/B123")
        assert scraper_class is AmazonScraper


class TestLinkedInScraper:
    """Test LinkedInScraper platform-specific features."""

    def test_linkedin_scraper_has_correct_attributes(self):
        """Test LinkedInScraper has correct dataset IDs."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert scraper.PLATFORM_NAME == "linkedin"
        assert scraper.DATASET_ID.startswith("gd_")  # People profiles
        assert hasattr(scraper, "DATASET_ID_COMPANIES")
        assert hasattr(scraper, "DATASET_ID_JOBS")

    def test_linkedin_scraper_has_profiles_method(self):
        """Test LinkedInScraper has profiles search method."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "profiles")
        assert hasattr(scraper, "profiles_async")
        assert callable(scraper.profiles)

    def test_linkedin_scraper_has_companies_method(self):
        """Test LinkedInScraper has companies search method."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "companies")
        assert hasattr(scraper, "companies_async")
        assert callable(scraper.companies)

    def test_linkedin_scraper_has_jobs_method(self):
        """Test LinkedInScraper has jobs search method."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "jobs")
        assert hasattr(scraper, "jobs_async")
        assert callable(scraper.jobs)

    def test_linkedin_scraper_registered_in_registry(self):
        """Test LinkedInScraper is registered for 'linkedin' domain."""
        scraper_class = get_scraper_for("https://linkedin.com/in/john")
        assert scraper_class is LinkedInScraper


class TestChatGPTScraper:
    """Test ChatGPTScraper platform-specific features."""

    def test_chatgpt_scraper_has_correct_attributes(self):
        """Test ChatGPTScraper has correct dataset ID."""
        scraper = ChatGPTScraper(bearer_token="test_token_123456789")

        assert scraper.PLATFORM_NAME == "chatgpt"
        assert scraper.DATASET_ID.startswith("gd_")

    def test_chatgpt_scraper_has_prompt_method(self):
        """Test ChatGPTScraper has prompt method."""
        scraper = ChatGPTScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "prompt")
        assert hasattr(scraper, "prompt_async")
        assert callable(scraper.prompt)

    def test_chatgpt_scraper_has_prompts_method(self):
        """Test ChatGPTScraper has prompts (batch) method."""
        scraper = ChatGPTScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "prompts")
        assert hasattr(scraper, "prompts_async")
        assert callable(scraper.prompts)

    def test_chatgpt_scraper_scrape_raises_not_implemented(self):
        """Test ChatGPTScraper raises NotImplementedError for scrape()."""
        scraper = ChatGPTScraper(bearer_token="test_token_123456789")

        with pytest.raises(NotImplementedError) as exc_info:
            scraper.scrape("https://chatgpt.com/")

        assert "doesn't support URL-based scraping" in str(exc_info.value)
        assert "Use prompt()" in str(exc_info.value)

    def test_chatgpt_scraper_registered_in_registry(self):
        """Test ChatGPTScraper is registered for 'chatgpt' domain."""
        scraper_class = get_scraper_for("https://chatgpt.com/c/123")
        assert scraper_class is ChatGPTScraper


class TestScrapeVsSearchDistinction:
    """Test clear distinction between scrape and search methods."""

    def test_scrape_methods_are_url_based(self):
        """Test scrape() methods accept URLs."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")

        # scrape() should accept URL
        assert hasattr(scraper, "scrape")
        # Method signature should accept urls parameter
        import inspect

        sig = inspect.signature(scraper.scrape)
        assert "urls" in sig.parameters

    def test_search_methods_are_parameter_based(self):
        """Test search methods (discovery) accept keywords/parameters."""
        # Search methods are in search services, not scrapers
        # Scrapers are now URL-based only per API spec

        from brightdata.scrapers.linkedin import LinkedInSearchScraper

        linkedin_search = LinkedInSearchScraper(bearer_token="test_token_123456789")

        import inspect

        # LinkedIn search jobs() should accept keyword (parameter-based discovery)
        jobs_sig = inspect.signature(linkedin_search.jobs)
        assert "keyword" in jobs_sig.parameters

        # LinkedIn search profiles() should accept firstName (parameter-based discovery)
        profiles_sig = inspect.signature(linkedin_search.profiles)
        assert "firstName" in profiles_sig.parameters

        # LinkedIn search posts() should accept profile_url (parameter-based discovery)
        posts_sig = inspect.signature(linkedin_search.posts)
        assert "profile_url" in posts_sig.parameters

    def test_all_platform_scrapers_have_scrape(self):
        """Test all platform scrapers have scrape() method."""
        scrapers = [
            AmazonScraper(bearer_token="test_token_123456789"),
            LinkedInScraper(bearer_token="test_token_123456789"),
            # ChatGPT is exception - it overrides to raise NotImplementedError
        ]

        for scraper in scrapers:
            assert hasattr(scraper, "scrape")
            assert callable(scraper.scrape)

    def test_platforms_have_consistent_async_sync_pairs(self):
        """Test all methods have async/sync pairs."""
        amazon = AmazonScraper(bearer_token="test_token_123456789")
        linkedin = LinkedInScraper(bearer_token="test_token_123456789")

        # Amazon - all URL-based scrape methods
        assert hasattr(amazon, "products") and hasattr(amazon, "products_async")
        assert hasattr(amazon, "reviews") and hasattr(amazon, "reviews_async")
        assert hasattr(amazon, "sellers") and hasattr(amazon, "sellers_async")

        # LinkedIn - URL-based scrape methods
        assert hasattr(linkedin, "posts") and hasattr(linkedin, "posts_async")
        assert hasattr(linkedin, "jobs") and hasattr(linkedin, "jobs_async")
        assert hasattr(linkedin, "profiles") and hasattr(linkedin, "profiles_async")
        assert hasattr(linkedin, "companies") and hasattr(linkedin, "companies_async")


class TestClientIntegration:
    """Test scrapers integrate with BrightDataClient."""

    def test_scrapers_accessible_through_client(self):
        """Test scrapers are accessible through client.scrape namespace."""
        from brightdata import BrightDataClient

        client = BrightDataClient(token="test_token_123456789")

        # All scrapers should be accessible
        assert hasattr(client.scrape, "amazon")
        assert hasattr(client.scrape, "linkedin")
        assert hasattr(client.scrape, "chatgpt")
        assert hasattr(client.scrape, "generic")

    def test_client_scraper_access_returns_correct_instances(self):
        """Test client returns correct scraper instances."""
        from brightdata import BrightDataClient

        client = BrightDataClient(token="test_token_123456789")

        amazon = client.scrape.amazon
        assert isinstance(amazon, AmazonScraper)
        assert amazon.PLATFORM_NAME == "amazon"

        linkedin = client.scrape.linkedin
        assert isinstance(linkedin, LinkedInScraper)
        assert linkedin.PLATFORM_NAME == "linkedin"

        chatgpt = client.scrape.chatgpt
        assert isinstance(chatgpt, ChatGPTScraper)
        assert chatgpt.PLATFORM_NAME == "chatgpt"

    def test_client_passes_token_to_scrapers(self):
        """Test client passes its token to scraper instances."""
        from brightdata import BrightDataClient

        token = "test_token_123456789"
        client = BrightDataClient(token=token)

        amazon = client.scrape.amazon
        assert amazon.bearer_token == token


class TestInterfaceConsistency:
    """Test interface consistency across platforms."""

    def test_amazon_interface_matches_spec(self):
        """Test Amazon scraper matches interface specification."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")

        # URL-based scraping
        assert hasattr(scraper, "scrape")

        # Parameter-based search
        assert hasattr(scraper, "products")
        assert hasattr(scraper, "reviews")

    def test_linkedin_interface_matches_spec(self):
        """Test LinkedIn scraper matches interface specification."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        # URL-based scraping
        assert hasattr(scraper, "scrape")

        # Parameter-based search
        assert hasattr(scraper, "profiles")
        assert hasattr(scraper, "companies")
        assert hasattr(scraper, "jobs")

    def test_chatgpt_interface_matches_spec(self):
        """Test ChatGPT scraper matches interface specification."""
        scraper = ChatGPTScraper(bearer_token="test_token_123456789")

        # Prompt-based (ChatGPT specific)
        assert hasattr(scraper, "prompt")
        assert hasattr(scraper, "prompts")

        # scrape() should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            scraper.scrape("https://chatgpt.com/")


class TestPhilosophicalPrinciples:
    """Test scrapers follow philosophical principles."""

    def test_platforms_feel_familiar(self):
        """Test platforms have similar interfaces (familiarity)."""
        amazon = AmazonScraper(bearer_token="test_token_123456789")
        linkedin = LinkedInScraper(bearer_token="test_token_123456789")

        # Both should have scrape() method
        assert hasattr(amazon, "scrape")
        assert hasattr(linkedin, "scrape")

        # Both should have async/sync pairs
        assert hasattr(amazon, "scrape_async")
        assert hasattr(linkedin, "scrape_async")

    def test_scrape_vs_search_is_clear(self):
        """Test scrape vs search distinction is clear."""
        amazon = AmazonScraper(bearer_token="test_token_123456789")

        import inspect

        # Amazon products() is now URL-based scraping (not search)
        products_sig = inspect.signature(amazon.products)
        assert "url" in products_sig.parameters
        assert "sync" not in products_sig.parameters  # sync parameter was removed

        # For search methods, check LinkedInSearchScraper
        from brightdata.scrapers.linkedin import LinkedInSearchScraper

        linkedin_search = LinkedInSearchScraper(bearer_token="test_token_123456789")

        # Search jobs() signature = parameter-based (has keyword, not url required)
        jobs_sig = inspect.signature(linkedin_search.jobs)
        assert "keyword" in jobs_sig.parameters

    def test_architecture_supports_future_auto_routing(self):
        """Test architecture is ready for future auto-routing."""
        # Registry pattern enables auto-routing
        amazon_url = "https://amazon.com/dp/B123"
        scraper_class = get_scraper_for(amazon_url)

        assert scraper_class is not None
        assert scraper_class is AmazonScraper

        # This enables future: client.scrape.auto(url)
        # The infrastructure is in place!
