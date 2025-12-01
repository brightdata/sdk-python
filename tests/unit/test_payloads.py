"""
Tests for dataclass-based payloads.

Tests validate:
- Runtime validation
- Default values
- Helper methods and properties
- Error handling
- Conversion to dict
"""

import pytest
from brightdata.payloads import (
    # Amazon
    AmazonProductPayload,
    AmazonReviewPayload,
    LinkedInProfilePayload,
    LinkedInProfileSearchPayload,
    LinkedInJobSearchPayload,
    LinkedInPostSearchPayload,
    # ChatGPT
    ChatGPTPromptPayload,
    # Facebook
    FacebookPostsProfilePayload,
    FacebookPostsGroupPayload,
    FacebookPostPayload,
    FacebookCommentsPayload,
    InstagramProfilePayload,
    InstagramPostPayload,
    InstagramReelPayload,
    InstagramPostsDiscoverPayload,
)


class TestAmazonPayloads:
    """Test Amazon payload dataclasses."""

    def test_amazon_product_payload_valid(self):
        """Test valid Amazon product payload."""
        payload = AmazonProductPayload(
            url="https://amazon.com/dp/B0CRMZHDG8", reviews_count=50, images_count=10
        )

        assert payload.url == "https://amazon.com/dp/B0CRMZHDG8"
        assert payload.reviews_count == 50
        assert payload.images_count == 10
        assert payload.asin == "B0CRMZHDG8"
        assert payload.is_product_url is True
        assert payload.domain == "amazon.com"
        assert payload.is_secure is True

    def test_amazon_product_payload_defaults(self):
        """Test Amazon product payload with defaults."""
        payload = AmazonProductPayload(url="https://amazon.com/dp/B123456789")

        assert payload.reviews_count is None
        assert payload.images_count is None

    def test_amazon_product_payload_invalid_url(self):
        """Test Amazon product payload with invalid URL."""
        with pytest.raises(ValueError, match="url must be an Amazon URL"):
            AmazonProductPayload(url="https://ebay.com/item/123")

    def test_amazon_product_payload_negative_count(self):
        """Test Amazon product payload with negative count."""
        with pytest.raises(ValueError, match="reviews_count must be non-negative"):
            AmazonProductPayload(url="https://amazon.com/dp/B123", reviews_count=-1)

    def test_amazon_product_payload_to_dict(self):
        """Test converting Amazon product payload to dict."""
        payload = AmazonProductPayload(url="https://amazon.com/dp/B123", reviews_count=50)

        result = payload.to_dict()
        assert result == {"url": "https://amazon.com/dp/B123", "reviews_count": 50}
        # images_count (None) should not be in dict
        assert "images_count" not in result

    def test_amazon_review_payload_valid(self):
        """Test valid Amazon review payload."""
        payload = AmazonReviewPayload(
            url="https://amazon.com/dp/B123", pastDays=30, keyWord="quality", numOfReviews=100
        )

        assert payload.pastDays == 30
        assert payload.keyWord == "quality"
        assert payload.numOfReviews == 100


class TestLinkedInPayloads:
    """Test LinkedIn payload dataclasses."""

    def test_linkedin_profile_payload_valid(self):
        """Test valid LinkedIn profile payload."""
        payload = LinkedInProfilePayload(url="https://linkedin.com/in/johndoe")

        assert payload.url == "https://linkedin.com/in/johndoe"
        assert "linkedin.com" in payload.domain

    def test_linkedin_profile_payload_invalid_url(self):
        """Test LinkedIn profile payload with invalid URL."""
        with pytest.raises(ValueError, match="url must be a LinkedIn URL"):
            LinkedInProfilePayload(url="https://facebook.com/johndoe")

    def test_linkedin_profile_search_payload_valid(self):
        """Test valid LinkedIn profile search payload."""
        payload = LinkedInProfileSearchPayload(firstName="John", lastName="Doe", company="Google")

        assert payload.firstName == "John"
        assert payload.lastName == "Doe"
        assert payload.company == "Google"

    def test_linkedin_profile_search_payload_empty_firstname(self):
        """Test LinkedIn profile search with empty firstName."""
        with pytest.raises(ValueError, match="firstName is required"):
            LinkedInProfileSearchPayload(firstName="")

    def test_linkedin_job_search_payload_valid(self):
        """Test valid LinkedIn job search payload."""
        payload = LinkedInJobSearchPayload(
            keyword="python developer", location="New York", remote=True, experienceLevel="mid"
        )

        assert payload.keyword == "python developer"
        assert payload.location == "New York"
        assert payload.remote is True
        assert payload.is_remote_search is True

    def test_linkedin_job_search_payload_no_criteria(self):
        """Test LinkedIn job search with no search criteria."""
        with pytest.raises(ValueError, match="At least one search parameter required"):
            LinkedInJobSearchPayload()

    def test_linkedin_job_search_payload_invalid_country(self):
        """Test LinkedIn job search with invalid country code."""
        with pytest.raises(ValueError, match="country must be 2-letter code"):
            LinkedInJobSearchPayload(keyword="python", country="USA")  # Should be "US"

    def test_linkedin_post_search_payload_valid(self):
        """Test valid LinkedIn post search payload."""
        payload = LinkedInPostSearchPayload(
            url="https://linkedin.com/in/johndoe", start_date="2025-01-01", end_date="2025-12-31"
        )

        assert payload.start_date == "2025-01-01"
        assert payload.end_date == "2025-12-31"

    def test_linkedin_post_search_payload_invalid_date(self):
        """Test LinkedIn post search with invalid date format."""
        with pytest.raises(ValueError, match="start_date must be in yyyy-mm-dd format"):
            LinkedInPostSearchPayload(
                url="https://linkedin.com/in/johndoe", start_date="01-01-2025"  # Wrong format
            )


class TestChatGPTPayloads:
    """Test ChatGPT payload dataclasses."""

    def test_chatgpt_prompt_payload_valid(self):
        """Test valid ChatGPT prompt payload."""
        payload = ChatGPTPromptPayload(
            prompt="Explain Python async programming", country="US", web_search=True
        )

        assert payload.prompt == "Explain Python async programming"
        assert payload.country == "US"
        assert payload.web_search is True
        assert payload.uses_web_search is True

    def test_chatgpt_prompt_payload_defaults(self):
        """Test ChatGPT prompt payload defaults."""
        payload = ChatGPTPromptPayload(prompt="Test prompt")

        assert payload.country == "US"
        assert payload.web_search is False
        assert payload.additional_prompt is None

    def test_chatgpt_prompt_payload_empty_prompt(self):
        """Test ChatGPT payload with empty prompt."""
        with pytest.raises(ValueError, match="prompt is required"):
            ChatGPTPromptPayload(prompt="")

    def test_chatgpt_prompt_payload_invalid_country(self):
        """Test ChatGPT payload with invalid country code."""
        with pytest.raises(ValueError, match="country must be 2-letter code"):
            ChatGPTPromptPayload(prompt="Test", country="USA")  # Should be "US"

    def test_chatgpt_prompt_payload_too_long(self):
        """Test ChatGPT payload with prompt too long."""
        with pytest.raises(ValueError, match="prompt too long"):
            ChatGPTPromptPayload(prompt="x" * 10001)


class TestFacebookPayloads:
    """Test Facebook payload dataclasses."""

    def test_facebook_posts_profile_payload_valid(self):
        """Test valid Facebook posts profile payload."""
        payload = FacebookPostsProfilePayload(
            url="https://facebook.com/profile",
            num_of_posts=10,
            start_date="01-01-2025",
            end_date="12-31-2025",
        )

        assert payload.url == "https://facebook.com/profile"
        assert payload.num_of_posts == 10
        assert payload.start_date == "01-01-2025"

    def test_facebook_posts_profile_payload_invalid_url(self):
        """Test Facebook payload with invalid URL."""
        with pytest.raises(ValueError, match="url must be a Facebook URL"):
            FacebookPostsProfilePayload(url="https://twitter.com/user")

    def test_facebook_posts_group_payload_valid(self):
        """Test valid Facebook posts group payload."""
        payload = FacebookPostsGroupPayload(
            url="https://facebook.com/groups/example", num_of_posts=20
        )

        assert payload.url == "https://facebook.com/groups/example"
        assert payload.num_of_posts == 20

    def test_facebook_posts_group_payload_not_group(self):
        """Test Facebook group payload without /groups/ in URL."""
        with pytest.raises(ValueError, match="url must be a Facebook group URL"):
            FacebookPostsGroupPayload(url="https://facebook.com/profile")

    def test_facebook_comments_payload_valid(self):
        """Test valid Facebook comments payload."""
        payload = FacebookCommentsPayload(
            url="https://facebook.com/post/123456", num_of_comments=100
        )

        assert payload.num_of_comments == 100


class TestInstagramPayloads:
    """Test Instagram payload dataclasses."""

    def test_instagram_profile_payload_valid(self):
        """Test valid Instagram profile payload."""
        payload = InstagramProfilePayload(url="https://instagram.com/username")

        assert payload.url == "https://instagram.com/username"
        assert "instagram.com" in payload.domain

    def test_instagram_post_payload_valid(self):
        """Test valid Instagram post payload."""
        payload = InstagramPostPayload(url="https://instagram.com/p/ABC123")

        assert payload.url == "https://instagram.com/p/ABC123"
        assert payload.is_post is True

    def test_instagram_reel_payload_valid(self):
        """Test valid Instagram reel payload."""
        payload = InstagramReelPayload(url="https://instagram.com/reel/ABC123")

        assert payload.url == "https://instagram.com/reel/ABC123"
        assert payload.is_reel is True

    def test_instagram_posts_discover_payload_valid(self):
        """Test valid Instagram posts discover payload."""
        payload = InstagramPostsDiscoverPayload(
            url="https://instagram.com/username", num_of_posts=10, post_type="reel"
        )

        assert payload.num_of_posts == 10
        assert payload.post_type == "reel"

    def test_instagram_posts_discover_payload_invalid_count(self):
        """Test Instagram discover payload with invalid count."""
        with pytest.raises(ValueError, match="num_of_posts must be positive"):
            InstagramPostsDiscoverPayload(url="https://instagram.com/username", num_of_posts=0)


class TestBasePayload:
    """Test base payload functionality."""

    def test_url_payload_invalid_type(self):
        """Test URL payload with invalid type."""
        with pytest.raises(TypeError, match="url must be string"):
            AmazonProductPayload(url=123)  # type: ignore

    def test_url_payload_empty(self):
        """Test URL payload with empty string."""
        with pytest.raises(ValueError, match="url cannot be empty"):
            AmazonProductPayload(url="")

    def test_url_payload_no_protocol(self):
        """Test URL payload without protocol."""
        with pytest.raises(ValueError, match="url must be valid HTTP/HTTPS URL"):
            AmazonProductPayload(url="amazon.com/dp/B123")

    def test_url_payload_properties(self):
        """Test URL payload helper properties."""
        payload = AmazonProductPayload(url="https://amazon.com/dp/B123")

        assert payload.domain == "amazon.com"
        assert payload.is_secure is True

        # Test non-HTTPS
        payload_http = FacebookPostPayload(url="http://facebook.com/post/123")
        assert payload_http.is_secure is False

    def test_to_dict_excludes_none(self):
        """Test to_dict() excludes None values."""
        payload = AmazonProductPayload(
            url="https://amazon.com/dp/B123",
            reviews_count=50,
            # images_count not provided (None)
        )

        result = payload.to_dict()
        assert "images_count" not in result
        assert "reviews_count" in result


class TestPayloadIntegration:
    """Integration tests for payload usage."""

    def test_payload_lifecycle(self):
        """Test complete payload lifecycle."""
        # Create payload with validation
        payload = LinkedInJobSearchPayload(
            keyword="python developer", location="New York", remote=True
        )

        # Check properties work
        assert payload.is_remote_search is True

        # Convert to dict for API call
        api_dict = payload.to_dict()
        assert api_dict["keyword"] == "python developer"
        assert api_dict["remote"] is True

        # Verify None values excluded
        assert "url" not in api_dict
        assert "company" not in api_dict

    def test_multiple_payloads_consistency(self):
        """Test consistency across different payload types."""
        payloads = [
            AmazonProductPayload(url="https://amazon.com/dp/B123"),
            LinkedInProfilePayload(url="https://linkedin.com/in/johndoe"),
            FacebookPostPayload(url="https://facebook.com/post/123"),
            InstagramPostPayload(url="https://instagram.com/p/ABC123"),
        ]

        # All should have consistent interface
        for payload in payloads:
            assert hasattr(payload, "url")
            assert hasattr(payload, "domain")
            assert hasattr(payload, "is_secure")
            assert hasattr(payload, "to_dict")
            assert callable(payload.to_dict)
