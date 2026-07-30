"""
Tests for ScraperCore — the shared construction core for collect + search scrapers.

Before ScraperCore, the 7 search classes each hand-copied the same __init__
(token resolution, engine reuse-or-create, DatasetAPIClient, WorkflowExecutor)
and had drifted (Amazon/ChatGPT/LinkedIn lacked the env-token fallback). These
tests pin the consolidated behavior.
"""

import pytest
from unittest.mock import MagicMock

from brightdata.exceptions import ValidationError
from brightdata.scrapers.base import BaseWebScraper, ScraperCore
from brightdata.scrapers.amazon.search import AmazonSearchScraper
from brightdata.scrapers.chatgpt.search import ChatGPTSearchService
from brightdata.scrapers.instagram.search import InstagramSearchScraper
from brightdata.scrapers.linkedin.search import LinkedInSearchScraper
from brightdata.scrapers.pinterest.search import PinterestSearchScraper
from brightdata.scrapers.tiktok.search import TikTokSearchScraper
from brightdata.scrapers.youtube.search import YouTubeSearchScraper

SEARCH_CLASSES = [
    AmazonSearchScraper,
    ChatGPTSearchService,
    InstagramSearchScraper,
    LinkedInSearchScraper,
    PinterestSearchScraper,
    TikTokSearchScraper,
    YouTubeSearchScraper,
]

EXPECTED_PLATFORMS = {
    AmazonSearchScraper: "amazon",
    ChatGPTSearchService: "chatgpt",
    InstagramSearchScraper: "instagram",
    LinkedInSearchScraper: "linkedin",
    PinterestSearchScraper: "pinterest",
    TikTokSearchScraper: "tiktok",
    YouTubeSearchScraper: "youtube",
}

TOKEN = "x" * 20


class TestHierarchy:
    def test_search_classes_inherit_scraper_core(self):
        for cls in SEARCH_CLASSES:
            assert issubclass(cls, ScraperCore), cls.__name__

    def test_base_web_scraper_inherits_scraper_core(self):
        assert issubclass(BaseWebScraper, ScraperCore)

    def test_search_classes_do_not_gain_scrape_surface(self):
        """Search classes take the core only — not BaseWebScraper's URL-scrape API."""
        for cls in SEARCH_CLASSES:
            assert not issubclass(cls, BaseWebScraper), cls.__name__
            assert not hasattr(cls, "scrape_async"), cls.__name__


class TestConstruction:
    @pytest.mark.parametrize("cls", SEARCH_CLASSES, ids=lambda c: c.__name__)
    def test_wires_engine_api_client_workflow(self, cls):
        engine = MagicMock()
        s = cls(bearer_token=TOKEN, engine=engine)
        assert s.bearer_token == TOKEN
        assert s.engine is engine
        assert s.api_client.engine is engine
        assert s.workflow_executor.api_client is s.api_client
        assert s.workflow_executor.platform_name == EXPECTED_PLATFORMS[cls]
        assert s.workflow_executor.cost_per_record == cls.COST_PER_RECORD

    @pytest.mark.parametrize("cls", SEARCH_CLASSES, ids=lambda c: c.__name__)
    def test_env_token_fallback(self, cls, monkeypatch):
        """All search classes resolve BRIGHTDATA_API_TOKEN (Amazon/ChatGPT/LinkedIn
        previously required an explicit bearer_token)."""
        monkeypatch.setenv("BRIGHTDATA_API_TOKEN", "tok_from_env_12345")
        s = cls(engine=MagicMock())
        assert s.bearer_token == "tok_from_env_12345"

    @pytest.mark.parametrize("cls", SEARCH_CLASSES, ids=lambda c: c.__name__)
    def test_missing_token_raises(self, cls, monkeypatch):
        monkeypatch.delenv("BRIGHTDATA_API_TOKEN", raising=False)
        with pytest.raises(ValidationError):
            cls(engine=MagicMock())

    def test_positional_token_still_works(self):
        """Amazon/ChatGPT/LinkedIn callers pass bearer_token positionally."""
        for cls in (AmazonSearchScraper, ChatGPTSearchService, LinkedInSearchScraper):
            assert cls(TOKEN).bearer_token == TOKEN


class TestContextManager:
    @pytest.mark.parametrize("cls", SEARCH_CLASSES, ids=lambda c: c.__name__)
    async def test_aenter_aexit_drive_engine(self, cls):
        engine = MagicMock()

        async def _noop(*a, **k):
            return engine

        engine.__aenter__ = _noop
        engine.__aexit__ = _noop
        s = cls(bearer_token=TOKEN, engine=engine)
        assert await s.__aenter__() is s
        await s.__aexit__(None, None, None)
