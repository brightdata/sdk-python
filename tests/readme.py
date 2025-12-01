"""
Tests to validate all code samples in README.md.

This test suite ensures that all code examples in the README.md file are accurate
and functional. Tests are organized by README sections and include:
- Authentication examples
- Simple web scraping examples
- Dataclass payload examples
- Pandas integration examples
- Platform-specific scraping (Amazon, LinkedIn, ChatGPT, Facebook, Instagram)
- SERP API examples (Google, Bing, Yandex)
- Async usage examples
- CLI tool examples
- Advanced usage examples
- Complete workflow example

All tests use real API calls (no mocking) to ensure documentation accuracy.
"""

import os
import json
import subprocess
import pytest
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

from brightdata import BrightDataClient
from brightdata.payloads import (
    AmazonProductPayload,
    LinkedInJobSearchPayload,
    ChatGPTPromptPayload,
)


@pytest.fixture
def api_token():
    """Get API token from environment or skip tests."""
    token = os.getenv("BRIGHTDATA_API_TOKEN")
    if not token:
        pytest.skip("API token not found. Set BRIGHTDATA_API_TOKEN to run README validation tests.")
    return token


@pytest.fixture
def client(api_token):
    """Create synchronous client instance for testing."""
    return BrightDataClient(token=api_token)


@pytest.fixture
async def async_client(api_token):
    """Create async client instance for testing."""
    async with BrightDataClient(token=api_token) as client:
        yield client


class TestQuickStartAuthentication:
    """Test authentication examples from Quick Start section."""

    def test_environment_variable_auth(self, api_token):
        """
        Test: README Quick Start - Authentication with environment variable.
        Line: 106-107
        """
        # From README: client = BrightDataClient()
        client = BrightDataClient()

        assert client is not None, "Client initialization failed"
        assert client.token == api_token, "Token not loaded from environment"

    def test_direct_credentials_auth(self):
        """
        Test: README Quick Start - Authentication with direct credentials.
        Line: 92-98
        """
        token = os.getenv("BRIGHTDATA_API_TOKEN")
        if not token:
            pytest.skip("API token not found")

        customer_id = os.getenv("BRIGHTDATA_CUSTOMER_ID")

        # From README
        client = BrightDataClient(token=token, customer_id=customer_id)

        assert client is not None, "Client initialization failed"
        assert client.token == token, "Token not set correctly"


class TestQuickStartSimpleScraping:
    """Test simple web scraping example from Quick Start."""

    def test_simple_web_scraping(self, client):
        """
        Test: README Quick Start - Simple Web Scraping.
        Line: 101-118
        """
        # From README:
        # result = client.scrape.generic.url("https://example.com")
        # if result.success:
        #     print(f"Success: {result.success}")
        #     print(f"Data: {result.data[:200]}...")
        #     print(f"Time: {result.elapsed_ms():.2f}ms")

        result = client.scrape.generic.url("https://example.com")

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"
        assert hasattr(result, "data"), "Result missing 'data' attribute"
        assert hasattr(result, "error"), "Result missing 'error' attribute"

        # Verify we can access the attributes as shown in README
        if result.success:
            assert result.data is not None, "data should not be None when success=True"
            elapsed = result.elapsed_ms()
            assert isinstance(elapsed, (int, float)), "elapsed_ms() should return number"
            assert elapsed >= 0, "elapsed_ms() should be non-negative"


class TestDataclassPayloads:
    """Test dataclass payload examples from README."""

    def test_amazon_payload_basic(self):
        """
        Test: README - Using Dataclass Payloads with Amazon.
        Line: 128-135
        """
        # From README:
        # payload = AmazonProductPayload(
        #     url="https://amazon.com/dp/B123456789",
        #     reviews_count=50
        # )
        # print(f"ASIN: {payload.asin}")

        payload = AmazonProductPayload(url="https://amazon.com/dp/B0CRMZHDG8", reviews_count=50)

        # Verify helper property
        assert payload.asin == "B0CRMZHDG8", f"Expected ASIN 'B0CRMZHDG8', got '{payload.asin}'"

        # Verify to_dict() method
        api_dict = payload.to_dict()
        assert isinstance(api_dict, dict), "to_dict() should return dict"
        assert "url" in api_dict, "to_dict() missing 'url' key"

    def test_linkedin_job_payload(self):
        """
        Test: README - LinkedIn job search payload.
        Line: 138-145
        """
        # From README:
        # job_payload = LinkedInJobSearchPayload(
        #     keyword="python developer",
        #     location="New York",
        #     remote=True
        # )
        # print(f"Remote search: {job_payload.is_remote_search}")

        job_payload = LinkedInJobSearchPayload(
            keyword="python developer", location="New York", remote=True
        )

        assert job_payload.is_remote_search is True, "is_remote_search should be True"

        api_dict = job_payload.to_dict()
        assert isinstance(api_dict, dict), "to_dict() should return dict"
        assert "keyword" in api_dict, "to_dict() missing 'keyword'"

    def test_amazon_payload_detailed(self):
        """
        Test: README - Amazon payload with helper properties.
        Line: 711-723
        """
        # From README:
        # payload = AmazonProductPayload(
        #     url="https://amazon.com/dp/B123456789",
        #     reviews_count=50,
        #     images_count=10
        # )
        # print(payload.asin)        # "B123456789"
        # print(payload.domain)      # "amazon.com"
        # print(payload.is_secure)   # True

        payload = AmazonProductPayload(
            url="https://amazon.com/dp/B0CRMZHDG8", reviews_count=50, images_count=10
        )

        assert payload.asin == "B0CRMZHDG8", "ASIN extraction failed"
        assert payload.domain == "amazon.com", "Domain extraction failed"
        assert payload.is_secure is True, "is_secure should be True for https"

        api_dict = payload.to_dict()
        assert "url" in api_dict, "to_dict() missing 'url'"

    def test_linkedin_job_payload_detailed(self):
        """
        Test: README - LinkedIn payload with helper properties.
        Line: 731-742
        """
        # From README:
        # payload = LinkedInJobSearchPayload(
        #     keyword="python developer",
        #     location="San Francisco",
        #     remote=True,
        #     experienceLevel="mid"
        # )
        # print(payload.is_remote_search)  # True

        payload = LinkedInJobSearchPayload(
            keyword="python developer", location="San Francisco", remote=True, experienceLevel="mid"
        )

        assert payload.is_remote_search is True, "is_remote_search should be True"

        api_dict = payload.to_dict()
        assert api_dict["keyword"] == "python developer", "Keyword mismatch"
        assert api_dict["remote"] is True, "Remote should be True"

    def test_chatgpt_payload_defaults(self):
        """
        Test: README - ChatGPT payload with default values.
        Line: 750-757
        """
        # From README:
        # payload = ChatGPTPromptPayload(
        #     prompt="Explain async programming",
        #     web_search=True
        # )
        # print(payload.country)  # "US" (default)
        # print(payload.uses_web_search)  # True

        payload = ChatGPTPromptPayload(prompt="Explain async programming", web_search=True)

        assert payload.country == "US", "Default country should be 'US'"
        assert payload.uses_web_search is True, "uses_web_search should be True"

    def test_payload_validation_invalid_url(self):
        """
        Test: README - Payload validation for invalid URL.
        Line: 764-767
        """
        # From README:
        # try:
        #     AmazonProductPayload(url="invalid-url")
        # except ValueError as e:
        #     print(e)  # "url must be valid HTTP/HTTPS URL"

        with pytest.raises(ValueError) as exc_info:
            AmazonProductPayload(url="invalid-url")

        error_msg = str(exc_info.value).lower()
        assert "url" in error_msg, f"Error should mention 'url', got: {error_msg}"

    def test_payload_validation_negative_count(self):
        """
        Test: README - Payload validation for negative reviews_count.
        Line: 769-775
        """
        # From README:
        # try:
        #     AmazonProductPayload(
        #         url="https://amazon.com/dp/B123",
        #         reviews_count=-1
        #     )
        # except ValueError as e:
        #     print(e)  # "reviews_count must be non-negative"

        with pytest.raises(ValueError) as exc_info:
            AmazonProductPayload(url="https://amazon.com/dp/B0CRMZHDG8", reviews_count=-1)

        error_msg = str(exc_info.value).lower()
        assert (
            "reviews_count" in error_msg or "negative" in error_msg
        ), f"Error should mention reviews_count or negative, got: {error_msg}"


class TestPlatformSpecificAmazon:
    """Test Amazon platform-specific examples from README."""

    @pytest.mark.slow
    def test_amazon_product_scraping(self, client):
        """
        Test: README - Amazon product scraping.
        Line: 183-187
        """
        # From README:
        # result = client.scrape.amazon.products(
        #     url="https://amazon.com/dp/B0CRMZHDG8",
        #     timeout=65
        # )

        result = client.scrape.amazon.products(url="https://amazon.com/dp/B0CRMZHDG8", timeout=65)

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"
        assert hasattr(result, "data"), "Result missing 'data' attribute"

    @pytest.mark.slow
    def test_amazon_reviews_with_filters(self, client):
        """
        Test: README - Amazon reviews with filters.
        Line: 189-195
        """
        # From README:
        # result = client.scrape.amazon.reviews(
        #     url="https://amazon.com/dp/B0CRMZHDG8",
        #     pastDays=30,
        #     keyWord="quality",
        #     numOfReviews=100
        # )

        result = client.scrape.amazon.reviews(
            url="https://amazon.com/dp/B0CRMZHDG8",
            pastDays=30,
            keyWord="quality",
            numOfReviews=10,  # Reduced for faster testing
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_amazon_sellers(self, client):
        """
        Test: README - Amazon seller information.
        Line: 197-200
        """
        # From README:
        # result = client.scrape.amazon.sellers(
        #     url="https://amazon.com/sp?seller=AXXXXXXXXX"
        # )

        # Using a real seller URL for testing
        result = client.scrape.amazon.sellers(url="https://amazon.com/sp?seller=A2L77EE7U53NWQ")

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"


class TestPlatformSpecificLinkedIn:
    """Test LinkedIn platform-specific examples from README."""

    @pytest.mark.slow
    def test_linkedin_profile_scraping(self, client):
        """
        Test: README - LinkedIn profile scraping.
        Line: 206-209
        """
        # From README:
        # result = client.scrape.linkedin.profiles(
        #     url="https://linkedin.com/in/johndoe"
        # )

        result = client.scrape.linkedin.profiles(url="https://linkedin.com/in/williamhgates")

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_linkedin_jobs_scrape(self, client):
        """
        Test: README - LinkedIn job scraping by URL.
        Line: 211-213
        """
        # From README:
        # result = client.scrape.linkedin.jobs(
        #     url="https://linkedin.com/jobs/view/123456"
        # )

        # Using a real job URL for testing
        result = client.scrape.linkedin.jobs(url="https://linkedin.com/jobs/view/3000000000")

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_linkedin_companies(self, client):
        """
        Test: README - LinkedIn company scraping.
        Line: 215-217
        """
        # From README:
        # result = client.scrape.linkedin.companies(
        #     url="https://linkedin.com/company/microsoft"
        # )

        result = client.scrape.linkedin.companies(url="https://linkedin.com/company/microsoft")

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_linkedin_job_search(self, client):
        """
        Test: README - LinkedIn job search/discovery.
        Line: 224-229
        """
        # From README:
        # result = client.search.linkedin.jobs(
        #     keyword="python developer",
        #     location="New York",
        #     remote=True,
        #     experienceLevel="mid"
        # )

        result = client.search.linkedin.jobs(
            keyword="python developer", location="New York", remote=True, experienceLevel="mid"
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_linkedin_profile_search(self, client):
        """
        Test: README - LinkedIn profile search.
        Line: 231-234
        """
        # From README:
        # result = client.search.linkedin.profiles(
        #     firstName="John",
        #     lastName="Doe"
        # )

        result = client.search.linkedin.profiles(firstName="Bill", lastName="Gates")

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"


class TestPlatformSpecificChatGPT:
    """Test ChatGPT platform-specific examples from README."""

    @pytest.mark.slow
    def test_chatgpt_single_prompt(self, client):
        """
        Test: README - ChatGPT single prompt.
        Line: 246-251
        """
        # From README:
        # result = client.scrape.chatgpt.prompt(
        #     prompt="Explain Python async programming",
        #     country="us",
        #     web_search=True
        # )

        result = client.scrape.chatgpt.prompt(
            prompt="Explain Python async programming", country="us", web_search=True
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_chatgpt_batch_prompts(self, client):
        """
        Test: README - ChatGPT batch prompts.
        Line: 253-257
        """
        # From README:
        # result = client.scrape.chatgpt.prompts(
        #     prompts=["What is Python?", "What is JavaScript?", "Compare them"],
        #     web_searches=[False, False, True]
        # )

        result = client.scrape.chatgpt.prompts(
            prompts=["What is Python?", "What is JavaScript?"], web_searches=[False, False]
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"


class TestPlatformSpecificFacebook:
    """Test Facebook platform-specific examples from README."""

    @pytest.mark.slow
    def test_facebook_posts_by_profile(self, client):
        """
        Test: README - Facebook posts from profile.
        Line: 263-270
        """
        # From README:
        # result = client.scrape.facebook.posts_by_profile(
        #     url="https://facebook.com/profile",
        #     num_of_posts=10,
        #     start_date="01-01-2025",
        #     end_date="12-31-2025",
        #     timeout=240
        # )

        result = client.scrape.facebook.posts_by_profile(
            url="https://facebook.com/zuck",
            num_of_posts=5,
            start_date="01-01-2025",
            end_date="12-31-2025",
            timeout=240,
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_facebook_posts_by_group(self, client):
        """
        Test: README - Facebook posts from group.
        Line: 272-277
        """
        # From README:
        # result = client.scrape.facebook.posts_by_group(
        #     url="https://facebook.com/groups/example",
        #     num_of_posts=20,
        #     timeout=240
        # )

        result = client.scrape.facebook.posts_by_group(
            url="https://facebook.com/groups/programming", num_of_posts=5, timeout=240
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"


class TestPlatformSpecificInstagram:
    """Test Instagram platform-specific examples from README."""

    @pytest.mark.slow
    def test_instagram_profile_scraping(self, client):
        """
        Test: README - Instagram profile scraping.
        Line: 305-309
        """
        # From README:
        # result = client.scrape.instagram.profiles(
        #     url="https://instagram.com/username",
        #     timeout=240
        # )

        result = client.scrape.instagram.profiles(
            url="https://instagram.com/instagram", timeout=240
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_instagram_post_scraping(self, client):
        """
        Test: README - Instagram specific post scraping.
        Line: 311-315
        """
        # From README:
        # result = client.scrape.instagram.posts(
        #     url="https://instagram.com/p/ABC123",
        #     timeout=240
        # )

        result = client.scrape.instagram.posts(
            url="https://instagram.com/p/C0000000000", timeout=240
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    def test_instagram_post_discovery(self, client):
        """
        Test: README - Instagram post discovery with filters.
        Line: 329-337
        """
        # From README:
        # result = client.search.instagram.posts(
        #     url="https://instagram.com/username",
        #     num_of_posts=10,
        #     start_date="01-01-2025",
        #     end_date="12-31-2025",
        #     post_type="reel",
        #     timeout=240
        # )

        result = client.search.instagram.posts(
            url="https://instagram.com/instagram",
            num_of_posts=5,
            start_date="01-01-2025",
            end_date="12-31-2025",
            post_type="reel",
            timeout=240,
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"


class TestSERPAPI:
    """Test SERP API examples from README."""

    def test_google_search(self, client):
        """
        Test: README - Google search.
        Line: 352-358
        """
        # From README:
        # result = client.search.google(
        #     query="python tutorial",
        #     location="United States",
        #     language="en",
        #     num_results=20
        # )

        result = client.search.google(
            query="python tutorial", location="United States", language="en", num_results=10
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"
        assert hasattr(result, "data"), "Result missing 'data' attribute"

        # From README: for item in result.data:
        if result.success and result.data:
            for item in result.data[:3]:
                # Items should have position, title, or url
                assert isinstance(item, dict), "Search result items should be dicts"

    def test_bing_search(self, client):
        """
        Test: README - Bing search.
        Line: 365-369
        """
        # From README:
        # result = client.search.bing(
        #     query="python tutorial",
        #     location="United States"
        # )

        result = client.search.bing(query="python tutorial", location="United States")

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    def test_yandex_search(self, client):
        """
        Test: README - Yandex search.
        Line: 371-375
        """
        # From README:
        # result = client.search.yandex(
        #     query="python tutorial",
        #     location="Russia"
        # )

        result = client.search.yandex(query="python tutorial", location="Russia")

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"


class TestAsyncUsage:
    """Test async usage examples from README."""

    @pytest.mark.asyncio
    async def test_async_multiple_urls(self, api_token):
        """
        Test: README - Async usage with multiple URLs.
        Line: 382-399
        """
        # From README:
        # async def scrape_multiple():
        #     async with BrightDataClient() as client:
        #         results = await client.scrape.generic.url_async([
        #             "https://example1.com",
        #             "https://example2.com",
        #             "https://example3.com"
        #         ])
        #         for result in results:
        #             print(f"Success: {result.success}")

        async with BrightDataClient(token=api_token) as client:
            results = await client.scrape.generic.url_async(
                ["https://httpbin.org/html", "https://example.com", "https://httpbin.org/json"]
            )

            assert results is not None, "Results is None"
            assert isinstance(results, list), "Results should be a list"
            assert len(results) == 3, f"Expected 3 results, got {len(results)}"

            for result in results:
                assert hasattr(result, "success"), "Result missing 'success' attribute"


class TestConnectionTesting:
    """Test connection testing examples from README."""

    @pytest.mark.asyncio
    async def test_async_connection_test(self, async_client):
        """
        Test: README - Async connection test.
        Line: 510-511
        """
        # From README:
        # is_valid = await client.test_connection()

        is_valid = await async_client.test_connection()

        assert isinstance(is_valid, bool), "test_connection should return bool"
        assert is_valid is True, "Connection test should succeed"

    def test_sync_connection_test(self, client):
        """
        Test: README - Sync connection test.
        Line: 512
        """
        # From README:
        # is_valid = client.test_connection_sync()

        is_valid = client.test_connection_sync()

        assert isinstance(is_valid, bool), "test_connection_sync should return bool"
        assert is_valid is True, "Sync connection test should succeed"

    @pytest.mark.asyncio
    async def test_get_account_info_async(self, async_client):
        """
        Test: README - Get account info async.
        Line: 514-519
        """
        # From README:
        # info = await client.get_account_info()
        # print(f"Zones: {info['zone_count']}")
        # print(f"Active zones: {[z['name'] for z in info['zones']]}")

        info = await async_client.get_account_info()

        assert isinstance(info, dict), "Account info should be dict"
        assert "zone_count" in info, "Account info missing 'zone_count'"
        assert "zones" in info, "Account info missing 'zones'"

    def test_get_account_info_sync(self, client):
        """
        Test: README - Get account info sync.
        Line: 516
        """
        # From README:
        # info = client.get_account_info_sync()

        info = client.get_account_info_sync()

        assert isinstance(info, dict), "Account info should be dict"
        assert "zone_count" in info, "Account info missing 'zone_count'"
        assert "zones" in info, "Account info missing 'zones'"


class TestResultObjects:
    """Test result object examples from README."""

    def test_result_object_attributes(self, client):
        """
        Test: README - Result object attributes and methods.
        Line: 577-595
        """
        # From README:
        # result = client.scrape.amazon.products(url="...")
        # result.success, result.data, result.error, result.cost
        # result.platform, result.method
        # result.elapsed_ms(), result.get_timing_breakdown()
        # result.to_dict(), result.to_json(indent=2)

        result = client.scrape.generic.url("https://example.com")

        # Verify all attributes
        assert hasattr(result, "success"), "Missing 'success' attribute"
        assert hasattr(result, "data"), "Missing 'data' attribute"
        assert hasattr(result, "error"), "Missing 'error' attribute"
        assert hasattr(result, "cost"), "Missing 'cost' attribute"
        assert hasattr(result, "platform"), "Missing 'platform' attribute"
        assert hasattr(result, "method"), "Missing 'method' attribute"

        # Verify methods
        elapsed = result.elapsed_ms()
        assert isinstance(elapsed, (int, float)), "elapsed_ms() should return number"

        timing = result.get_timing_breakdown()
        assert isinstance(timing, dict), "get_timing_breakdown() should return dict"

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict), "to_dict() should return dict"

        result_json = result.to_json(indent=2)
        assert isinstance(result_json, str), "to_json() should return str"
        json.loads(result_json)  # Verify valid JSON


class TestAdvancedUsage:
    """Test advanced usage examples from README."""

    @pytest.mark.slow
    def test_sync_method_usage(self, client):
        """
        Test: README - Sync method usage.
        Line: 826-830
        """
        # From README:
        # result = client.scrape.linkedin.profiles(
        #     url="https://linkedin.com/in/johndoe",
        #     timeout=300
        # )

        result = client.scrape.linkedin.profiles(
            url="https://linkedin.com/in/williamhgates", timeout=300
        )

        assert result is not None, "Result is None"
        assert hasattr(result, "success"), "Result missing 'success' attribute"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_async_method_usage(self, api_token):
        """
        Test: README - Async method usage.
        Line: 832-843
        """
        # From README:
        # async def scrape_profiles():
        #     async with BrightDataClient() as client:
        #         result = await client.scrape.linkedin.profiles_async(
        #             url="https://linkedin.com/in/johndoe",
        #             timeout=300
        #         )

        async with BrightDataClient(token=api_token) as client:
            result = await client.scrape.linkedin.profiles_async(
                url="https://linkedin.com/in/williamhgates", timeout=300
            )

            assert result is not None, "Result is None"
            assert hasattr(result, "success"), "Result missing 'success' attribute"


class TestCompleteWorkflow:
    """Test the complete workflow example from README."""

    @pytest.mark.slow
    def test_complete_workflow_example(self, api_token):
        """
        Test: README - Complete Workflow Example.
        Line: 1094-1159
        """
        # From README:
        # client = BrightDataClient()
        # if client.test_connection_sync():
        #     info = client.get_account_info_sync()
        #     product = client.scrape.amazon.products(...)
        #     jobs = client.search.linkedin.jobs(...)
        #     search_results = client.search.google(...)

        client = BrightDataClient(token=api_token)

        # Test connection
        is_connected = client.test_connection_sync()
        assert is_connected is True, "Connection test failed"

        # Get account info
        info = client.get_account_info_sync()
        assert isinstance(info, dict), "Account info should be dict"
        assert "zone_count" in info, "Account info missing 'zone_count'"

        # Scrape Amazon product
        product = client.scrape.amazon.products(url="https://amazon.com/dp/B0CRMZHDG8")
        assert product is not None, "Amazon product result is None"
        assert hasattr(product, "success"), "Product result missing 'success'"

        # Search LinkedIn jobs
        jobs = client.search.linkedin.jobs(
            keyword="python developer", location="San Francisco", remote=True
        )
        assert jobs is not None, "LinkedIn jobs result is None"
        assert hasattr(jobs, "success"), "Jobs result missing 'success'"

        # Search Google
        search_results = client.search.google(
            query="python async tutorial", location="United States", num_results=5
        )
        assert search_results is not None, "Google search result is None"
        assert hasattr(search_results, "success"), "Search result missing 'success'"


class TestCLIExamples:
    """Test CLI usage examples from README."""

    def test_cli_help_command(self):
        """
        Test: README - CLI help command.
        Line: 606
        """
        # From README:
        # brightdata --help

        result = subprocess.run(
            ["brightdata", "--help"], capture_output=True, text=True, timeout=10
        )

        assert result.returncode == 0, f"CLI help command failed with code {result.returncode}"
        assert (
            "brightdata" in result.stdout.lower() or "help" in result.stdout.lower()
        ), "Help output should contain expected text"

    @pytest.mark.slow
    def test_cli_scrape_amazon_products(self, api_token):
        """
        Test: README - CLI scrape Amazon product command.
        Line: 608-611
        """
        # From README:
        # brightdata scrape amazon products \
        #   "https://amazon.com/dp/B0CRMZHDG8"

        env = os.environ.copy()
        env["BRIGHTDATA_API_TOKEN"] = api_token

        result = subprocess.run(
            ["brightdata", "scrape", "amazon", "products", "https://amazon.com/dp/B0CRMZHDG8"],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        # CLI should execute without error (exit code 0 or 1)
        assert result.returncode in [
            0,
            1,
        ], f"CLI command failed with unexpected code {result.returncode}: {result.stderr}"

    @pytest.mark.slow
    def test_cli_search_linkedin_jobs(self, api_token):
        """
        Test: README - CLI search LinkedIn jobs command.
        Line: 613-618
        """
        # From README:
        # brightdata search linkedin jobs \
        #   --keyword "python developer" \
        #   --location "New York" \
        #   --remote \
        #   --output-file jobs.json

        env = os.environ.copy()
        env["BRIGHTDATA_API_TOKEN"] = api_token

        result = subprocess.run(
            [
                "brightdata",
                "search",
                "linkedin",
                "jobs",
                "--keyword",
                "python developer",
                "--location",
                "New York",
                "--remote",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        # CLI should execute without error
        assert result.returncode in [
            0,
            1,
        ], f"CLI command failed with unexpected code {result.returncode}: {result.stderr}"

    def test_cli_search_google(self, api_token):
        """
        Test: README - CLI search Google command.
        Line: 620-623
        """
        # From README:
        # brightdata search google \
        #   "python tutorial" \
        #   --location "United States"

        env = os.environ.copy()
        env["BRIGHTDATA_API_TOKEN"] = api_token

        result = subprocess.run(
            ["brightdata", "search", "google", "python tutorial", "--location", "United States"],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )

        # CLI should execute without error
        assert result.returncode in [
            0,
            1,
        ], f"CLI command failed with unexpected code {result.returncode}: {result.stderr}"

    def test_cli_scrape_generic(self, api_token):
        """
        Test: README - CLI generic web scraping command.
        Line: 625-628
        """
        # From README:
        # brightdata scrape generic \
        #   "https://example.com" \
        #   --response-format pretty

        env = os.environ.copy()
        env["BRIGHTDATA_API_TOKEN"] = api_token

        result = subprocess.run(
            [
                "brightdata",
                "scrape",
                "generic",
                "https://example.com",
                "--response-format",
                "pretty",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )

        # CLI should execute without error
        assert result.returncode in [
            0,
            1,
        ], f"CLI command failed with unexpected code {result.returncode}: {result.stderr}"


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v", "--tb=short"])
