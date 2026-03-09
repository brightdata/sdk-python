"""Shared test fixtures for Bright Data SDK tests."""

import sys
import os
from unittest.mock import AsyncMock, MagicMock
from typing import Any, Dict, Optional

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ---------------------------------------------------------------------------
# Mock HTTP Response
# ---------------------------------------------------------------------------


class MockResponse:
    """Mock aiohttp response with configurable status, JSON, and text."""

    def __init__(
        self,
        status: int = 200,
        json_data: Any = None,
        text_data: str = "",
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status = status
        self._json_data = json_data
        self._text_data = text_data
        self.headers = headers or {}
        self.closed = False

    async def json(self):
        return self._json_data

    async def text(self):
        return self._text_data

    async def release(self):
        pass

    def close(self):
        self.closed = True


class MockContextManager:
    """Mock async context manager wrapping a MockResponse."""

    def __init__(self, response: MockResponse):
        self._response = response

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, *args):
        pass


# ---------------------------------------------------------------------------
# Engine fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_engine():
    """
    Reusable mock AsyncEngine.

    The engine's HTTP methods (get, post, get_from_url, post_to_url, etc.)
    return MockContextManager by default. Override per-test by setting
    the return_value on the method.

    Usage:
        async with mock_engine.get("/endpoint") as response:
            data = await response.json()
    """
    engine = MagicMock()
    engine.bearer_token = "test_token_123456789"

    default_response = MockResponse(200, json_data={})
    default_cm = MockContextManager(default_response)

    engine.get = MagicMock(return_value=default_cm)
    engine.post = MagicMock(return_value=default_cm)
    engine.delete = MagicMock(return_value=default_cm)
    engine.get_from_url = MagicMock(return_value=default_cm)
    engine.post_to_url = MagicMock(return_value=default_cm)
    engine.request = MagicMock(return_value=default_cm)

    return engine


def make_engine_response(engine, method: str, response: MockResponse):
    """
    Configure a mock engine method to return a specific response.

    Args:
        engine: Mock engine from mock_engine fixture
        method: Method name ("get", "post", "get_from_url", "post_to_url")
        response: MockResponse to return

    Usage:
        make_engine_response(mock_engine, "post_to_url", MockResponse(200, {"snapshot_id": "abc"}))
    """
    cm = MockContextManager(response)
    getattr(engine, method).return_value = cm


# ---------------------------------------------------------------------------
# API Client fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_api_client():
    """Mock DatasetAPIClient with configurable trigger/status/fetch."""
    client = AsyncMock()
    client.trigger = AsyncMock(return_value="snap_123")
    client.get_status = AsyncMock(return_value="ready")
    client.fetch_result = AsyncMock(return_value=[{"title": "Test"}])
    return client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_status_sequence(statuses):
    """
    Create an async side_effect that returns statuses in order.

    Usage:
        mock_api_client.get_status.side_effect = make_status_sequence(
            ["in_progress", "in_progress", "ready"]
        )
    """

    async def side_effect(*args, **kwargs):
        return statuses.pop(0)

    return side_effect
