"""
Tests for engine-level HTTP error translation and structured exceptions.

Covers: per-status translation at the choke point, the 202 pass-through that
protects the SDK's only recovery path, `retryable` correctness (the
duplicate-job guard), export surface, and back-compat of the exception
constructors.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

import brightdata
import brightdata.exceptions as ex
from brightdata.core.engine import AsyncEngine
from brightdata.exceptions import (
    APIError,
    AuthenticationError,
    BrightDataError,
    DataNotReadyError,
    RateLimitError,
)
from brightdata.utils.http import parse_retry_after, status_phrase
from brightdata.utils.retry import is_retryable


def _resp(status, text="body", headers=None):
    r = AsyncMock()
    r.status = status
    r.text = AsyncMock(return_value=text)
    r.release = AsyncMock()
    r.close = MagicMock()  # aiohttp's close() is sync
    r.headers = headers or {}
    return r


async def _enter(engine, response):
    """Send one request through the engine with a canned response."""
    engine._session.request = AsyncMock(return_value=response)
    async with engine.get("/test") as r:
        return r


# ---------------------------------------------------------------------------
# Per-status translation
# ---------------------------------------------------------------------------


class TestStatusTranslation:
    @pytest.mark.parametrize("status", [401, 403])
    async def test_auth_statuses(self, status):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with pytest.raises(AuthenticationError) as ei:
                await _enter(engine, _resp(status, "nope"))
            assert ei.value.status_code == status
            assert ei.value.raw == "nope"
            assert ei.value.retryable is False

    @pytest.mark.parametrize("status", [400, 404, 422])
    async def test_client_errors_are_api_error_not_retryable(self, status):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with pytest.raises(APIError) as ei:
                await _enter(engine, _resp(status))
            assert not isinstance(ei.value, RateLimitError)
            assert ei.value.status_code == status
            assert ei.value.retryable is False

    @pytest.mark.parametrize("status", [500, 502, 503])
    async def test_server_errors_are_retryable(self, status):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with pytest.raises(APIError) as ei:
                await _enter(engine, _resp(status))
            assert ei.value.status_code == status
            assert ei.value.retryable is True

    async def test_429_becomes_rate_limit_error_with_retry_after(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with pytest.raises(RateLimitError) as ei:
                await _enter(engine, _resp(429, "slow down", {"Retry-After": "30"}))
            assert ei.value.status_code == 429
            assert ei.value.retry_after == 30.0
            assert ei.value.retryable is False

    async def test_429_with_non_json_body_is_not_a_parse_error(self):
        """The field case: a bare string under a non-JSON content type."""
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with pytest.raises(RateLimitError) as ei:
                await _enter(engine, _resp(429, "too_many_parallel_jobs"))
            assert "too_many_parallel_jobs" in ei.value.raw
            assert ei.value.retry_after is None

    async def test_non_standard_status_does_not_crash_phrase_lookup(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with pytest.raises(APIError) as ei:
                await _enter(engine, _resp(520))  # Cloudflare
            assert ei.value.status_code == 520

    async def test_error_carries_url_and_method(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with pytest.raises(APIError) as ei:
                await _enter(engine, _resp(500))
            assert ei.value.method == "GET"
            assert ei.value.url.endswith("/test")

    async def test_raw_is_bounded(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with pytest.raises(APIError) as ei:
                await _enter(engine, _resp(500, "x" * 20000))
            assert len(ei.value.raw) < 20000
            assert "truncated" in ei.value.raw


# ---------------------------------------------------------------------------
# 202 must pass through — the SDK's only recovery path depends on it
# ---------------------------------------------------------------------------


class TestAcceptedPassesThrough:
    @pytest.mark.parametrize("status", [200, 201, 202, 204])
    async def test_success_and_accepted_are_returned_not_raised(self, status):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            r = await _enter(engine, _resp(status))
            assert r.status == status

    async def test_fetch_result_still_raises_data_not_ready_on_202(self):
        from brightdata.scrapers.api_client import DatasetAPIClient

        resp = _resp(202, "still building")
        engine = MagicMock()
        engine.get_from_url = MagicMock(return_value=_ctx(resp))
        with pytest.raises(DataNotReadyError):
            await DatasetAPIClient(engine).fetch_result("snap_1")


def _ctx(response):
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=response)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


# ---------------------------------------------------------------------------
# retryable — the duplicate-job guard
# ---------------------------------------------------------------------------


class TestRetryable:
    def test_missing_status_is_never_retryable(self):
        """Raised locally, possibly after the server accepted the work."""
        assert is_retryable(APIError("Failed to trigger scrape - no snapshot_id returned")) is False

    def test_explicit_5xx_is_retryable(self):
        assert is_retryable(APIError("x", status_code=500)) is True

    def test_4xx_is_not_retryable(self):
        assert is_retryable(APIError("x", status_code=400)) is False

    def test_rate_limit_is_never_retryable_even_if_flagged(self):
        assert is_retryable(RateLimitError("x", status_code=429, retryable=True)) is False

    def test_network_and_timeout_are_retryable(self):
        from brightdata.exceptions import NetworkError

        assert is_retryable(NetworkError("down")) is True
        assert is_retryable(TimeoutError("slow")) is True


# ---------------------------------------------------------------------------
# Behaviour preserved at repaired call sites
# ---------------------------------------------------------------------------


class TestRepairedCallSites:
    async def test_crawler_scrape_returns_result_on_http_error(self):
        from brightdata.crawler.service import CrawlerService

        client = MagicMock()
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(side_effect=APIError("boom", status_code=500, raw="oops"))
        cm.__aexit__ = AsyncMock(return_value=False)
        client.engine.post_to_url = MagicMock(return_value=cm)

        result = await CrawlerService(client).crawl(urls="https://example.com")
        assert result.success is False
        assert "500" in result.error

    @pytest.mark.parametrize(
        "raised,expected",
        [
            (APIError("x", status_code=500), "error"),
            (RateLimitError("x", status_code=429), "error"),
        ],
    )
    async def test_unlocker_status_returns_string_never_raises(self, raised, expected):
        from brightdata.web_unlocker.async_client import AsyncUnblockerClient

        engine = MagicMock()
        engine.BASE_URL = "https://api.brightdata.com"
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(side_effect=raised)
        cm.__aexit__ = AsyncMock(return_value=False)
        engine.get_from_url = MagicMock(return_value=cm)

        got = await AsyncUnblockerClient(engine).get_status(zone="z", response_id="r")
        assert got == expected

    async def test_poll_reports_transport_failure_not_job_failure(self):
        from brightdata.utils.polling import poll_until_ready

        async def bad_status(_):
            raise AuthenticationError("Unauthorized (401)", status_code=401)

        async def never(_):
            raise AssertionError("should not fetch")

        r = await poll_until_ready(bad_status, never, "snap_1", poll_interval=0, poll_timeout=5)
        assert r.success is False
        assert "Failed to get status" in r.error
        assert "Job failed" not in r.error


# ---------------------------------------------------------------------------
# Exports and back-compat
# ---------------------------------------------------------------------------


class TestExportsAndBackCompat:
    def test_rate_limit_error_importable_at_both_levels(self):
        assert brightdata.RateLimitError is ex.RateLimitError

    def test_every_exception_name_is_exported_top_level(self):
        missing = [n for n in ex.__all__ if n not in brightdata.__all__]
        assert not missing, f"not re-exported from brightdata: {missing}"

    def test_legacy_constructors_still_work(self):
        assert BrightDataError("m").message == "m"
        assert APIError("m").status_code is None
        assert APIError("m", 429).status_code == 429  # positional, as before
        assert APIError("m", 429, "body").response_text == "body"

    def test_rate_limit_is_catchable_as_api_error(self):
        with pytest.raises(APIError):
            raise RateLimitError("x", status_code=429)

    def test_dataset_error_is_catchable_both_ways(self):
        from brightdata.datasets import DatasetError

        assert issubclass(DatasetError, BrightDataError)
        assert issubclass(DatasetError, Exception)


class TestHttpHelpers:
    @pytest.mark.parametrize(
        "value,expected", [("30", 30.0), ("0", 0.0), (None, None), ("soon", None)]
    )
    def test_parse_retry_after(self, value, expected):
        headers = {"Retry-After": value} if value is not None else {}
        assert parse_retry_after(headers) == expected

    def test_status_phrase_handles_non_standard(self):
        assert status_phrase(429) == "Too Many Requests"
        assert status_phrase(520)  # must not raise


# ---------------------------------------------------------------------------
# Structure must survive to the caller (the point of the whole change)
# ---------------------------------------------------------------------------


class TestCausePropagation:
    async def test_rate_limit_during_polling_reaches_the_caller(self):
        from brightdata.utils.polling import poll_until_ready

        async def rate_limited(_):
            raise RateLimitError("Rate limited (429)", status_code=429, retry_after=45.0)

        async def never(_):
            raise AssertionError("should not fetch")

        r = await poll_until_ready(rate_limited, never, "snap_1", poll_interval=0, poll_timeout=5)

        assert r.success is False
        assert isinstance(r.cause, RateLimitError)
        assert r.cause.status_code == 429
        assert r.cause.retry_after == 45.0
        assert r.cause.retryable is False

    async def test_trigger_failure_carries_cause(self):
        from brightdata.scrapers.workflow import WorkflowExecutor

        api = MagicMock()
        api.trigger = AsyncMock(side_effect=APIError("boom", status_code=503))
        r = await WorkflowExecutor(api).execute(payload=[{"url": "u"}], dataset_id="gd_x")

        assert r.success is False
        assert isinstance(r.cause, APIError)
        assert r.cause.status_code == 503
        assert r.cause.retryable is True

    async def test_crawler_result_carries_cause(self):
        from brightdata.crawler.service import CrawlerService

        client = MagicMock()
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(side_effect=RateLimitError("rl", status_code=429, retry_after=10))
        cm.__aexit__ = AsyncMock(return_value=False)
        client.engine.post_to_url = MagicMock(return_value=cm)

        r = await CrawlerService(client).crawl(urls="https://example.com")
        assert isinstance(r.cause, RateLimitError)
        assert r.cause.retry_after == 10

    def test_result_with_cause_is_still_serializable(self):
        from brightdata.models import ScrapeResult

        r = ScrapeResult(
            success=False,
            error="rate limited",
            cause=RateLimitError("rl", status_code=429, retry_after=30.0),
        )
        payload = r.to_dict()
        assert payload["cause"]["type"] == "RateLimitError"
        assert payload["cause"]["status_code"] == 429
        r.to_json()  # must not raise


class TestDatasetErrorContract:
    """The datasets layer must keep raising DatasetError after central translation."""

    async def _call(self, status, body, headers=None):
        from brightdata.datasets.base import BaseDataset

        class DS(BaseDataset):
            DATASET_ID = "gd_x"
            NAME = "x"

        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            engine._session.request = AsyncMock(return_value=_resp(status, body, headers))
            return await DS(engine)(filter={"name": "f", "operator": "is_not_null"})

    async def test_client_error_is_still_a_dataset_error(self):
        from brightdata.datasets import DatasetError

        with pytest.raises(DatasetError) as ei:
            await self._call(400, '{"error":"bad filter"}')
        assert ei.value.status_code == 400
        assert "bad filter" in ei.value.raw

    async def test_rate_limit_stays_rate_limit_error(self):
        with pytest.raises(RateLimitError) as ei:
            await self._call(429, "too_many_parallel_jobs", {"Retry-After": "60"})
        assert ei.value.retry_after == 60.0

    async def test_message_keeps_a_body_excerpt(self):
        with pytest.raises(APIError) as ei:
            engine = AsyncEngine(bearer_token="tok")
            async with engine:
                await _enter(engine, _resp(400, "helpful detail"))
        assert "helpful detail" in str(ei.value)
        assert len(str(ei.value)) < 300  # bounded
