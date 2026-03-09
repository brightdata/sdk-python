"""Tests for utils/retry.py — Exponential backoff logic."""

from unittest.mock import AsyncMock, patch

import pytest

from brightdata.utils.retry import retry_with_backoff
from brightdata.exceptions import APIError, NetworkError, AuthenticationError, ValidationError


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestRetrySuccess:
    @pytest.mark.asyncio
    async def test_returns_on_first_success(self):
        func = AsyncMock(return_value="ok")
        result = await retry_with_backoff(func, max_retries=3)
        assert result == "ok"
        assert func.call_count == 1

    @pytest.mark.asyncio
    async def test_retries_then_succeeds(self):
        func = AsyncMock(side_effect=[NetworkError("fail"), NetworkError("fail"), "ok"])

        with patch("brightdata.utils.retry.asyncio.sleep", new_callable=AsyncMock):
            result = await retry_with_backoff(func, max_retries=3, initial_delay=0.01)

        assert result == "ok"
        assert func.call_count == 3


# ---------------------------------------------------------------------------
# Retryable vs non-retryable exceptions
# ---------------------------------------------------------------------------


class TestRetryableExceptions:
    @pytest.mark.asyncio
    async def test_retries_on_network_error(self):
        func = AsyncMock(side_effect=[NetworkError("net"), "ok"])

        with patch("brightdata.utils.retry.asyncio.sleep", new_callable=AsyncMock):
            result = await retry_with_backoff(func, max_retries=3, initial_delay=0.01)

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_retries_on_timeout_error(self):
        func = AsyncMock(side_effect=[TimeoutError("timeout"), "ok"])

        with patch("brightdata.utils.retry.asyncio.sleep", new_callable=AsyncMock):
            result = await retry_with_backoff(func, max_retries=3, initial_delay=0.01)

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_retries_on_api_error(self):
        func = AsyncMock(side_effect=[APIError("500", status_code=500), "ok"])

        with patch("brightdata.utils.retry.asyncio.sleep", new_callable=AsyncMock):
            result = await retry_with_backoff(func, max_retries=3, initial_delay=0.01)

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_does_not_retry_authentication_error(self):
        func = AsyncMock(side_effect=AuthenticationError("bad token"))

        with pytest.raises(AuthenticationError, match="bad token"):
            await retry_with_backoff(func, max_retries=3)

        assert func.call_count == 1

    @pytest.mark.asyncio
    async def test_does_not_retry_validation_error(self):
        func = AsyncMock(side_effect=ValidationError("bad input"))

        with pytest.raises(ValidationError, match="bad input"):
            await retry_with_backoff(func, max_retries=3)

        assert func.call_count == 1

    @pytest.mark.asyncio
    async def test_does_not_retry_value_error(self):
        func = AsyncMock(side_effect=ValueError("wrong"))

        with pytest.raises(ValueError):
            await retry_with_backoff(func, max_retries=3)

        assert func.call_count == 1

    @pytest.mark.asyncio
    async def test_custom_retryable_exceptions(self):
        func = AsyncMock(side_effect=[ValueError("retry me"), "ok"])

        with patch("brightdata.utils.retry.asyncio.sleep", new_callable=AsyncMock):
            result = await retry_with_backoff(
                func,
                max_retries=3,
                retryable_exceptions=[ValueError],
                initial_delay=0.01,
            )

        assert result == "ok"


# ---------------------------------------------------------------------------
# Exhausted retries
# ---------------------------------------------------------------------------


class TestRetryExhausted:
    @pytest.mark.asyncio
    async def test_raises_last_exception_after_max_retries(self):
        func = AsyncMock(side_effect=NetworkError("persistent failure"))

        with patch("brightdata.utils.retry.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(NetworkError, match="persistent failure"):
                await retry_with_backoff(func, max_retries=2, initial_delay=0.01)

        assert func.call_count == 3  # initial + 2 retries

    @pytest.mark.asyncio
    async def test_zero_retries_calls_once(self):
        func = AsyncMock(side_effect=NetworkError("fail"))

        with pytest.raises(NetworkError):
            await retry_with_backoff(func, max_retries=0)

        assert func.call_count == 1


# ---------------------------------------------------------------------------
# Backoff timing
# ---------------------------------------------------------------------------


class TestBackoffTiming:
    @pytest.mark.asyncio
    async def test_exponential_backoff_delays(self):
        func = AsyncMock(
            side_effect=[NetworkError("1"), NetworkError("2"), NetworkError("3"), "ok"]
        )
        sleep_calls = []

        async def mock_sleep(duration):
            sleep_calls.append(duration)

        with patch("brightdata.utils.retry.asyncio.sleep", side_effect=mock_sleep):
            result = await retry_with_backoff(
                func, max_retries=3, initial_delay=1.0, backoff_factor=2.0
            )

        assert result == "ok"
        assert sleep_calls == [1.0, 2.0, 4.0]

    @pytest.mark.asyncio
    async def test_max_delay_cap(self):
        func = AsyncMock(
            side_effect=[NetworkError("1"), NetworkError("2"), NetworkError("3"), "ok"]
        )
        sleep_calls = []

        async def mock_sleep(duration):
            sleep_calls.append(duration)

        with patch("brightdata.utils.retry.asyncio.sleep", side_effect=mock_sleep):
            result = await retry_with_backoff(
                func,
                max_retries=3,
                initial_delay=10.0,
                backoff_factor=10.0,
                max_delay=50.0,
            )

        # Delays: min(10, 50)=10, min(100, 50)=50, min(1000, 50)=50
        assert sleep_calls == [10.0, 50.0, 50.0]
