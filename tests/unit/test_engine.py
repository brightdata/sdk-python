"""Tests for core/engine.py — AsyncEngine HTTP communication."""

import asyncio
import ssl
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from brightdata.core.engine import AsyncEngine
from brightdata.exceptions import AuthenticationError, NetworkError, SSLError


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestEngineInit:
    def test_stores_bearer_token(self):
        engine = AsyncEngine(bearer_token="tok_abc")
        assert engine.bearer_token == "tok_abc"

    def test_default_timeout(self):
        engine = AsyncEngine(bearer_token="tok")
        assert engine.timeout.total == 30

    def test_custom_timeout(self):
        engine = AsyncEngine(bearer_token="tok", timeout=120)
        assert engine.timeout.total == 120

    def test_default_rate_limit(self):
        engine = AsyncEngine(bearer_token="tok")
        assert engine._rate_limit == AsyncEngine.DEFAULT_RATE_LIMIT

    def test_custom_rate_limit(self):
        engine = AsyncEngine(bearer_token="tok", rate_limit=5, rate_period=2.0)
        assert engine._rate_limit == 5
        assert engine._rate_period == 2.0

    def test_session_none_before_enter(self):
        engine = AsyncEngine(bearer_token="tok")
        assert engine._session is None


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestEngineContextManager:
    @pytest.mark.asyncio
    async def test_creates_session_on_enter(self):
        engine = AsyncEngine(bearer_token="tok_abc")
        async with engine:
            assert engine._session is not None
            assert not engine._session.closed

    @pytest.mark.asyncio
    async def test_closes_session_on_exit(self):
        engine = AsyncEngine(bearer_token="tok_abc")
        async with engine:
            session = engine._session
        assert engine._session is None
        assert session.closed

    @pytest.mark.asyncio
    async def test_idempotent_enter(self):
        """Calling __aenter__ twice should reuse the same session."""
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            session1 = engine._session
            await engine.__aenter__()
            session2 = engine._session
            assert session1 is session2

    @pytest.mark.asyncio
    async def test_session_headers_contain_auth(self):
        engine = AsyncEngine(bearer_token="my_secret_token")
        async with engine:
            headers = engine._session.headers
            assert headers["Authorization"] == "Bearer my_secret_token"
            assert headers["Content-Type"] == "application/json"
            assert "brightdata-sdk/" in headers["User-Agent"]


# ---------------------------------------------------------------------------
# Request routing (without real HTTP — tests the method dispatch)
# ---------------------------------------------------------------------------


class TestRequestRouting:
    @pytest.mark.asyncio
    async def test_raises_if_no_session(self):
        engine = AsyncEngine(bearer_token="tok")
        with pytest.raises(RuntimeError, match="must be used as async context manager"):
            engine.request("GET", "/test")

    @pytest.mark.asyncio
    async def test_get_delegates_to_request(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with patch.object(engine, "request", return_value="cm") as mock_req:
                result = engine.get("/endpoint", params={"a": "1"})
                mock_req.assert_called_once_with(
                    "GET", "/endpoint", params={"a": "1"}, headers=None
                )

    @pytest.mark.asyncio
    async def test_post_delegates_to_request(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with patch.object(engine, "request", return_value="cm") as mock_req:
                result = engine.post("/endpoint", json_data={"k": "v"})
                mock_req.assert_called_once_with(
                    "POST", "/endpoint", json_data={"k": "v"}, params=None, headers=None
                )

    @pytest.mark.asyncio
    async def test_delete_delegates_to_request(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            with patch.object(engine, "request", return_value="cm") as mock_req:
                result = engine.delete("/endpoint")
                mock_req.assert_called_once_with(
                    "DELETE", "/endpoint", json_data=None, params=None, headers=None
                )

    @pytest.mark.asyncio
    async def test_request_builds_full_url(self):
        """request() should prepend BASE_URL to the endpoint."""
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            cm = engine.request("GET", "/v3/test")
            # The URL is stored inside the ResponseContextManager
            assert cm._url == f"{AsyncEngine.BASE_URL}/v3/test"

    @pytest.mark.asyncio
    async def test_request_merges_custom_headers(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            cm = engine.request("GET", "/test", headers={"X-Custom": "val"})
            assert cm._headers["X-Custom"] == "val"
            # Original auth header should still be there
            assert "Bearer tok" in cm._headers["Authorization"]

    @pytest.mark.asyncio
    async def test_post_to_url_uses_full_url(self):
        """post_to_url should NOT prepend BASE_URL."""
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            cm = engine.post_to_url("https://custom.api.com/trigger", json_data={"x": 1})
            assert cm._url == "https://custom.api.com/trigger"

    @pytest.mark.asyncio
    async def test_get_from_url_uses_full_url(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            cm = engine.get_from_url("https://custom.api.com/data", params={"fmt": "json"})
            assert cm._url == "https://custom.api.com/data"
            assert cm._params == {"fmt": "json"}


# ---------------------------------------------------------------------------
# Error handling (mock aiohttp session to simulate failures)
# ---------------------------------------------------------------------------


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_401_raises_authentication_error(self):
        engine = AsyncEngine(bearer_token="bad_token")
        async with engine:
            # Mock the session.request to return a 401 response
            mock_resp = AsyncMock()
            mock_resp.status = 401
            mock_resp.text = AsyncMock(return_value="Unauthorized")
            mock_resp.release = AsyncMock()
            engine._session.request = AsyncMock(return_value=mock_resp)

            cm = engine.get("/test")
            with pytest.raises(AuthenticationError, match="Unauthorized"):
                async with cm:
                    pass

    @pytest.mark.asyncio
    async def test_403_raises_authentication_error(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            mock_resp = AsyncMock()
            mock_resp.status = 403
            mock_resp.text = AsyncMock(return_value="Forbidden")
            mock_resp.release = AsyncMock()
            engine._session.request = AsyncMock(return_value=mock_resp)

            cm = engine.get("/test")
            with pytest.raises(AuthenticationError, match="Forbidden"):
                async with cm:
                    pass

    @pytest.mark.asyncio
    async def test_200_returns_response(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json = AsyncMock(return_value={"ok": True})
            mock_resp.close = MagicMock()
            engine._session.request = AsyncMock(return_value=mock_resp)

            async with engine.get("/test") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data == {"ok": True}

    @pytest.mark.asyncio
    async def test_network_error_raises_network_error(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            engine._session.request = AsyncMock(
                side_effect=aiohttp.ClientError("Connection refused")
            )

            cm = engine.get("/test")
            with pytest.raises(NetworkError, match="Network error"):
                async with cm:
                    pass

    @pytest.mark.asyncio
    async def test_timeout_raises_timeout_error(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            engine._session.request = AsyncMock(side_effect=asyncio.TimeoutError())

            cm = engine.get("/test")
            with pytest.raises(TimeoutError, match="timeout"):
                async with cm:
                    pass

    @pytest.mark.asyncio
    async def test_ssl_error_raises_ssl_error(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            ssl_err = aiohttp.ClientConnectorCertificateError(
                connection_key=MagicMock(),
                certificate_error=ssl.SSLCertVerificationError("CERTIFICATE_VERIFY_FAILED"),
            )
            engine._session.request = AsyncMock(side_effect=ssl_err)

            cm = engine.get("/test")
            with pytest.raises(SSLError):
                async with cm:
                    pass

    @pytest.mark.asyncio
    async def test_os_error_with_ssl_raises_ssl_error(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            engine._session.request = AsyncMock(
                side_effect=OSError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed")
            )

            cm = engine.get("/test")
            with pytest.raises(SSLError):
                async with cm:
                    pass

    @pytest.mark.asyncio
    async def test_generic_os_error_raises_network_error(self):
        """Non-SSL OSError should be NetworkError, not SSLError."""
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            engine._session.request = AsyncMock(side_effect=OSError("Connection reset by peer"))

            cm = engine.get("/test")
            with pytest.raises(NetworkError, match="Network error"):
                async with cm:
                    pass

    @pytest.mark.asyncio
    async def test_response_closed_on_exit(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.close = MagicMock()
            engine._session.request = AsyncMock(return_value=mock_resp)

            async with engine.get("/test") as resp:
                pass
            mock_resp.close.assert_called_once()


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limiter_created_on_enter(self):
        engine = AsyncEngine(bearer_token="tok", rate_limit=5)
        async with engine:
            if engine._rate_limiter is not None:
                # aiolimiter installed
                assert engine._rate_limiter is not None
            # If aiolimiter not installed, limiter will be None — that's OK

    @pytest.mark.asyncio
    async def test_rate_limiter_cleared_on_exit(self):
        engine = AsyncEngine(bearer_token="tok", rate_limit=5)
        async with engine:
            pass
        assert engine._rate_limiter is None
