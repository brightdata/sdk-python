"""Unit tests for Amazon scraper."""

import pytest
from brightdata import BrightDataClient
from brightdata.scrapers.amazon import AmazonScraper
from brightdata.exceptions import ValidationError


class TestAmazonScraperURLBased:
    """Test Amazon scraper (URL-based extraction)."""
    
    def test_amazon_scraper_has_products_method(self):
        """Test Amazon scraper has products method."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        assert hasattr(scraper, 'products')
        assert hasattr(scraper, 'products_async')
        assert callable(scraper.products)
        assert callable(scraper.products_async)
    
    def test_amazon_scraper_has_reviews_method(self):
        """Test Amazon scraper has reviews method."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        assert hasattr(scraper, 'reviews')
        assert hasattr(scraper, 'reviews_async')
        assert callable(scraper.reviews)
        assert callable(scraper.reviews_async)
    
    def test_amazon_scraper_has_sellers_method(self):
        """Test Amazon scraper has sellers method."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        assert hasattr(scraper, 'sellers')
        assert hasattr(scraper, 'sellers_async')
        assert callable(scraper.sellers)
        assert callable(scraper.sellers_async)
    
    def test_products_method_signature(self):
        """Test products method has correct signature."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.products)
        
        # Required: url parameter
        assert 'url' in sig.parameters
        
        # Optional: sync and timeout
        assert 'sync' in sig.parameters
        assert 'timeout' in sig.parameters
        
        # Defaults
        assert sig.parameters['sync'].default is True
        assert sig.parameters['timeout'].default == 65
    
    def test_reviews_method_signature(self):
        """Test reviews method has correct signature."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reviews)
        
        # Required: url
        assert 'url' in sig.parameters
        
        # Optional filters
        assert 'pastDays' in sig.parameters
        assert 'keyWord' in sig.parameters
        assert 'numOfReviews' in sig.parameters
        assert 'sync' in sig.parameters
        assert 'timeout' in sig.parameters
        
        # Defaults
        assert sig.parameters['sync'].default is True
        assert sig.parameters['timeout'].default == 65
    
    def test_sellers_method_signature(self):
        """Test sellers method has correct signature."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.sellers)
        
        assert 'url' in sig.parameters
        assert 'sync' in sig.parameters
        assert 'timeout' in sig.parameters
        assert sig.parameters['sync'].default is True
        assert sig.parameters['timeout'].default == 65


class TestAmazonDatasetIDs:
    """Test Amazon has correct dataset IDs."""
    
    def test_scraper_has_all_dataset_ids(self):
        """Test scraper has dataset IDs for all types."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        assert scraper.DATASET_ID  # Products
        assert scraper.DATASET_ID_REVIEWS
        assert scraper.DATASET_ID_SELLERS
        
        # All should start with gd_
        assert scraper.DATASET_ID.startswith("gd_")
        assert scraper.DATASET_ID_REVIEWS.startswith("gd_")
        assert scraper.DATASET_ID_SELLERS.startswith("gd_")
    
    def test_dataset_ids_are_correct(self):
        """Test dataset IDs match Bright Data identifiers."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        # Verify known IDs
        assert scraper.DATASET_ID == "gd_l7q7dkf244hwxbl93"  # Products
        assert scraper.DATASET_ID_REVIEWS == "gd_l1vq6tkpl34p7mq7c"  # Reviews
        assert scraper.DATASET_ID_SELLERS == "gd_lwjkkolem8c4o7j3s"  # Sellers


class TestAmazonSyncVsAsyncMode:
    """Test sync vs async mode handling."""
    
    def test_sync_true_uses_correct_timeout(self):
        """Test sync=True uses 65s default timeout."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.products)
        
        assert sig.parameters['timeout'].default == 65
    
    def test_all_methods_have_sync_parameter(self):
        """Test all scrape methods have sync parameter."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        for method_name in ['products', 'reviews', 'sellers']:
            sig = inspect.signature(getattr(scraper, method_name))
            assert 'sync' in sig.parameters
            assert sig.parameters['sync'].default is True


class TestAmazonAPISpecCompliance:
    """Test compliance with exact API specifications."""
    
    def test_products_api_spec(self):
        """Test products() matches CP API spec."""
        client = BrightDataClient(token="test_token_123456789")
        
        # API Spec: client.scrape.amazon.products(url, sync=True, timeout=65)
        import inspect
        sig = inspect.signature(client.scrape.amazon.products)
        
        assert 'url' in sig.parameters
        assert 'sync' in sig.parameters
        assert 'timeout' in sig.parameters
        assert sig.parameters['sync'].default is True
        assert sig.parameters['timeout'].default == 65
    
    def test_reviews_api_spec(self):
        """Test reviews() matches CP API spec."""
        client = BrightDataClient(token="test_token_123456789")
        
        # API Spec: reviews(url, pastDays, keyWord, numOfReviews, sync, timeout)
        import inspect
        sig = inspect.signature(client.scrape.amazon.reviews)
        
        params = sig.parameters
        assert 'url' in params
        assert 'pastDays' in params
        assert 'keyWord' in params
        assert 'numOfReviews' in params
        assert 'sync' in params
        assert 'timeout' in params
    
    def test_sellers_api_spec(self):
        """Test sellers() matches CP API spec."""
        client = BrightDataClient(token="test_token_123456789")
        
        # API Spec: sellers(url, sync=True, timeout=65)
        import inspect
        sig = inspect.signature(client.scrape.amazon.sellers)
        
        assert 'url' in sig.parameters
        assert 'sync' in sig.parameters
        assert 'timeout' in sig.parameters


class TestAmazonParameterArraySupport:
    """Test array parameter support (str | array<str>)."""
    
    def test_url_accepts_string(self):
        """Test url parameter accepts single string."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.products)
        
        # Type annotation should allow str | List[str]
        url_annotation = str(sig.parameters['url'].annotation)
        assert 'Union' in url_annotation or '|' in url_annotation
        assert 'str' in url_annotation
    
    def test_url_accepts_list(self):
        """Test url parameter accepts list."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.products)
        
        url_annotation = str(sig.parameters['url'].annotation)
        assert 'List' in url_annotation or 'list' in url_annotation


class TestAmazonSyncAsyncPairs:
    """Test all methods have async/sync pairs."""
    
    def test_all_methods_have_pairs(self):
        """Test all methods have async/sync pairs."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        methods = ['products', 'reviews', 'sellers']
        
        for method in methods:
            assert hasattr(scraper, method)
            assert hasattr(scraper, f'{method}_async')
            assert callable(getattr(scraper, method))
            assert callable(getattr(scraper, f'{method}_async'))


class TestAmazonClientIntegration:
    """Test Amazon integrates properly with client."""
    
    def test_amazon_accessible_via_client(self):
        """Test Amazon scraper accessible via client.scrape.amazon."""
        client = BrightDataClient(token="test_token_123456789")
        
        amazon = client.scrape.amazon
        assert amazon is not None
        assert isinstance(amazon, AmazonScraper)
    
    def test_client_passes_token_to_scraper(self):
        """Test client passes token to Amazon scraper."""
        token = "test_token_123456789"
        client = BrightDataClient(token=token)
        
        amazon = client.scrape.amazon
        assert amazon.bearer_token == token
    
    def test_all_amazon_methods_accessible_through_client(self):
        """Test all Amazon methods accessible through client."""
        client = BrightDataClient(token="test_token_123456789")
        
        amazon = client.scrape.amazon
        
        assert callable(amazon.products)
        assert callable(amazon.reviews)
        assert callable(amazon.sellers)


class TestAmazonReviewsFilters:
    """Test Amazon reviews method filters."""
    
    def test_reviews_accepts_pastDays_filter(self):
        """Test reviews method accepts pastDays parameter."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reviews)
        
        assert 'pastDays' in sig.parameters
        assert sig.parameters['pastDays'].default is None  # Optional
    
    def test_reviews_accepts_keyWord_filter(self):
        """Test reviews method accepts keyWord parameter."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reviews)
        
        assert 'keyWord' in sig.parameters
        assert sig.parameters['keyWord'].default is None
    
    def test_reviews_accepts_numOfReviews_filter(self):
        """Test reviews method accepts numOfReviews parameter."""
        import inspect
        
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        sig = inspect.signature(scraper.reviews)
        
        assert 'numOfReviews' in sig.parameters
        assert sig.parameters['numOfReviews'].default is None


class TestAmazonPhilosophicalPrinciples:
    """Test Amazon scraper follows philosophical principles."""
    
    def test_consistent_timeout_defaults(self):
        """Test consistent timeout defaults across methods."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        import inspect
        
        # All methods should default to 65s
        for method_name in ['products', 'reviews', 'sellers']:
            sig = inspect.signature(getattr(scraper, method_name))
            assert sig.parameters['timeout'].default == 65
    
    def test_sync_mode_default_is_true(self):
        """Test sync mode defaults to True (immediate response)."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        import inspect
        
        for method_name in ['products', 'reviews', 'sellers']:
            sig = inspect.signature(getattr(scraper, method_name))
            assert sig.parameters['sync'].default is True
    
    def test_amazon_is_platform_expert(self):
        """Test Amazon scraper knows its platform."""
        scraper = AmazonScraper(bearer_token="test_token_123456789")
        
        assert scraper.PLATFORM_NAME == "amazon"
        assert scraper.DATASET_ID  # Has dataset knowledge
        assert scraper.MIN_POLL_TIMEOUT == 240  # Knows Amazon takes longer

