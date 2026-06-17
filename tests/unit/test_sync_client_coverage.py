"""
Tests for the sync-client parity coverage (Steps 1-5 of the plan).

Two kinds of tests:
  1. Drift-proof parity — derive the async surface (ScrapeService / SearchService
     properties) and assert SyncBrightDataClient exposes every one, plus datasets.
     Adding an async scraper without a sync wrapper will fail these automatically.
  2. Functional — the new sync wrapper classes correctly delegate to their async
     object on the persistent loop (tested in isolation with an AsyncMock async
     object + a real loop, so no network and no full-client __enter__ needed).
"""

import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock

from brightdata import SyncBrightDataClient
from brightdata.models import ScrapeResult
from brightdata.discover.models import DiscoverSnapshot
from brightdata.scrapers.service import ScrapeService
from brightdata.serp.service import SearchService
from brightdata.sync_client import (
    SyncDatasetsClient,
    SyncDataset,
    SyncRedditScraper,
    SyncTikTokScraper,
    SyncYouTubeScraper,
    SyncPerplexityScraper,
    SyncDigiKeyScraper,
    SyncTikTokSearchScraper,
    SyncYouTubeSearchScraper,
    SyncInstagramSearchScraper,
)


@pytest.fixture
def loop():
    lp = asyncio.new_event_loop()
    yield lp
    lp.close()


def _client():
    # Constructed, not entered: enough for structural/parity checks (no loop/network).
    return SyncBrightDataClient(token="x" * 12)


# ---------------------------------------------------------------------------
# Drift-proof parity (structural; no loop needed)
# ---------------------------------------------------------------------------


class TestParity:
    def test_datasets_property_exists(self):
        """The 1.md bug: SyncBrightDataClient must expose `datasets`."""
        c = _client()
        assert hasattr(c, "datasets")
        # dynamic dataset access resolves to a SyncDataset with the full method set
        imdb = c.datasets.imdb_movies
        for m in ("download", "get_status", "sample", "get_metadata"):
            assert hasattr(imdb, m)

    def test_scrape_surface_matches_async(self):
        async_scrapers = [n for n, v in vars(ScrapeService).items() if isinstance(v, property)]
        c = _client()
        missing = [n for n in async_scrapers if not hasattr(c.scrape, n)]
        assert not missing, f"sync scrape missing async scrapers: {missing}"

    def test_search_surface_matches_async(self):
        async_search = [n for n, v in vars(SearchService).items() if isinstance(v, property)]
        c = _client()
        missing = [n for n in async_search if not hasattr(c.search, n)]
        assert not missing, f"sync search missing async verticals: {missing}"

    def test_instagram_search_partials(self):
        c = _client()
        for m in ("posts", "reels", "profiles", "reels_all"):
            assert hasattr(c.search.instagram, m)

    def test_pinterest_trigger_poll(self):
        c = _client()
        for m in (
            "posts_trigger",
            "posts_status",
            "posts_fetch",
            "profiles_trigger",
            "profiles_status",
            "profiles_fetch",
        ):
            assert hasattr(c.scrape.pinterest, m)


# ---------------------------------------------------------------------------
# Functional: the new wrappers delegate to async on the loop (isolated)
# ---------------------------------------------------------------------------


class TestDatasetsWrapper:
    def test_dataset_call_returns_snapshot_id(self, loop):
        async_ds = AsyncMock(return_value="snap_123")  # calling it -> snapshot_id
        async_ds.download = AsyncMock(return_value=[{"r": 1}])
        sd = SyncDataset(async_ds, loop)
        sid = sd(filter={"name": "year", "operator": "=", "value": 2024}, records_limit=10)
        assert sid == "snap_123"
        assert sd.download(sid) == [{"r": 1}]

    def test_datasets_client_getattr(self, loop):
        async_datasets = MagicMock()
        async_datasets.imdb_movies = AsyncMock(return_value="snap_1")
        async_datasets.imdb_movies.download = AsyncMock(return_value=[{"x": 1}])
        sdc = SyncDatasetsClient(async_datasets, loop)
        assert sdc.imdb_movies(filter={}, records_limit=5) == "snap_1"
        assert sdc.imdb_movies.download("snap_1") == [{"x": 1}]

    def test_datasets_client_private_attr_guarded(self, loop):
        sdc = SyncDatasetsClient(MagicMock(), loop)
        with pytest.raises(AttributeError):
            _ = sdc._not_a_dataset


class TestScraperWrappers:
    def test_reddit_posts_delegates(self, loop):
        api = MagicMock()
        api.posts = AsyncMock(return_value=ScrapeResult(success=True, data=[{"p": 1}]))
        s = SyncRedditScraper(api, loop)
        res = s.posts("https://reddit.com/r/python/...")
        assert res.success and res.data == [{"p": 1}]
        api.posts.assert_awaited_once()

    def test_tiktok_trigger_status_fetch(self, loop):
        api = MagicMock()
        api.posts_trigger = AsyncMock(return_value="JOB")  # whatever async returns (job/snapshot)
        api.posts_status = AsyncMock(return_value="ready")
        api.posts_fetch = AsyncMock(return_value=[{"v": 1}])
        s = SyncTikTokScraper(api, loop)
        assert s.posts_trigger("u") == "JOB"
        assert s.posts_status("sid") == "ready"
        assert s.posts_fetch("sid") == [{"v": 1}]

    def test_perplexity_and_digikey_resolve(self, loop):
        api = MagicMock()
        api.search = AsyncMock(return_value="ok")
        assert SyncPerplexityScraper(api, loop).search("q") == "ok"
        api2 = MagicMock()
        api2.discover_by_category = AsyncMock(return_value="cat")
        assert SyncDigiKeyScraper(api2, loop).discover_by_category("u") == "cat"

    def test_youtube_videos_delegates(self, loop):
        api = MagicMock()
        api.videos = AsyncMock(return_value=ScrapeResult(success=True, data=[{"y": 1}]))
        assert SyncYouTubeScraper(api, loop).videos("u").data == [{"y": 1}]


class TestSearchWrappers:
    def test_youtube_search_delegates(self, loop):
        api = MagicMock()
        api.videos_by_keyword = AsyncMock(return_value="SR")
        assert SyncYouTubeSearchScraper(api, loop).videos_by_keyword("python") == "SR"

    def test_tiktok_search_delegates(self, loop):
        api = MagicMock()
        api.posts_by_keyword = AsyncMock(return_value="SR")
        assert SyncTikTokSearchScraper(api, loop).posts_by_keyword("#x") == "SR"

    def test_instagram_search_new_methods(self, loop):
        api = MagicMock()
        api.profiles = AsyncMock(return_value="P")
        api.reels_all = AsyncMock(return_value="R")
        s = SyncInstagramSearchScraper(api, loop)
        assert s.profiles("u") == "P"
        assert s.reels_all("u") == "R"


class TestDiscoverSyncPath:
    """Discover's sync manual path — the one subsystem that had none before."""

    def _client(self, loop):
        c = SyncBrightDataClient(token="x" * 12)
        c._loop = loop  # inject the loop; do NOT enter the context (no network)
        return c

    def test_discover_trigger_returns_colorless_snapshot(self, loop):
        c = self._client(loop)
        fake_job = MagicMock(task_id="t1", query="q", intent="i")
        c._async_client.discover_trigger = AsyncMock(return_value=fake_job)
        snap = c.discover_trigger("q", intent="i")
        assert isinstance(snap, DiscoverSnapshot)
        assert (snap.task_id, snap.query, snap.intent) == ("t1", "q", "i")
        # colorless: no I/O methods on the handle
        assert not hasattr(snap, "fetch")

    def test_discover_status_wait_fetch_by_task_id(self, loop):
        c = self._client(loop)
        svc = MagicMock()
        svc.status = AsyncMock(return_value="done")
        svc.wait = AsyncMock(return_value="done")
        svc.fetch = AsyncMock(return_value=[{"r": 1}])
        c._async_client._discover_service = svc
        assert c.discover_status("t1") == "done"
        assert c.discover_wait("t1") == "done"
        assert c.discover_fetch("t1") == [{"r": 1}]

    def test_discover_service_is_ensured_when_missing(self, loop):
        c = self._client(loop)
        c._async_client._discover_service = None  # not yet created
        svc = c._discover_service()
        assert svc is not None and c._async_client._discover_service is svc
