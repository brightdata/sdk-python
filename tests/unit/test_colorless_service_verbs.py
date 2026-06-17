"""
Tests for the colorless-job service verbs (slice 1 of the colorless refactor).

Covers the additive service-level verbs that let a triggered job be driven by
its id alone:
  - BaseWebScraper.status / wait / fetch / to_result(snapshot_id)
  - DiscoverService.status / wait / fetch / to_result(task_id)

Also guards that the existing colored ScrapeJob methods still work (no
regression) and that the relocated logic matches the job's behavior.

Mocked at the api_client / _poll_once seam (not raw aiohttp), per the plan.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from brightdata.scrapers.amazon import AmazonScraper
from brightdata.scrapers.job import ScrapeJob
from brightdata.discover.service import DiscoverService
from brightdata.models import ScrapeResult
from brightdata.discover.models import DiscoverResult
from brightdata.exceptions import APIError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scraper_with_api(api):
    """An AmazonScraper (concrete BaseWebScraper) with its api_client mocked."""
    s = AmazonScraper(bearer_token="x" * 12)
    s.api_client = api
    return s


def _api(status="ready", data=None, status_seq=None):
    api = AsyncMock()
    if status_seq is not None:
        api.get_status.side_effect = list(status_seq)
    else:
        api.get_status.return_value = status
    api.fetch_result.return_value = data if data is not None else [{"k": 1}]
    return api


# ---------------------------------------------------------------------------
# BaseWebScraper service verbs (inherited by every scraper)
# ---------------------------------------------------------------------------


class TestScraperServiceVerbs:
    @pytest.mark.asyncio
    async def test_status_delegates_to_api_client(self):
        s = _scraper_with_api(_api(status="running"))
        assert await s.status("snap_1") == "running"
        s.api_client.get_status.assert_awaited_once_with("snap_1")

    @pytest.mark.asyncio
    async def test_fetch_delegates_to_api_client(self):
        s = _scraper_with_api(_api(data=[{"a": 1}, {"b": 2}]))
        assert await s.fetch("snap_1") == [{"a": 1}, {"b": 2}]
        s.api_client.fetch_result.assert_awaited_once_with("snap_1", format="json")

    @pytest.mark.asyncio
    async def test_wait_polls_until_ready(self):
        s = _scraper_with_api(_api(status_seq=["running", "running", "ready"]))
        assert await s.wait("snap_1", poll_interval=0) == "ready"
        assert s.api_client.get_status.await_count == 3

    @pytest.mark.asyncio
    async def test_wait_raises_on_failed_status(self):
        s = _scraper_with_api(_api(status="failed"))
        with pytest.raises(APIError):
            await s.wait("snap_1", poll_interval=0)

    @pytest.mark.asyncio
    async def test_wait_times_out(self):
        s = _scraper_with_api(_api(status="running"))
        with pytest.raises(TimeoutError):
            await s.wait("snap_1", timeout=-1, poll_interval=0)

    @pytest.mark.asyncio
    async def test_to_result_success(self):
        s = _scraper_with_api(_api(status="ready", data=[{"a": 1}, {"b": 2}]))
        res = await s.to_result("snap_1", poll_interval=0)
        assert isinstance(res, ScrapeResult)
        assert res.success is True
        assert res.data == [{"a": 1}, {"b": 2}]
        assert res.snapshot_id == "snap_1"
        assert res.platform == (s.PLATFORM_NAME or None)
        assert res.cost == 2 * s.COST_PER_RECORD  # cost from the service's class attrs

    @pytest.mark.asyncio
    async def test_to_result_failure_is_caught(self):
        s = _scraper_with_api(_api(status="error"))
        res = await s.to_result("snap_1", poll_interval=0)
        assert res.success is False
        assert res.error and "error" in res.error.lower()
        assert res.snapshot_id == "snap_1"


# ---------------------------------------------------------------------------
# Parity + regression: the colored ScrapeJob still works, and the relocated
# service verbs produce the same result as the job's methods.
# ---------------------------------------------------------------------------


class TestParityAndRegression:
    @pytest.mark.asyncio
    async def test_scrapejob_methods_still_work(self):
        api = _api(status="ready", data=[{"z": 9}])
        job = ScrapeJob(snapshot_id="snap_1", api_client=api)
        assert await job.status() == "ready"
        assert await job.fetch() == [{"z": 9}]

    @pytest.mark.asyncio
    async def test_service_verb_matches_job(self):
        api = _api(status="ready", data=[{"x": 1}])
        s = _scraper_with_api(api)
        job = ScrapeJob(snapshot_id="snap_1", api_client=api)
        assert await s.fetch("snap_1") == await job.fetch()
        assert await s.status("snap_1") == await job.status()


# ---------------------------------------------------------------------------
# DiscoverService service verbs (the previously-missing id-based path)
# ---------------------------------------------------------------------------


class TestDiscoverServiceVerbs:
    def _svc(self):
        return DiscoverService(engine=MagicMock())

    @pytest.mark.asyncio
    async def test_status_by_task_id(self):
        svc = self._svc()
        svc._poll_once = AsyncMock(return_value={"status": "done", "results": []})
        assert await svc.status("t1") == "done"
        svc._poll_once.assert_awaited_once_with("t1")

    @pytest.mark.asyncio
    async def test_fetch_by_task_id(self):
        svc = self._svc()
        svc._poll_once = AsyncMock(return_value={"status": "done", "results": [{"r": 1}]})
        assert await svc.fetch("t1") == [{"r": 1}]

    @pytest.mark.asyncio
    async def test_wait_by_task_id(self):
        svc = self._svc()
        svc._poll_until_done = AsyncMock(return_value={"status": "done", "results": []})
        assert await svc.wait("t1") == "done"
        svc._poll_until_done.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_to_result_by_task_id(self):
        svc = self._svc()
        svc._poll_until_done = AsyncMock(
            return_value={"status": "done", "results": [{"r": 1}], "duration_seconds": 1.2}
        )
        res = await svc.to_result("t1")
        assert isinstance(res, DiscoverResult)
        assert res.success is True
        assert res.total_results == 1
        assert res.task_id == "t1"

    @pytest.mark.asyncio
    async def test_to_result_failure_is_caught(self):
        svc = self._svc()
        svc._poll_until_done = AsyncMock(side_effect=APIError("Discover task failed: boom"))
        res = await svc.to_result("t1")
        assert res.success is False
        assert res.task_id == "t1"
        assert res.error and "boom" in res.error
