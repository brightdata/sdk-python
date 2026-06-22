"""
Tests for the X (Twitter) scraper — the 5 variants from devdocs/x/1.md.

Asserts each variant sends the right dataset_id, payload shape, and discover
params (type=discover_new & discover_by=...). Mocked at the api_client / workflow
boundary — no network.
"""

import asyncio

from unittest.mock import AsyncMock, MagicMock

from brightdata.scrapers.x.scraper import XScraper
from brightdata.scrapers.registry import get_scraper_for
from brightdata.models import ScrapeResult
from brightdata.sync_client import SyncXScraper

POSTS = "gd_lwxkxvnf1cynvib9co"
PROFILES = "gd_lwxmeb2u1cniijd7t4"


def _scraper() -> XScraper:
    s = XScraper(bearer_token="x" * 12, engine=MagicMock())
    s.api_client = MagicMock()
    s.api_client.trigger = AsyncMock(return_value="snap1")
    return s


def _trigger_kwargs(s: XScraper) -> dict:
    return s.api_client.trigger.await_args.kwargs


# ---------------------------------------------------------------------------
# Per-variant trigger payload / dataset / discover params
# ---------------------------------------------------------------------------


class TestXTriggerPayloads:
    async def test_v1_posts_by_url(self):
        s = _scraper()
        await s.posts_trigger("https://x.com/CNN/status/1796673270344810776")
        kw = _trigger_kwargs(s)
        assert kw["dataset_id"] == POSTS
        assert kw["payload"] == [{"url": "https://x.com/CNN/status/1796673270344810776"}]
        assert "extra_params" not in kw  # plain collect, no discover

    async def test_v2_posts_by_profile(self):
        s = _scraper()
        await s.posts_by_profile_trigger(
            "https://x.com/elonmusk", start_date="2023-01-15", end_date="2024-03-15"
        )
        kw = _trigger_kwargs(s)
        assert kw["dataset_id"] == POSTS
        assert kw["payload"] == [
            {
                "url": "https://x.com/elonmusk",
                "start_date": "2023-01-15",
                "end_date": "2024-03-15",
            }
        ]
        assert kw["extra_params"] == {"type": "discover_new", "discover_by": "profile_url"}

    async def test_v2_dates_default_to_empty_string(self):
        s = _scraper()
        await s.posts_by_profile_trigger("https://x.com/fabrizioromano")
        payload = _trigger_kwargs(s)["payload"]
        assert payload[0]["start_date"] == ""
        assert payload[0]["end_date"] == ""

    async def test_v3_posts_by_profiles_array(self):
        s = _scraper()
        urls = ["https://x.com/NextLifeAdFlow", "https://x.com/BSCNews"]
        await s.posts_by_profiles_array_trigger(urls)
        kw = _trigger_kwargs(s)
        assert kw["dataset_id"] == POSTS
        # one input row carrying the whole array
        assert kw["payload"] == [{"urls": urls, "start_date": "", "end_date": ""}]
        assert kw["extra_params"] == {"type": "discover_new", "discover_by": "profiles_array"}

    async def test_v4_profiles_by_url(self):
        s = _scraper()
        await s.profiles_trigger("https://x.com/elonmusk", max_number_of_posts=100)
        kw = _trigger_kwargs(s)
        assert kw["dataset_id"] == PROFILES
        assert kw["payload"] == [{"url": "https://x.com/elonmusk", "max_number_of_posts": 100}]
        assert "extra_params" not in kw

    async def test_v4_profiles_omits_max_when_none(self):
        s = _scraper()
        await s.profiles_trigger("https://x.com/cnn")
        assert _trigger_kwargs(s)["payload"] == [{"url": "https://x.com/cnn"}]

    async def test_v5_profiles_by_username(self):
        s = _scraper()
        await s.profiles_by_username_trigger(["elonmusk", "BillGates"])
        kw = _trigger_kwargs(s)
        assert kw["dataset_id"] == PROFILES
        assert kw["payload"] == [{"user_name": "elonmusk"}, {"user_name": "BillGates"}]
        assert kw["extra_params"] == {"type": "discover_new", "discover_by": "user_name"}


# ---------------------------------------------------------------------------
# Full path (execute) — dataset + payload threaded correctly
# ---------------------------------------------------------------------------


class TestXFullPath:
    async def test_posts_uses_posts_dataset_and_unwraps_single(self):
        s = _scraper()
        s.workflow_executor.execute = AsyncMock(
            return_value=ScrapeResult(success=True, data=[{"id": 1}])
        )
        res = await s.posts("https://x.com/CNN/status/1796673270344810776")
        kw = s.workflow_executor.execute.await_args.kwargs
        assert kw["dataset_id"] == POSTS
        assert kw["payload"] == [{"url": "https://x.com/CNN/status/1796673270344810776"}]
        assert "extra_params" not in kw
        assert res.success and res.data == {"id": 1}  # single URL unwrapped

    async def test_profiles_by_username_full_path_discover(self):
        s = _scraper()
        s.workflow_executor.execute = AsyncMock(
            return_value=ScrapeResult(success=True, data=[{"u": 1}])
        )
        await s.profiles_by_username("elonmusk")
        kw = s.workflow_executor.execute.await_args.kwargs
        assert kw["dataset_id"] == PROFILES
        assert kw["payload"] == [{"user_name": "elonmusk"}]
        assert kw["extra_params"] == {"type": "discover_new", "discover_by": "user_name"}


# ---------------------------------------------------------------------------
# Wiring: registry + sync wrapper
# ---------------------------------------------------------------------------


class TestXWiring:
    def test_registered_for_x_domain(self):
        assert get_scraper_for("https://x.com/elonmusk") is XScraper

    def test_sync_wrapper_delegates(self):
        loop = asyncio.new_event_loop()
        try:
            api = MagicMock()
            api.posts = AsyncMock(return_value=ScrapeResult(success=True, data=[{"p": 1}]))
            api.profiles_by_username = AsyncMock(return_value=ScrapeResult(success=True, data=[]))
            s = SyncXScraper(api, loop)
            assert s.posts("https://x.com/u/status/1").data == [{"p": 1}]
            api.posts.assert_awaited_once()
            s.profiles_by_username("elonmusk")
            api.profiles_by_username.assert_awaited_once()
        finally:
            loop.close()


class _FakeTriggerResponse:
    status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def json(self):
        return {"snapshot_id": "s1"}


class TestXLimitPerInput:
    async def test_forwarded_on_discover_trigger(self):
        s = _scraper()
        await s.posts_by_profile_trigger("https://x.com/elonmusk", limit_per_input=2)
        assert _trigger_kwargs(s)["limit_per_input"] == 2

    async def test_forwarded_on_collect_trigger(self):
        s = _scraper()
        await s.posts_trigger("https://x.com/u/status/1", limit_per_input=5)
        assert _trigger_kwargs(s)["limit_per_input"] == 5

    async def test_none_by_default(self):
        s = _scraper()
        await s.profiles_by_username_trigger("elonmusk")
        assert _trigger_kwargs(s).get("limit_per_input") is None


class TestTriggerBodyWrapping:
    """api_client.trigger sends a bare array by default, wrapped body with a limit."""

    def _client_capturing(self, captured):
        from brightdata.scrapers.api_client import DatasetAPIClient

        engine = MagicMock()

        def post_to_url(url, json_data=None, params=None):
            captured["body"] = json_data
            return _FakeTriggerResponse()

        engine.post_to_url = post_to_url
        return DatasetAPIClient(engine)

    async def test_bare_array_without_limit(self):
        captured = {}
        c = self._client_capturing(captured)
        await c.trigger(payload=[{"url": "u"}], dataset_id="d")
        assert captured["body"] == [{"url": "u"}]

    async def test_wrapped_with_limit(self):
        captured = {}
        c = self._client_capturing(captured)
        await c.trigger(payload=[{"url": "u"}], dataset_id="d", limit_per_input=2)
        assert captured["body"] == {"input": [{"url": "u"}], "limit_per_input": 2}
