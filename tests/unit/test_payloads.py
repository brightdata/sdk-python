"""Tests for payload dataclasses — Validation, defaults, and serialization."""

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


# ---------------------------------------------------------------------------
# Amazon
# ---------------------------------------------------------------------------


class TestAmazonPayloads:
    def test_product_payload_valid(self):
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

    def test_product_payload_defaults(self):
        payload = AmazonProductPayload(url="https://amazon.com/dp/B123456789")
        assert payload.reviews_count is None
        assert payload.images_count is None

    def test_product_payload_rejects_non_amazon_url(self):
        with pytest.raises(ValueError, match="url must be an Amazon URL"):
            AmazonProductPayload(url="https://ebay.com/item/123")

    def test_product_payload_rejects_negative_count(self):
        with pytest.raises(ValueError, match="reviews_count must be non-negative"):
            AmazonProductPayload(url="https://amazon.com/dp/B123", reviews_count=-1)

    def test_product_payload_to_dict_excludes_none(self):
        payload = AmazonProductPayload(url="https://amazon.com/dp/B123", reviews_count=50)
        result = payload.to_dict()
        assert result == {"url": "https://amazon.com/dp/B123", "reviews_count": 50}
        assert "images_count" not in result

    def test_review_payload_valid(self):
        payload = AmazonReviewPayload(
            url="https://amazon.com/dp/B123", pastDays=30, keyWord="quality", numOfReviews=100
        )
        assert payload.pastDays == 30
        assert payload.keyWord == "quality"
        assert payload.numOfReviews == 100


# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------


class TestLinkedInPayloads:
    def test_profile_payload_valid(self):
        payload = LinkedInProfilePayload(url="https://linkedin.com/in/johndoe")
        assert payload.url == "https://linkedin.com/in/johndoe"
        assert "linkedin.com" in payload.domain

    def test_profile_payload_rejects_non_linkedin_url(self):
        with pytest.raises(ValueError, match="url must be a LinkedIn URL"):
            LinkedInProfilePayload(url="https://facebook.com/johndoe")

    def test_profile_search_payload_valid(self):
        payload = LinkedInProfileSearchPayload(firstName="John", lastName="Doe", company="Google")
        assert payload.firstName == "John"
        assert payload.lastName == "Doe"
        assert payload.company == "Google"

    def test_profile_search_rejects_empty_firstname(self):
        with pytest.raises(ValueError, match="firstName is required"):
            LinkedInProfileSearchPayload(firstName="")

    def test_job_search_payload_valid(self):
        payload = LinkedInJobSearchPayload(
            keyword="python developer", location="New York", remote=True, experienceLevel="mid"
        )
        assert payload.keyword == "python developer"
        assert payload.location == "New York"
        assert payload.remote is True
        assert payload.is_remote_search is True

    def test_job_search_rejects_no_criteria(self):
        with pytest.raises(ValueError, match="At least one search parameter required"):
            LinkedInJobSearchPayload()

    def test_job_search_rejects_invalid_country_code(self):
        with pytest.raises(ValueError, match="country must be 2-letter code"):
            LinkedInJobSearchPayload(keyword="python", country="USA")

    def test_post_search_payload_valid(self):
        payload = LinkedInPostSearchPayload(
            url="https://linkedin.com/in/johndoe", start_date="2025-01-01", end_date="2025-12-31"
        )
        assert payload.start_date == "2025-01-01"
        assert payload.end_date == "2025-12-31"

    def test_post_search_rejects_invalid_date_format(self):
        with pytest.raises(ValueError, match="start_date must be in yyyy-mm-dd format"):
            LinkedInPostSearchPayload(
                url="https://linkedin.com/in/johndoe", start_date="01-01-2025"
            )


# ---------------------------------------------------------------------------
# ChatGPT
# ---------------------------------------------------------------------------


class TestChatGPTPayloads:
    def test_prompt_payload_valid(self):
        payload = ChatGPTPromptPayload(
            prompt="Explain Python async programming", country="US", web_search=True
        )
        assert payload.prompt == "Explain Python async programming"
        assert payload.country == "US"
        assert payload.web_search is True
        assert payload.uses_web_search is True

    def test_prompt_payload_defaults(self):
        payload = ChatGPTPromptPayload(prompt="Test prompt")
        assert payload.country == "US"
        assert payload.web_search is False
        assert payload.additional_prompt is None

    def test_prompt_payload_rejects_empty_prompt(self):
        with pytest.raises(ValueError, match="prompt is required"):
            ChatGPTPromptPayload(prompt="")

    def test_prompt_payload_rejects_invalid_country(self):
        with pytest.raises(ValueError, match="country must be 2-letter code"):
            ChatGPTPromptPayload(prompt="Test", country="USA")

    def test_prompt_payload_rejects_too_long(self):
        with pytest.raises(ValueError, match="prompt too long"):
            ChatGPTPromptPayload(prompt="x" * 10001)


# ---------------------------------------------------------------------------
# Facebook
# ---------------------------------------------------------------------------


class TestFacebookPayloads:
    def test_posts_profile_payload_valid(self):
        payload = FacebookPostsProfilePayload(
            url="https://facebook.com/profile",
            num_of_posts=10,
            start_date="01-01-2025",
            end_date="12-31-2025",
        )
        assert payload.url == "https://facebook.com/profile"
        assert payload.num_of_posts == 10
        assert payload.start_date == "01-01-2025"

    def test_posts_profile_rejects_non_facebook_url(self):
        with pytest.raises(ValueError, match="url must be a Facebook URL"):
            FacebookPostsProfilePayload(url="https://twitter.com/user")

    def test_posts_group_payload_valid(self):
        payload = FacebookPostsGroupPayload(
            url="https://facebook.com/groups/example", num_of_posts=20
        )
        assert payload.url == "https://facebook.com/groups/example"
        assert payload.num_of_posts == 20

    def test_posts_group_rejects_non_group_url(self):
        with pytest.raises(ValueError, match="url must be a Facebook group URL"):
            FacebookPostsGroupPayload(url="https://facebook.com/profile")

    def test_comments_payload_valid(self):
        payload = FacebookCommentsPayload(
            url="https://facebook.com/post/123456", num_of_comments=100
        )
        assert payload.num_of_comments == 100


# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------


class TestInstagramPayloads:
    def test_profile_payload_valid(self):
        payload = InstagramProfilePayload(url="https://instagram.com/username")
        assert payload.url == "https://instagram.com/username"
        assert "instagram.com" in payload.domain

    def test_post_payload_valid(self):
        payload = InstagramPostPayload(url="https://instagram.com/p/ABC123")
        assert payload.url == "https://instagram.com/p/ABC123"
        assert payload.is_post is True

    def test_reel_payload_valid(self):
        payload = InstagramReelPayload(url="https://instagram.com/reel/ABC123")
        assert payload.url == "https://instagram.com/reel/ABC123"
        assert payload.is_reel is True

    def test_posts_discover_payload_valid(self):
        payload = InstagramPostsDiscoverPayload(
            url="https://instagram.com/username", num_of_posts=10, post_type="reel"
        )
        assert payload.num_of_posts == 10
        assert payload.post_type == "reel"

    def test_posts_discover_rejects_zero_count(self):
        with pytest.raises(ValueError, match="num_of_posts must be positive"):
            InstagramPostsDiscoverPayload(url="https://instagram.com/username", num_of_posts=0)


# ---------------------------------------------------------------------------
# Base payload behavior
# ---------------------------------------------------------------------------


class TestBasePayloadBehavior:
    def test_rejects_non_string_url(self):
        with pytest.raises(TypeError, match="url must be string"):
            AmazonProductPayload(url=123)  # type: ignore

    def test_rejects_empty_url(self):
        with pytest.raises(ValueError, match="url cannot be empty"):
            AmazonProductPayload(url="")

    def test_rejects_url_without_protocol(self):
        with pytest.raises(ValueError, match="url must be valid HTTP/HTTPS URL"):
            AmazonProductPayload(url="amazon.com/dp/B123")

    def test_url_helper_properties(self):
        payload = AmazonProductPayload(url="https://amazon.com/dp/B123")
        assert payload.domain == "amazon.com"
        assert payload.is_secure is True

        payload_http = FacebookPostPayload(url="http://facebook.com/post/123")
        assert payload_http.is_secure is False

    def test_to_dict_excludes_none_values(self):
        payload = AmazonProductPayload(url="https://amazon.com/dp/B123", reviews_count=50)
        result = payload.to_dict()
        assert "images_count" not in result
        assert "reviews_count" in result


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------


class TestPayloadIntegration:
    def test_full_lifecycle(self):
        payload = LinkedInJobSearchPayload(
            keyword="python developer", location="New York", remote=True
        )
        assert payload.is_remote_search is True

        api_dict = payload.to_dict()
        assert api_dict["keyword"] == "python developer"
        assert api_dict["remote"] is True
        assert "url" not in api_dict
        assert "company" not in api_dict

    def test_consistent_interface_across_types(self):
        payloads = [
            AmazonProductPayload(url="https://amazon.com/dp/B123"),
            LinkedInProfilePayload(url="https://linkedin.com/in/johndoe"),
            FacebookPostPayload(url="https://facebook.com/post/123"),
            InstagramPostPayload(url="https://instagram.com/p/ABC123"),
        ]

        for payload in payloads:
            assert hasattr(payload, "url")
            assert hasattr(payload, "domain")
            assert hasattr(payload, "is_secure")
            assert hasattr(payload, "to_dict")
            assert callable(payload.to_dict)
