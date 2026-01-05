"""Unit tests for LinkedIn scraper and search services."""

from brightdata import BrightDataClient
from brightdata.scrapers.linkedin import LinkedInScraper, LinkedInSearchScraper


class TestLinkedInScraperURLBased:
    """Test LinkedIn scraper (URL-based extraction)."""

    def test_linkedin_scraper_has_posts_method(self):
        """Test LinkedIn scraper has posts method (async-first API)."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "posts")
        assert callable(scraper.posts)

    def test_linkedin_scraper_has_jobs_method(self):
        """Test LinkedIn scraper has jobs method (async-first API)."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "jobs")
        assert callable(scraper.jobs)

    def test_linkedin_scraper_has_profiles_method(self):
        """Test LinkedIn scraper has profiles method (async-first API)."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "profiles")
        assert callable(scraper.profiles)

    def test_linkedin_scraper_has_companies_method(self):
        """Test LinkedIn scraper has companies method (async-first API)."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert hasattr(scraper, "companies")
        assert callable(scraper.companies)

    def test_posts_method_signature(self):
        """Test posts method has correct signature."""
        import inspect

        scraper = LinkedInScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts)

        # Required: url parameter
        assert "url" in sig.parameters

        # Optional: sync and timeout
        assert "sync" not in sig.parameters
        assert "timeout" in sig.parameters

        # Defaults
        assert sig.parameters["timeout"].default == 180

    def test_jobs_method_signature(self):
        """Test jobs method has correct signature."""
        import inspect

        scraper = LinkedInScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.jobs)

        assert "url" in sig.parameters
        assert "sync" not in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 180

    def test_profiles_method_signature(self):
        """Test profiles method has correct signature."""
        import inspect

        scraper = LinkedInScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.profiles)

        assert "url" in sig.parameters
        assert "sync" not in sig.parameters
        assert "timeout" in sig.parameters

    def test_companies_method_signature(self):
        """Test companies method has correct signature."""
        import inspect

        scraper = LinkedInScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.companies)

        assert "url" in sig.parameters
        assert "sync" not in sig.parameters
        assert "timeout" in sig.parameters


class TestLinkedInSearchScraper:
    """Test LinkedIn search service (discovery/parameter-based)."""

    def test_linkedin_search_has_posts_method(self):
        """Test LinkedIn search has posts discovery method (async-first API)."""
        search = LinkedInSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(search, "posts")
        assert callable(search.posts)

    def test_linkedin_search_has_profiles_method(self):
        """Test LinkedIn search has profiles discovery method (async-first API)."""
        search = LinkedInSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(search, "profiles")
        assert callable(search.profiles)

    def test_linkedin_search_has_jobs_method(self):
        """Test LinkedIn search has jobs discovery method (async-first API)."""
        search = LinkedInSearchScraper(bearer_token="test_token_123456789")

        assert hasattr(search, "jobs")
        assert callable(search.jobs)

    def test_search_posts_signature(self):
        """Test search.posts has correct signature."""
        import inspect

        search = LinkedInSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(search.posts)

        # Required: profile_url
        assert "profile_url" in sig.parameters

        # Optional: start_date, end_date, timeout
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters
        assert "timeout" in sig.parameters

    def test_search_profiles_signature(self):
        """Test search.profiles has correct signature."""
        import inspect

        search = LinkedInSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(search.profiles)

        # Required: firstName
        assert "firstName" in sig.parameters

        # Optional: lastName, timeout
        assert "lastName" in sig.parameters
        assert "timeout" in sig.parameters

    def test_search_jobs_signature(self):
        """Test search.jobs has correct signature."""
        import inspect

        search = LinkedInSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(search.jobs)

        # All parameters should be present
        params = sig.parameters
        assert "url" in params
        assert "location" in params
        assert "keyword" in params
        assert "country" in params
        assert "timeRange" in params
        assert "jobType" in params
        assert "experienceLevel" in params
        assert "remote" in params
        assert "company" in params
        assert "locationRadius" in params
        assert "timeout" in params


class TestLinkedInDualNamespaces:
    """Test LinkedIn has both scrape and search namespaces."""

    def test_client_has_scrape_linkedin(self):
        """Test client.scrape.linkedin exists."""
        client = BrightDataClient(token="test_token_123456789")

        scraper = client.scrape.linkedin
        assert scraper is not None
        assert isinstance(scraper, LinkedInScraper)

    def test_client_has_search_linkedin(self):
        """Test client.search.linkedin exists."""
        client = BrightDataClient(token="test_token_123456789")

        search = client.search.linkedin
        assert search is not None
        assert isinstance(search, LinkedInSearchScraper)

    def test_scrape_vs_search_distinction(self):
        """Test clear distinction between scrape and search."""
        client = BrightDataClient(token="test_token_123456789")

        scraper = client.scrape.linkedin
        search = client.search.linkedin

        # Scraper uses 'url' parameter
        import inspect

        scraper_sig = inspect.signature(scraper.posts)
        assert "url" in scraper_sig.parameters
        assert "sync" not in scraper_sig.parameters  # sync parameter was removed

        # Search uses platform-specific parameters
        search_sig = inspect.signature(search.posts)
        assert "profile_url" in search_sig.parameters
        assert "start_date" in search_sig.parameters
        assert "url" not in search_sig.parameters  # Different from scraper

    def test_scrape_linkedin_methods_accept_url_list(self):
        """Test scrape.linkedin methods accept url as str | list."""
        import inspect

        client = BrightDataClient(token="test_token_123456789")
        scraper = client.scrape.linkedin

        # Check type hints
        sig = inspect.signature(scraper.posts)
        url_param = sig.parameters["url"]

        # Should accept Union[str, List[str]]
        annotation_str = str(url_param.annotation)
        assert "str" in annotation_str
        assert "List" in annotation_str or "list" in annotation_str


class TestLinkedInDatasetIDs:
    """Test LinkedIn has correct dataset IDs for each type."""

    def test_scraper_has_all_dataset_ids(self):
        """Test scraper has dataset IDs for all types."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        assert scraper.DATASET_ID  # Profiles
        assert scraper.DATASET_ID_COMPANIES
        assert scraper.DATASET_ID_JOBS
        assert scraper.DATASET_ID_POSTS

        # All should start with gd_
        assert scraper.DATASET_ID.startswith("gd_")
        assert scraper.DATASET_ID_COMPANIES.startswith("gd_")
        assert scraper.DATASET_ID_JOBS.startswith("gd_")
        assert scraper.DATASET_ID_POSTS.startswith("gd_")

    def test_search_has_dataset_ids(self):
        """Test search service has dataset IDs."""
        search = LinkedInSearchScraper(bearer_token="test_token_123456789")

        assert search.DATASET_ID_POSTS
        assert search.DATASET_ID_PROFILES
        assert search.DATASET_ID_JOBS


class TestSyncVsAsyncMode:
    """Test sync vs async mode handling."""

    def test_default_timeout_is_correct(self):
        """Test default timeout is 180s for async workflow."""
        import inspect

        scraper = LinkedInScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts)

        assert sig.parameters["timeout"].default == 180

    def test_methods_dont_have_sync_parameter(self):
        """Test all scrape methods don't have sync parameter (standard async pattern)."""
        import inspect

        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        for method_name in ["posts", "jobs", "profiles", "companies"]:
            sig = inspect.signature(getattr(scraper, method_name))
            assert "sync" not in sig.parameters


class TestAPISpecCompliance:
    """Test compliance with exact API specifications."""

    def test_scrape_posts_api_spec(self):
        """Test client.scrape.linkedin.posts matches API spec."""
        client = BrightDataClient(token="test_token_123456789")

        # API Spec: client.scrape.linkedin.posts(url, timeout=180)
        import inspect

        sig = inspect.signature(client.scrape.linkedin.posts)

        assert "url" in sig.parameters
        assert "sync" not in sig.parameters
        assert "timeout" in sig.parameters
        assert sig.parameters["timeout"].default == 180

    def test_search_posts_api_spec(self):
        """Test client.search.linkedin.posts matches API spec."""
        client = BrightDataClient(token="test_token_123456789")

        # API Spec: posts(profile_url, start_date, end_date)
        import inspect

        sig = inspect.signature(client.search.linkedin.posts)

        assert "profile_url" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters

    def test_search_profiles_api_spec(self):
        """Test client.search.linkedin.profiles matches API spec."""
        client = BrightDataClient(token="test_token_123456789")

        # API Spec: profiles(firstName, lastName, timeout)
        import inspect

        sig = inspect.signature(client.search.linkedin.profiles)

        assert "firstName" in sig.parameters
        assert "lastName" in sig.parameters
        assert "timeout" in sig.parameters

    def test_search_jobs_api_spec(self):
        """Test client.search.linkedin.jobs matches API spec."""
        client = BrightDataClient(token="test_token_123456789")

        # API Spec: jobs(url, location, keyword, country, ...)
        import inspect

        sig = inspect.signature(client.search.linkedin.jobs)

        params = sig.parameters
        assert "url" in params
        assert "location" in params
        assert "keyword" in params
        assert "country" in params
        assert "timeRange" in params
        assert "jobType" in params
        assert "experienceLevel" in params
        assert "remote" in params
        assert "company" in params
        assert "locationRadius" in params
        assert "timeout" in params


class TestLinkedInClientIntegration:
    """Test LinkedIn integrates properly with client."""

    def test_linkedin_accessible_via_client_scrape(self):
        """Test LinkedIn scraper accessible via client.scrape.linkedin."""
        client = BrightDataClient(token="test_token_123456789")

        linkedin = client.scrape.linkedin
        assert linkedin is not None
        assert isinstance(linkedin, LinkedInScraper)

    def test_linkedin_accessible_via_client_search(self):
        """Test LinkedIn search accessible via client.search.linkedin."""
        client = BrightDataClient(token="test_token_123456789")

        linkedin_search = client.search.linkedin
        assert linkedin_search is not None
        assert isinstance(linkedin_search, LinkedInSearchScraper)

    def test_client_passes_token_to_scraper(self):
        """Test client passes token to LinkedIn scraper."""
        token = "test_token_123456789"
        client = BrightDataClient(token=token)

        linkedin = client.scrape.linkedin
        assert linkedin.bearer_token == token

    def test_client_passes_token_to_search(self):
        """Test client passes token to LinkedIn search."""
        token = "test_token_123456789"
        client = BrightDataClient(token=token)

        search = client.search.linkedin
        assert search.bearer_token == token


class TestInterfaceExamples:
    """Test interface examples from specifications."""

    def test_scrape_posts_interface(self):
        """Test scrape.linkedin.posts interface."""
        client = BrightDataClient(token="test_token_123456789")

        # Interface: posts(url=str|list, timeout=180)
        linkedin = client.scrape.linkedin

        # Should be callable
        assert callable(linkedin.posts)

        # Accepts url, sync, timeout
        import inspect

        sig = inspect.signature(linkedin.posts)
        assert set(["url", "timeout"]).issubset(sig.parameters.keys())

    def test_search_posts_interface(self):
        """Test search.linkedin.posts interface."""
        client = BrightDataClient(token="test_token_123456789")

        # Interface: posts(profile_url, start_date, end_date)
        linkedin_search = client.search.linkedin

        assert callable(linkedin_search.posts)

        import inspect

        sig = inspect.signature(linkedin_search.posts)
        assert "profile_url" in sig.parameters
        assert "start_date" in sig.parameters
        assert "end_date" in sig.parameters

    def test_search_jobs_interface(self):
        """Test search.linkedin.jobs interface."""
        client = BrightDataClient(token="test_token_123456789")

        # Interface: jobs(url, location, keyword, ..many filters)
        linkedin_search = client.search.linkedin

        assert callable(linkedin_search.jobs)

        import inspect

        sig = inspect.signature(linkedin_search.jobs)

        # All the filters from spec
        expected_params = [
            "url",
            "location",
            "keyword",
            "country",
            "timeRange",
            "jobType",
            "experienceLevel",
            "remote",
            "company",
            "locationRadius",
            "timeout",
        ]

        for param in expected_params:
            assert param in sig.parameters


class TestParameterArraySupport:
    """Test array parameter support (str | array<str>)."""

    def test_url_accepts_string(self):
        """Test url parameter accepts single string."""
        import inspect

        scraper = LinkedInScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.posts)

        # Type annotation should allow str | List[str]
        url_annotation = str(sig.parameters["url"].annotation)
        assert "Union" in url_annotation or "|" in url_annotation
        assert "str" in url_annotation

    def test_profile_url_accepts_array(self):
        """Test profile_url accepts arrays."""
        import inspect

        search = LinkedInSearchScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(search.posts)

        # profile_url should accept str | list
        annotation = str(sig.parameters["profile_url"].annotation)
        assert "Union" in annotation or "str" in annotation


class TestAsyncFirstAPI:
    """Test all methods follow async-first pattern."""

    def test_scraper_has_all_methods(self):
        """Test scraper has all methods (async-first API, no _async suffix)."""
        scraper = LinkedInScraper(bearer_token="test_token_123456789")

        methods = ["posts", "jobs", "profiles", "companies"]

        for method in methods:
            assert hasattr(scraper, method)
            assert callable(getattr(scraper, method))

    def test_search_has_all_methods(self):
        """Test search has all methods (async-first API, no _async suffix)."""
        search = LinkedInSearchScraper(bearer_token="test_token_123456789")

        methods = ["posts", "profiles", "jobs"]

        for method in methods:
            assert hasattr(search, method)
            assert callable(getattr(search, method))


class TestPhilosophicalPrinciples:
    """Test LinkedIn follows philosophical principles."""

    def test_clear_scrape_vs_search_distinction(self):
        """Test clear distinction between scrape (URL) and search (params)."""
        client = BrightDataClient(token="test_token_123456789")

        scraper = client.scrape.linkedin
        search = client.search.linkedin

        # Scraper is for URLs
        import inspect

        scraper_posts_sig = inspect.signature(scraper.posts)
        assert "url" in scraper_posts_sig.parameters

        # Search is for discovery parameters
        search_posts_sig = inspect.signature(search.posts)
        assert "profile_url" in search_posts_sig.parameters
        assert "start_date" in search_posts_sig.parameters

    def test_consistent_timeout_defaults(self):
        """Test consistent timeout defaults across methods."""
        client = BrightDataClient(token="test_token_123456789")

        scraper = client.scrape.linkedin

        import inspect

        # All scrape methods should default to 65s
        for method_name in ["posts", "jobs", "profiles", "companies"]:
            sig = inspect.signature(getattr(scraper, method_name))
            assert sig.parameters["timeout"].default == 180

    def test_uses_standard_async_workflow(self):
        """Test methods use standard async workflow (no sync parameter)."""
        client = BrightDataClient(token="test_token_123456789")

        scraper = client.scrape.linkedin

        import inspect

        sig = inspect.signature(scraper.posts)

        # Should not have sync parameter
        assert "sync" not in sig.parameters
