"""Unit tests for SERP service."""

from brightdata.api.serp import (
    BaseSERPService,
    GoogleSERPService,
    BingSERPService,
    YandexSERPService,
)


class TestBaseSERPService:
    """Test base SERP service functionality."""

    def test_base_serp_has_search_engine_attribute(self):
        """Test base SERP service has SEARCH_ENGINE attribute."""
        assert hasattr(BaseSERPService, "SEARCH_ENGINE")
        assert hasattr(BaseSERPService, "ENDPOINT")

    def test_base_serp_has_search_methods(self):
        """Test base SERP service has search methods."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        assert hasattr(service, "search")
        assert hasattr(service, "search_async")
        assert callable(service.search)
        assert callable(service.search_async)

    def test_base_serp_has_data_normalizer(self):
        """Test base SERP has data_normalizer."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        assert hasattr(service, "data_normalizer")
        assert hasattr(service.data_normalizer, "normalize")
        assert callable(service.data_normalizer.normalize)


class TestGoogleSERPService:
    """Test Google SERP service."""

    def test_google_serp_has_correct_engine_name(self):
        """Test Google SERP service has correct search engine name."""
        assert GoogleSERPService.SEARCH_ENGINE == "google"

    def test_google_serp_build_search_url(self):
        """Test Google search URL building."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        url = service.url_builder.build(
            query="python tutorial",
            location="United States",
            language="en",
            device="desktop",
            num_results=10,
        )

        assert "google.com/search" in url
        assert "q=python+tutorial" in url or "q=python%20tutorial" in url
        assert "num=10" in url
        assert "hl=en" in url
        assert "gl=" in url  # Location code

    def test_google_serp_url_encoding(self):
        """Test Google search query encoding."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        url = service.url_builder.build(
            query="python & javascript",
            location=None,
            language="en",
            device="desktop",
            num_results=10,
        )

        # Should encode special characters
        assert "google.com/search" in url
        assert "+" in url or "%20" in url  # Space encoded

    def test_google_serp_location_parsing(self):
        """Test location name to country code parsing."""
        from brightdata.utils.location import LocationService, LocationFormat

        # Test country name mappings
        assert LocationService.parse_location("United States", LocationFormat.GOOGLE) == "us"
        assert LocationService.parse_location("United Kingdom", LocationFormat.GOOGLE) == "gb"
        assert LocationService.parse_location("Canada", LocationFormat.GOOGLE) == "ca"

        # Test direct codes
        assert LocationService.parse_location("US", LocationFormat.GOOGLE) == "us"
        assert LocationService.parse_location("GB", LocationFormat.GOOGLE) == "gb"

    def test_google_serp_normalize_data(self):
        """Test Google SERP data normalization."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        # Test with structured data
        raw_data = {
            "organic": [
                {
                    "title": "Python Tutorial",
                    "url": "https://python.org/tutorial",
                    "description": "Learn Python",
                },
                {
                    "title": "Advanced Python",
                    "url": "https://example.com/advanced",
                    "description": "Advanced topics",
                },
            ],
            "total_results": 1000000,
        }

        normalized = service.data_normalizer.normalize(raw_data)

        assert "results" in normalized
        assert len(normalized["results"]) == 2
        assert normalized["results"][0]["position"] == 1
        assert normalized["results"][0]["title"] == "Python Tutorial"
        assert normalized["results"][1]["position"] == 2

    def test_google_serp_normalize_empty_data(self):
        """Test Google SERP normalization with empty data."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        # Normalization is done via data_normalizer attribute
        normalized = service.data_normalizer.normalize({})
        assert "results" in normalized
        assert normalized["results"] == []


class TestBingSERPService:
    """Test Bing SERP service."""

    def test_bing_serp_has_correct_engine_name(self):
        """Test Bing SERP service has correct search engine name."""
        assert BingSERPService.SEARCH_ENGINE == "bing"

    def test_bing_serp_build_search_url(self):
        """Test Bing search URL building."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = BingSERPService(engine)

        url = service.url_builder.build(
            query="python tutorial",
            location="United States",
            language="en",
            device="desktop",
            num_results=10,
        )

        assert "bing.com/search" in url
        assert "q=python" in url
        assert "count=10" in url


class TestYandexSERPService:
    """Test Yandex SERP service."""

    def test_yandex_serp_has_correct_engine_name(self):
        """Test Yandex SERP service has correct search engine name."""
        assert YandexSERPService.SEARCH_ENGINE == "yandex"

    def test_yandex_serp_build_search_url(self):
        """Test Yandex search URL building."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = YandexSERPService(engine)

        url = service.url_builder.build(
            query="python tutorial",
            location="Russia",
            language="ru",
            device="desktop",
            num_results=10,
        )

        assert "yandex.com/search" in url
        assert "text=python" in url
        assert "numdoc=10" in url


class TestSERPNormalization:
    """Test SERP data normalization across engines."""

    def test_normalized_results_have_position(self):
        """Test normalized results include ranking position."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        raw_data = {
            "organic": [
                {"title": "Result 1", "url": "https://example1.com", "description": "Desc 1"},
                {"title": "Result 2", "url": "https://example2.com", "description": "Desc 2"},
            ]
        }

        normalized = service.data_normalizer.normalize(raw_data)

        # Each result should have position starting from 1
        for i, result in enumerate(normalized["results"], 1):
            assert result["position"] == i

    def test_normalized_results_have_required_fields(self):
        """Test normalized results have required fields."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        raw_data = {
            "organic": [
                {"title": "Test", "url": "https://test.com", "description": "Test desc"},
            ]
        }

        normalized = service.data_normalizer.normalize(raw_data)
        result = normalized["results"][0]

        # Required fields
        assert "position" in result
        assert "title" in result
        assert "url" in result
        assert "description" in result


class TestClientIntegration:
    """Test SERP services integrate with BrightDataClient."""

    def test_search_service_accessible_through_client(self):
        """Test search service is accessible via client.search."""
        from brightdata import BrightDataClient

        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client, "search")
        assert client.search is not None

    def test_search_service_has_google_method(self):
        """Test search service has google() method."""
        from brightdata import BrightDataClient

        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client.search, "google")
        assert hasattr(client.search, "google_async")
        assert callable(client.search.google)
        assert callable(client.search.google_async)

    def test_search_service_has_bing_method(self):
        """Test search service has bing() method."""
        from brightdata import BrightDataClient

        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client.search, "bing")
        assert hasattr(client.search, "bing_async")
        assert callable(client.search.bing)

    def test_search_service_has_yandex_method(self):
        """Test search service has yandex() method."""
        from brightdata import BrightDataClient

        client = BrightDataClient(token="test_token_123456789")

        assert hasattr(client.search, "yandex")
        assert hasattr(client.search, "yandex_async")
        assert callable(client.search.yandex)


class TestSERPInterfaceConsistency:
    """Test interface consistency across search engines."""

    def test_all_engines_have_same_signature(self):
        """Test all search engines have consistent method signatures."""
        from brightdata import BrightDataClient
        import inspect

        client = BrightDataClient(token="test_token_123456789")

        # Get signatures
        google_sig = inspect.signature(client.search.google)
        bing_sig = inspect.signature(client.search.bing)
        yandex_sig = inspect.signature(client.search.yandex)

        # All should have 'query' parameter
        assert "query" in google_sig.parameters
        assert "query" in bing_sig.parameters
        assert "query" in yandex_sig.parameters

    def test_all_engines_return_search_result(self):
        """Test all engines return SearchResult type."""
        from brightdata import BrightDataClient
        import inspect

        client = BrightDataClient(token="test_token_123456789")

        # Check return type hints if available
        google_sig = inspect.signature(client.search.google_async)
        # Return annotation should mention SearchResult or List[SearchResult]
        if google_sig.return_annotation != inspect.Signature.empty:
            assert "SearchResult" in str(google_sig.return_annotation)


class TestPhilosophicalPrinciples:
    """Test SERP service follows philosophical principles."""

    def test_serp_data_normalized_across_engines(self):
        """Test SERP data is normalized for easy comparison."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")

        # Same raw data structure
        raw_data = {
            "organic": [
                {"title": "Result", "url": "https://example.com", "description": "Desc"},
            ],
            "total_results": 1000,
        }

        # Both engines should normalize to same format
        google_service = GoogleSERPService(engine)
        google_normalized = google_service.data_normalizer.normalize(raw_data)

        # Normalized format should have:
        assert "results" in google_normalized
        assert "total_results" in google_normalized
        assert isinstance(google_normalized["results"], list)

    def test_search_engine_quirks_handled_transparently(self):
        """Test search engine specific quirks are abstracted away."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")

        # Different engines have different URL patterns
        google = GoogleSERPService(engine)
        bing = BingSERPService(engine)
        yandex = YandexSERPService(engine)

        # But all build URLs transparently
        google_url = google.url_builder.build("test", None, "en", "desktop", 10)
        bing_url = bing.url_builder.build("test", None, "en", "desktop", 10)
        yandex_url = yandex.url_builder.build("test", None, "ru", "desktop", 10)

        # Each should have their engine's domain
        assert "google.com" in google_url
        assert "bing.com" in bing_url
        assert "yandex.com" in yandex_url

        # But query is present in all
        assert "test" in google_url
        assert "test" in bing_url
        assert "test" in yandex_url

    def test_results_include_ranking_position(self):
        """Test results include ranking position for competitive analysis."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        raw_data = {
            "organic": [
                {"title": "First", "url": "https://1.com", "description": "D1"},
                {"title": "Second", "url": "https://2.com", "description": "D2"},
                {"title": "Third", "url": "https://3.com", "description": "D3"},
            ]
        }

        normalized = service.data_normalizer.normalize(raw_data)

        # Positions should be 1, 2, 3
        positions = [r["position"] for r in normalized["results"]]
        assert positions == [1, 2, 3]


class TestSERPFeatureExtraction:
    """Test SERP feature detection and extraction."""

    def test_extract_featured_snippet(self):
        """Test extraction of featured snippet."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        raw_data = {
            "organic": [],
            "featured_snippet": {
                "title": "What is Python?",
                "description": "Python is a programming language...",
                "url": "https://python.org",
            },
        }

        normalized = service.data_normalizer.normalize(raw_data)

        assert "featured_snippet" in normalized
        assert normalized["featured_snippet"]["title"] == "What is Python?"

    def test_extract_knowledge_panel(self):
        """Test extraction of knowledge panel."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        raw_data = {
            "organic": [],
            "knowledge_panel": {
                "title": "Python",
                "type": "Programming Language",
                "description": "High-level programming language",
            },
        }

        normalized = service.data_normalizer.normalize(raw_data)

        assert "knowledge_panel" in normalized
        assert normalized["knowledge_panel"]["title"] == "Python"

    def test_extract_people_also_ask(self):
        """Test extraction of People Also Ask section."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        raw_data = {
            "organic": [],
            "people_also_ask": [
                {"question": "What is Python used for?", "answer": "..."},
                {"question": "Is Python easy to learn?", "answer": "..."},
            ],
        }

        normalized = service.data_normalizer.normalize(raw_data)

        assert "people_also_ask" in normalized
        assert len(normalized["people_also_ask"]) == 2


class TestLocationLanguageSupport:
    """Test location and language-specific search support."""

    def test_google_supports_location(self):
        """Test Google search supports location parameter."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        url = service.url_builder.build(
            query="restaurants",
            location="New York",
            language="en",
            device="desktop",
            num_results=10,
        )

        # Should have location parameter
        assert "gl=" in url

    def test_google_supports_language(self):
        """Test Google search supports language parameter."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        url_en = service.url_builder.build("test", None, "en", "desktop", 10)
        url_es = service.url_builder.build("test", None, "es", "desktop", 10)
        url_fr = service.url_builder.build("test", None, "fr", "desktop", 10)

        assert "hl=en" in url_en
        assert "hl=es" in url_es
        assert "hl=fr" in url_fr

    def test_google_supports_device_types(self):
        """Test Google search supports device type parameter."""
        from brightdata.core.engine import AsyncEngine

        engine = AsyncEngine("test_token_123456789")
        service = GoogleSERPService(engine)

        service.url_builder.build("test", None, "en", "desktop", 10)
        url_mobile = service.url_builder.build("test", None, "en", "mobile", 10)

        # Mobile should have mobile-specific parameter
        assert "mobile" in url_mobile.lower() or "mobileaction" in url_mobile
