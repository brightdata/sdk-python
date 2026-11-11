"""Business Search request, response, and transport contract tests.

Cover page envelopes, projections, paging, diagnostics, and failure identity
using mocks or a loopback HTTP peer, without live API requests.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from types import SimpleNamespace
from typing import Any, Dict, Literal, get_type_hints
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from multidict import CIMultiDict

from brightdata import BrightDataClient, BrightSearchPage, BrightSearchService, SyncBrightDataClient
from brightdata.core.engine import AsyncEngine
from brightdata.exceptions import (
    APIError,
    AuthenticationError,
    BrightDataError,
    NetworkError,
    RateLimitError,
)
from brightdata.exceptions import ValidationError
from brightdata.sync_client import SyncSearchService
from brightdata.utils.retry import is_retryable, retry_with_backoff
from tests.conftest import MockContextManager, MockResponse

PUBLIC_SEARCHES = [
    ("business", "companies", "company"),
    ("business", "people", "people"),
    ("ecommerce", "products", "ecommerce"),
]


@pytest.fixture
def body():
    return {
        "req_id": "request_123",
        "source": "linkedin_company",
        "meta": {"matched": 42, "coverage_percent": 100, "offset": 0, "limit": 10},
        "documents": [
            {"bright_id": "northstar", "data": {"name": "Northstar Systems"}},
            {"bright_id": "second", "data": {}},
        ],
    }


def response(body, status=200, headers=None):
    return MockResponse(status, json_data=body, text_data=json.dumps(body), headers=headers)


@pytest.fixture
def service(mock_engine, body):
    mock_engine.BASE_URL = AsyncEngine.BASE_URL
    mock_engine.post.return_value = MockContextManager(response(body))
    return BrightSearchService(mock_engine)


@pytest.mark.parametrize(
    "category,mode",
    [
        ("company", "ludicrous"),
        ("company", "instant"),
        ("company", "smart"),
        ("people", "ludicrous"),
        ("people", "instant"),
        ("people", "smart"),
        ("ecommerce", "ludicrous"),
    ],
)
async def test_supported_requests_are_one_native_post(service, mock_engine, body, category, mode):
    query = {"equals": {"country_code": "US"}} if mode == "ludicrous" else "US companies"
    page = await service.search(category, query, mode=mode)

    mock_engine.post.assert_called_once_with(
        f"/search/{category}",
        json_data={"mode": mode, "query": query, "offset": 0, "limit": 10},
        preserve_error_response=True,
        allow_redirects=False,
    )
    mock_engine.get.assert_not_called()
    assert page.to_dict() == body
    assert page.req_id == "request_123"


async def test_structured_queries_custom_fields_and_debug_values_are_not_rewritten(
    service, mock_engine
):
    query = {
        "and": [
            {"text": {"role": {"value": "engineer", "mode": "all-or-top-bm25", "top-k": 100}}},
            {"or": [{"equals": {"city": "Berlin"}}, {"in": {"country_code": ["DE", "GB"]}}]},
            {"not": {"equals": {"future_field": False}}},
            {"range": {"experience_years": {">=": 0, "<": 10}}},
        ]
    }
    debug = {
        "explain": {"trace": 1},
        "trace": False,
        "benchmark": 0,
        "__overrides__": {
            "hornet": {"score": {"parameters": {"name_weight": None, "about_weight": 0}}},
            "reranker": {"enabled": False},
        },
    }
    before = deepcopy((query, debug))
    view = {"fields": ["name", "future_released_field"]}
    await service.search(
        "people",
        query,
        mode="ludicrous",
        source="future_people",
        view=view,
        offset=20,
        limit=20,
        debug=debug,
    )
    sent = mock_engine.post.call_args.kwargs["json_data"]
    assert sent == {
        "query": query,
        "mode": "ludicrous",
        "source": "future_people",
        "view": view,
        "offset": 20,
        "limit": 20,
        **debug,
    }
    assert (query, debug) == before


async def test_explicit_false_and_null_debug_are_retained(service, mock_engine):
    await service.search(
        "company", "query", mode="instant", debug={"explain": False, "__overrides__": None}
    )
    sent = mock_engine.post.call_args.kwargs["json_data"]
    assert sent["explain"] is False
    assert "__overrides__" in sent and sent["__overrides__"] is None
    assert "trace" not in sent and "benchmark" not in sent


@pytest.mark.parametrize(
    "changes",
    [
        {"category": "flights"},
        {"category": "ecom"},  # The API accepts ecommerce, not the old spelling.
        {"category": ["company"]},
        {"mode": "fast"},
        {"mode": None},
        {"category": "ecommerce", "mode": "instant"},
        {"category": "ecommerce", "mode": "smart"},
        {"mode": "ludicrous", "query": "text"},
        {"mode": "ludicrous", "query": []},
        {"query": {}},
        {"query": None},
        {"query": "x" * 201},
        {"offset": -1},
        {"offset": True},
        {"offset": 1.5},
        {"offset": "1"},
        {"offset": 1001},
        {"mode": "smart", "offset": 101},
        {"limit": -1},
        {"limit": False},
        {"limit": 1.5},
        {"limit": None},
        {"limit": 101},
        {"mode": "smart", "limit": 11},
        {"source": ["linkedin_company"]},
        {"view": ["name"]},
        {"view": {"fields": "name"}},
        {"view": {"fields": [1]}},
        {"view": {"other": []}},
        {"view": {"fields": [], "other": 1}},
        {"category": "ecommerce", "mode": "ludicrous", "query": {}, "view": "summary"},
        {
            "category": "ecommerce",
            "mode": "ludicrous",
            "query": {},
            "source": "retail_products_live",
            "view": "summary",
        },
        {"debug": False},
        {"debug": {"query": {}}},
        {"debug": {"mode": "smart"}},
        {"debug": {"limit": 100}},
        {"debug": {"source": "other"}},
    ],
)
async def test_invalid_outer_requests_fail_before_network(service, mock_engine, changes):
    arguments = {"category": "company", "query": "query", "mode": "instant", **changes}
    with pytest.raises(ValidationError):
        await service.search(**arguments)
    mock_engine.post.assert_not_called()


@pytest.mark.parametrize("target", ["query", "debug"])
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param(float("-inf"), id="negative-infinity"),
        pytest.param({1: "value"}, id="integer-key"),
        pytest.param({False: "value"}, id="boolean-key"),
        pytest.param({None: "value"}, id="null-key"),
        pytest.param({1.5: "value"}, id="float-key"),
        pytest.param({("key",): "value"}, id="tuple-key"),
        pytest.param(b"bytes", id="bytes"),
        pytest.param({1, 2}, id="set"),
        pytest.param(object(), id="object"),
    ],
)
async def test_nested_non_json_values_fail_before_dispatch(service, mock_engine, target, value):
    query = {"future_field": [value]} if target == "query" else {}
    debug = {"__overrides__": {"future_option": [value]}} if target == "debug" else None
    with pytest.raises(ValidationError):
        await service.search("company", query, mode="ludicrous", debug=debug)
    mock_engine.post.assert_not_called()


@pytest.mark.parametrize("target", ["query", "debug"])
@pytest.mark.parametrize("container", ["list", "dict"])
async def test_circular_payload_fails_before_dispatch(service, mock_engine, target, container):
    if container == "list":
        value = []
        value.append(value)
    else:
        value = {}
        value["self"] = value
    query = {"future_field": value} if target == "query" else {}
    debug = {"__overrides__": value} if target == "debug" else None
    with pytest.raises(ValidationError):
        await service.search("company", query, mode="ludicrous", debug=debug)
    mock_engine.post.assert_not_called()
    assert (value[0] if container == "list" else value["self"]) is value


async def test_deep_payload_fails_before_dispatch(service, mock_engine):
    query = {}
    for _ in range(1500):
        query = {"nested": query}
    with pytest.raises(ValidationError):
        await service.search("company", query, mode="ludicrous")
    mock_engine.post.assert_not_called()


async def test_json_validation_preserves_nested_values_and_shared_containers(service, mock_engine):
    shared = {"future_field": [None, False, 0, [], {}, "text", 1.5]}
    query = {"future_query": [shared, shared]}
    debug = {"__overrides__": {"future_debug": shared}, "trace": False, "benchmark": 0}
    before = deepcopy((query, debug))

    await service.search("company", query, mode="ludicrous", debug=debug)

    sent = mock_engine.post.call_args.kwargs["json_data"]
    assert (query, debug) == before
    assert sent["query"] == before[0]
    assert sent["query"]["future_query"][0] is shared
    assert sent["__overrides__"] == before[1]["__overrides__"]
    assert sent["trace"] is False and sent["benchmark"] == 0
    assert json.loads(json.dumps(sent, allow_nan=False)) == sent


@pytest.mark.parametrize("category", ["company", "people"])
@pytest.mark.parametrize("mode", ["instant", "smart"])
@pytest.mark.parametrize("offset,limit", [(91, 10), (100, 1)])
async def test_natural_language_window_fails_before_network(
    service, mock_engine, category, mode, offset, limit
):
    with pytest.raises(ValidationError, match=r"offset.*limit.*100"):
        await service.search(category, "US companies", mode=mode, offset=offset, limit=limit)
    mock_engine.post.assert_not_called()


@pytest.mark.parametrize(
    "mode,limit,offset",
    [
        ("ludicrous", 100, 1000),
        ("instant", 100, 0),
        ("instant", 1, 99),
        ("smart", 10, 90),
        ("smart", 1, 99),
    ],
)
async def test_documented_boundaries_are_inclusive(service, mock_engine, mode, limit, offset):
    query = {"equals": {"headquarters_country_code": "US"}} if mode == "ludicrous" else "x" * 200
    await service.search("company", query, mode=mode, limit=limit, offset=offset)
    sent = mock_engine.post.call_args.kwargs["json_data"]
    assert sent["limit"] == limit and sent["offset"] == offset
    assert sent["query"] == query


@pytest.mark.parametrize("mode,query", [("instant", ""), ("ludicrous", {})])
async def test_unspecified_zero_and_empty_semantics_are_left_to_server(
    service, mock_engine, mode, query
):
    await service.search("company", query, mode=mode, limit=0)
    assert mock_engine.post.call_args.kwargs["json_data"]["limit"] == 0
    assert mock_engine.post.call_args.kwargs["json_data"]["query"] == query


async def test_future_source_view_rules_are_server_owned(service, mock_engine):
    await service.search("ecommerce", {}, mode="ludicrous", source="future_retail", view="summary")
    assert mock_engine.post.call_args.kwargs["json_data"]["view"] == "summary"


def test_page_preserves_sparse_fields_order_diagnostics_and_unknown_fields(body):
    body["meta"].update(matched=100, coverage_percent=72.5, future_meta="value")
    body["documents"][0].update(score=0.8, future_document="value")
    body["documents"][0]["data"]["future_field"] = None
    body["documents"][1]["data"] = {"name": "Second"}
    body["__explain__"] = {"future_diagnostic": {"value": None}}
    body["response_headers"] = {"future_wire_field": True}
    page = BrightSearchPage(body, {"x-debug-trace-page": "https://trace.example/page"})

    assert page.to_dict() == body
    assert json.loads(page.to_json()) == body
    assert page.source == body["source"]
    assert page.meta["matched"] == 100 and page.meta["coverage_percent"] == 72.5
    assert [doc["bright_id"] for doc in page.documents] == ["northstar", "second"]
    assert "score" not in page.documents[1]
    assert "future_field" not in page.documents[1]["data"]
    assert page.explain == body["__explain__"]
    assert page.response_headers != page.raw["response_headers"]

    copied = page.to_dict()
    copied["documents"][0]["data"]["name"] = "Changed"
    assert page.documents[0]["data"]["name"] == "Northstar Systems"
    page.raw["meta"]["matched"] = 43
    assert page.meta["matched"] == 43  # no duplicate cached metadata


@pytest.mark.parametrize("documents", [[], [{"bright_id": "id_only", "data": {}}]])
def test_empty_pages_and_id_only_documents_are_valid(body, documents):
    body["documents"] = documents
    page = BrightSearchPage(body)
    assert page.documents == documents
    assert page.explain is None
    assert "__explain__" not in page.to_dict()


@pytest.mark.parametrize(
    "field,value",
    [
        ("req_id", None),
        ("source", 1),
        ("meta", None),
        ("documents", {}),
        ("documents", [None]),
        ("documents", [{"bright_id": 1, "data": {}}]),
        ("documents", [{"bright_id": "id", "data": None}]),
    ],
)
async def test_malformed_envelope_raises_api_error(service, mock_engine, body, field, value):
    body[field] = value
    mock_engine.post.return_value = MockContextManager(response(body))
    with pytest.raises(APIError, match="Invalid Bright Search response") as error:
        await service.search("company", "query", mode="instant")
    assert error.value.response_json == body
    assert error.value.status_code == 200 and error.value.retryable is False
    mock_engine.post.assert_called_once()


@pytest.mark.parametrize(
    "field,value",
    [
        ("matched", True),
        ("matched", "42"),
        ("matched", float("nan")),
        ("coverage_percent", None),
        ("coverage_percent", float("inf")),
        ("offset", False),
        ("limit", 10.5),
    ],
)
def test_malformed_meta_does_not_become_successful_empty_data(body, field, value):
    body["meta"][field] = value
    with pytest.raises(ValueError, match=f"meta.{field}"):
        BrightSearchPage(body)


@pytest.mark.parametrize("data", [[], None, "text", {}])
async def test_invalid_or_missing_response_envelope(service, mock_engine, data):
    mock_engine.post.return_value = MockContextManager(response(data))
    with pytest.raises(APIError, match="Invalid Bright Search response"):
        await service.search("company", "query", mode="instant")
    mock_engine.post.assert_called_once()


async def test_non_json_success_remains_an_api_failure(service, mock_engine):
    mock_engine.post.return_value = MockContextManager(
        MockResponse(200, text_data="<html>error</html>")
    )
    with pytest.raises(APIError, match="invalid JSON") as error:
        await service.search("company", "query", mode="instant")
    assert error.value.raw == "<html>error</html>"
    mock_engine.post.assert_called_once()


async def test_unexpected_accepted_response_does_not_start_polling(service, mock_engine, body):
    mock_engine.post.return_value = MockContextManager(response(body, status=202))
    with pytest.raises(APIError, match="Unexpected Bright Search status") as error:
        await service.search("company", "query", mode="instant")
    assert error.value.req_id == "request_123"
    mock_engine.post.assert_called_once()
    mock_engine.get.assert_not_called()


@pytest.mark.parametrize(
    "status,error_type",
    [
        (400, APIError),
        (401, AuthenticationError),
        (403, AuthenticationError),
        (429, RateLimitError),
        (500, APIError),
        (502, APIError),
    ],
)
async def test_engine_preserves_error_identity_before_truncation_without_retry(status, error_type):
    data = {"__explain__": {"detail": "x" * 6000}, "req_id": "tail_request_id", "error": "failed"}
    headers = CIMultiDict(
        {
            "Retry-After": "2",
            "X-Debug-Trace": "https://trace.example/raw",
            "X-Debug-Trace-Page": "https://trace.example/page",
            "Set-Cookie": "omit-me",
        }
    )
    engine = AsyncEngine("test_token")
    async with engine:
        engine._session.request = AsyncMock(return_value=response(data, status, headers))
        with pytest.raises(error_type) as error:
            await BrightSearchService(engine).search("company", "query", mode="instant")
        engine._session.request.assert_awaited_once()
        assert "preserve_error_response" not in engine._session.request.call_args.kwargs

    exc = error.value
    assert exc.req_id == "tail_request_id" and exc.response_json == data
    assert "tail_request_id" not in exc.raw and "truncated" in exc.raw
    assert exc.response_headers == {
        "retry-after": "2",
        "x-debug-trace": "https://trace.example/raw",
        "x-debug-trace-page": "https://trace.example/page",
    }
    assert exc.status_code == status and exc.method == "POST"
    assert exc.url == "https://api.brightdata.com/search/company"
    assert exc.retryable is False
    if status == 429:
        assert exc.retry_after == 2


async def test_error_capture_is_opt_in_and_non_json_errors_keep_their_type():
    engine = AsyncEngine("test_token")
    async with engine:
        engine._session.request = AsyncMock(return_value=response({"req_id": "legacy"}, 400))
        with pytest.raises(APIError) as legacy:
            async with engine.post("/legacy"):
                pass
        assert legacy.value.req_id is None
        assert legacy.value.response_json is None
        assert legacy.value.response_headers == {}

        engine._session.request = AsyncMock(
            return_value=MockResponse(429, text_data="rate limited")
        )
        with pytest.raises(RateLimitError) as non_json:
            await BrightSearchService(engine).search("people", "query", mode="instant")
        assert non_json.value.raw == "rate limited"
        assert non_json.value.response_json is None
        assert non_json.value.req_id is None
        engine._session.request.assert_awaited_once()


@pytest.mark.parametrize(
    "failure,expected",
    [(asyncio.TimeoutError(), TimeoutError), (aiohttp.ClientError("offline"), NetworkError)],
)
async def test_transport_failures_are_not_replayed(failure, expected):
    engine = AsyncEngine("test_token")
    async with engine:
        engine._session.request = AsyncMock(side_effect=failure)
        with pytest.raises(expected) as error:
            await retry_with_backoff(
                lambda: BrightSearchService(engine).search("company", "query", mode="instant"),
                max_retries=1,
                initial_delay=0,
            )
        engine._session.request.assert_awaited_once()
        assert not is_retryable(error.value)


@pytest.mark.parametrize("status", [200, 429])
async def test_body_timeout_keeps_known_context(status):
    failure = asyncio.TimeoutError("body timed out")
    resp = response({}, status, CIMultiDict({"Retry-After": "2", "X-Debug-Trace": "trace"}))
    resp.text = AsyncMock(side_effect=failure)
    async with AsyncEngine("test_token") as engine:
        engine._session.request = AsyncMock(return_value=resp)
        with pytest.raises(TimeoutError) as error:
            await retry_with_backoff(
                lambda: BrightSearchService(engine).search("company", "query", mode="instant"),
                max_retries=1,
                initial_delay=0,
            )
        engine._session.request.assert_awaited_once()
        assert resp.closed
    exc = error.value
    assert isinstance(exc, BrightDataError)
    assert exc.status_code == status
    assert exc.response_headers == {"retry-after": "2", "x-debug-trace": "trace"}
    assert exc.retry_after == 2
    assert exc.url == "https://api.brightdata.com/search/company" and exc.method == "POST"
    assert exc.req_id is None and exc.response_json is None
    assert exc.__cause__ is failure
    assert not is_retryable(exc)


async def test_legacy_request_timeout_remains_plain_and_retryable():
    failure = asyncio.TimeoutError("connection timed out")
    async with AsyncEngine("test_token") as engine:
        engine._session.request = AsyncMock(side_effect=failure)

        async def request():
            async with engine.post("/legacy"):
                pytest.fail("The mocked request should time out")

        with pytest.raises(TimeoutError) as error:
            await retry_with_backoff(request, max_retries=1, initial_delay=0)
        assert engine._session.request.await_count == 2
        assert type(error.value) is TimeoutError
        assert error.value.__cause__ is failure
        assert is_retryable(error.value)


@pytest.mark.parametrize("client_type", [BrightDataClient, SyncBrightDataClient])
def test_search_categories_are_lazy_cached_and_separate(client_type):
    client = client_type(token="test_token_12345", auto_create_zones=False)
    search = client.search
    assert search.business is search.business
    assert search.ecommerce is search.ecommerce
    assert search.business is not search.ecommerce
    assert callable(search.business.companies)
    assert callable(search.business.people)
    assert callable(search.ecommerce.products)
    for name in ("company", "people", "ecom"):
        assert not hasattr(search, name)
    assert not hasattr(search.business, "company")
    assert not hasattr(search.business, "products")
    assert not hasattr(search.ecommerce, "companies")
    assert not hasattr(search.ecommerce, "people")
    async_search = search if client_type is BrightDataClient else search._async
    assert async_search._bright_search_service is None


@pytest.mark.parametrize("client_type", [BrightDataClient, SyncBrightDataClient])
def test_ecommerce_product_annotations_match_supported_inputs(client_type):
    client = client_type(token="test_token_12345", auto_create_zones=False)
    hints = get_type_hints(client.search.ecommerce.products)
    assert hints["query"] == Dict[str, Any]
    assert hints["mode"] == Literal["ludicrous"]
    assert hints["return"] is BrightSearchPage


@pytest.mark.parametrize("namespace,name,category", PUBLIC_SEARCHES)
async def test_async_facade_uses_shared_engine_and_no_zones(body, namespace, name, category):
    client = BrightDataClient(token="test_token_12345", auto_create_zones=False)
    search = getattr(client.search, namespace)
    with patch(
        "brightdata.client.ZoneManager.ensure_required_zones", new_callable=AsyncMock
    ) as zones:
        async with client:
            assert search is getattr(client.search, namespace)
            session = client.engine._session
            session.request = AsyncMock(
                return_value=response(body, headers={"X-Debug-Trace-Page": "trace"})
            )
            page = await getattr(search, name)({}, mode="ludicrous", view="full")
            assert page.to_dict() == body
            assert page.response_headers == {"x-debug-trace-page": "trace"}
            assert client.search._bright_search_service.engine is client.engine
            cached = client.search._bright_search_service
            await getattr(search, name)({}, mode="ludicrous")
            assert client.search._bright_search_service is cached
            assert not session.closed
            assert session.request.await_count == 2
            assert session.request.call_args.kwargs["url"].endswith(f"/search/{category}")
        assert session.closed
        zones.assert_not_awaited()


@pytest.mark.parametrize("namespace,name,category", PUBLIC_SEARCHES)
async def test_async_facade_requires_initialization(namespace, name, category):
    client = BrightDataClient(token="test_token_12345", auto_create_zones=False)
    with pytest.raises(RuntimeError, match="not initialized"):
        await getattr(getattr(client.search, namespace), name)({}, mode="ludicrous")


@pytest.mark.parametrize("namespace,name,category", PUBLIC_SEARCHES)
def test_sync_facade_has_the_same_wire_contract_and_page(body, namespace, name, category):
    client = SyncBrightDataClient(token="test_token_12345", auto_create_zones=False)
    before_enter = getattr(client.search, namespace)
    with pytest.raises(RuntimeError, match="not initialized"):
        getattr(before_enter, name)({}, mode="ludicrous")
    retired = None
    with patch(
        "brightdata.client.ZoneManager.ensure_required_zones", new_callable=AsyncMock
    ) as zones:
        for _ in range(2):
            with client:
                search = getattr(client.search, namespace)
                assert search is getattr(client.search, namespace)
                assert search is not before_enter
                if retired is not None:
                    assert search is not retired
                    with pytest.raises(RuntimeError, match="not initialized"):
                        getattr(retired, name)({}, mode="ludicrous")
                session = client._async_client.engine._session
                session.request = AsyncMock(return_value=response(body))
                page = getattr(search, name)(
                    {},
                    mode="ludicrous",
                    source="future_source",
                    view={"fields": ["name"]},
                    limit=20,
                )
                assert isinstance(page, BrightSearchPage) and page.to_dict() == body
                session.request.assert_awaited_once()
                sent = session.request.call_args.kwargs
                assert sent["url"].endswith(f"/search/{category}")
                assert sent["json"] == {
                    "mode": "ludicrous",
                    "query": {},
                    "source": "future_source",
                    "view": {"fields": ["name"]},
                    "offset": 0,
                    "limit": 20,
                }
                retired = search
            assert session.closed
        zones.assert_not_awaited()
    with pytest.raises(RuntimeError, match="not initialized"):
        getattr(getattr(client.search, namespace), name)({}, mode="ludicrous")


@pytest.mark.parametrize("namespace,name,category", PUBLIC_SEARCHES)
async def test_sync_call_in_async_context_fails_before_creating_a_coroutine(
    namespace, name, category
):
    loop = asyncio.new_event_loop()
    async_service = MagicMock()
    try:
        service = SyncSearchService(async_service, loop)
        with pytest.raises(RuntimeError, match="async context"):
            getattr(getattr(service, namespace), name)({}, mode="ludicrous")
        getattr(getattr(async_service, namespace), name).assert_not_called()
    finally:
        loop.close()


@pytest.fixture
def wire_server(monkeypatch, body):
    """Real HTTP responses, including bodies aiohttp must reject while reading."""
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")

    @asynccontextmanager
    async def serve(status=200, payload=b"", *, headers=None, length=None, hold_open=False):
        requests = []
        handlers = set()
        disconnected = asyncio.Event()

        async def handle(reader, writer):
            task = asyncio.current_task()
            handlers.add(task)
            try:
                request = (await reader.readuntil(b"\r\n\r\n")).decode("ascii").split("\r\n")
                method, path, _ = request[0].split(" ")
                request_headers = {
                    name.lower(): value.strip()
                    for line in request[1:]
                    if ":" in line
                    for name, value in [line.split(":", 1)]
                }
                data = await reader.readexactly(int(request_headers.get("content-length", 0)))
                requests.append((method, path, data))
                response_status, response_body = status, payload
                response_headers = {
                    "Content-Type": "application/json",
                    "Content-Length": str(len(payload) if length is None else length),
                    "Connection": "close",
                    "X-Debug-Trace-Page": "local-trace",
                    "Retry-After": "2",
                    **(headers or {}),
                }
                if path == "/redirected":
                    response_status, response_body = 200, json.dumps(body).encode()
                    response_headers["Content-Length"] = str(len(response_body))
                head = f"HTTP/1.1 {response_status} Test\r\n" + "".join(
                    f"{key}: {value}\r\n" for key, value in response_headers.items()
                )
                writer.write(head.encode("ascii") + b"\r\n" + response_body)
                await writer.drain()
                if hold_open:
                    await reader.read()
            finally:
                writer.close()
                await writer.wait_closed()
                disconnected.set()
                handlers.discard(task)

        server = await asyncio.start_server(handle, "127.0.0.1", 0)
        try:
            yield SimpleNamespace(
                url=f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}",
                requests=requests,
                disconnected=disconnected,
            )
        finally:
            server.close()
            await server.wait_closed()
            pending = list(handlers)
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)

    return serve


def assert_wire_error_context(exc, peer, status):
    assert exc.status_code == status
    assert exc.url == f"{peer.url}/search/company"
    assert exc.method == "POST"
    assert exc.response_headers == {"x-debug-trace-page": "local-trace", "retry-after": "2"}
    assert len(peer.requests) == 1
    assert peer.requests[0][:2] == ("POST", "/search/company")


@pytest.mark.parametrize("status", [500, 502])
async def test_wire_http_failure_is_not_replayed_through_generic_backoff(wire_server, status):
    payload = b'{"req_id": "failed-search", "error": "upstream failed"}'
    async with wire_server(status, payload) as peer:
        async with BrightDataClient(token="local_test_token", auto_create_zones=False) as client:
            client.engine.BASE_URL = peer.url
            with pytest.raises(APIError) as error:
                await retry_with_backoff(
                    lambda: client.search.business.companies("query", mode="instant"),
                    max_retries=1,
                    initial_delay=0,
                )
            assert_wire_error_context(error.value, peer, status)
            assert error.value.req_id == "failed-search"
            assert error.value.retryable is False


@pytest.mark.parametrize("status", [500, 502])
async def test_wire_legacy_http_failure_still_retries(wire_server, status):
    async with wire_server(status, b'{"error": "upstream failed"}') as peer:
        async with AsyncEngine("local_test_token") as engine:
            engine.BASE_URL = peer.url

            async def request():
                async with engine.post("/legacy"):
                    pytest.fail("The HTTP error should be raised during entry")

            with pytest.raises(APIError) as error:
                await retry_with_backoff(request, max_retries=1, initial_delay=0)
            assert len(peer.requests) == 2
            assert error.value.retryable is True


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
async def test_wire_redirect_is_an_error_without_another_request(wire_server, status):
    async with wire_server(status, headers={"Location": "/redirected"}) as peer:
        async with BrightDataClient(token="local_test_token", auto_create_zones=False) as client:
            client.engine.BASE_URL = peer.url
            with pytest.raises(APIError, match="Unexpected Bright Search status") as error:
                await client.search.business.companies("query", mode="instant")
            assert_wire_error_context(error.value, peer, status)
            assert error.value.retryable is False


@pytest.mark.parametrize("status,next_method", [(302, "GET"), (307, "POST")])
async def test_wire_legacy_post_still_follows_redirects(wire_server, body, status, next_method):
    async with wire_server(status, headers={"Location": "/redirected"}) as peer:
        async with AsyncEngine("local_test_token") as engine:
            engine.BASE_URL = peer.url
            async with engine.post("/legacy", json_data={"query": "original"}) as resp:
                assert await resp.json() == body
        assert [request[:2] for request in peer.requests] == [
            ("POST", "/legacy"),
            (next_method, "/redirected"),
        ]


@pytest.mark.parametrize(
    "payload,length,error_type,cause_type",
    [
        (b'{"req_id": "partial"', 100, NetworkError, aiohttp.ClientPayloadError),
        (b'{"req_id": "ok", "data": "\xff"}', None, APIError, UnicodeDecodeError),
        (b"[" * 1500 + b"0" + b"]" * 1500, None, APIError, RecursionError),
    ],
    ids=["truncated", "invalid-utf8", "deep-json"],
)
async def test_wire_body_failures_use_sdk_errors(
    wire_server, payload, length, error_type, cause_type
):
    async with wire_server(payload=payload, length=length) as peer:
        async with BrightDataClient(token="local_test_token", auto_create_zones=False) as client:
            client.engine.BASE_URL = peer.url
            with pytest.raises(error_type) as error:
                await retry_with_backoff(
                    lambda: client.search.business.companies("query", mode="instant"),
                    max_retries=1,
                    initial_delay=0,
                )
            assert_wire_error_context(error.value, peer, 200)
            assert isinstance(error.value.__cause__, cause_type)
            assert error.value.retryable is False


@pytest.mark.parametrize(
    "status,error_type",
    [
        (400, APIError),
        (401, AuthenticationError),
        (403, AuthenticationError),
        (429, RateLimitError),
        (500, APIError),
        (502, APIError),
    ],
)
@pytest.mark.parametrize(
    "payload",
    [
        b'{"req_id": "recoverable", "error": "\xff"}',
        b'{"req_id": "corrupt\xff", "error": "failed"}',
    ],
    ids=["outside-request-id", "inside-request-id"],
)
async def test_wire_invalid_error_encoding_keeps_http_classification(
    wire_server, status, error_type, payload
):
    async with wire_server(status, payload) as peer:
        async with BrightDataClient(token="local_test_token", auto_create_zones=False) as client:
            client.engine.BASE_URL = peer.url
            with pytest.raises(error_type) as error:
                await client.search.business.companies("query", mode="instant")
            assert_wire_error_context(error.value, peer, status)
            assert error.value.req_id is None
            assert error.value.response_json is None
            assert "\ufffd" in error.value.raw
            assert isinstance(error.value.__cause__, UnicodeDecodeError)
            if status == 429:
                assert error.value.retry_after == 2
                assert error.value.retryable is False


async def test_wire_valid_unicode_error_json_remains_authoritative(wire_server):
    data = {"req_id": "valid-\ufffd", "error": "failed"}
    async with wire_server(500, json.dumps(data).encode()) as peer:
        async with BrightDataClient(token="local_test_token", auto_create_zones=False) as client:
            client.engine.BASE_URL = peer.url
            with pytest.raises(APIError) as error:
                await client.search.business.companies("query", mode="instant")
            assert_wire_error_context(error.value, peer, 500)
            assert error.value.req_id == data["req_id"]
            assert error.value.response_json == data
            assert error.value.__cause__ is None


@pytest.mark.parametrize("status,error_type", [(429, RateLimitError), (500, APIError)])
async def test_wire_truncated_error_keeps_known_status_and_headers(wire_server, status, error_type):
    async with wire_server(status, b'{"req_id": "incomplete"', length=100) as peer:
        async with BrightDataClient(token="local_test_token", auto_create_zones=False) as client:
            client.engine.BASE_URL = peer.url
            with pytest.raises(error_type) as error:
                await client.search.business.companies("query", mode="instant")
            assert_wire_error_context(error.value, peer, status)
            assert isinstance(error.value.__cause__, aiohttp.ClientPayloadError)
            assert error.value.req_id is None and error.value.response_json is None
            if status == 429:
                assert error.value.retry_after == 2 and error.value.retryable is False


async def test_wire_legacy_error_decoding_remains_strict(wire_server):
    async with wire_server(400, b"\xff") as peer:
        async with AsyncEngine("local_test_token") as engine:
            engine.BASE_URL = peer.url
            with pytest.raises(UnicodeDecodeError):
                async with engine.post("/legacy"):
                    pytest.fail("Invalid encoding should fail before entry")
        assert len(peer.requests) == 1


@pytest.mark.parametrize("status", [200, 429])
async def test_wire_body_timeout_stays_timeout_and_closes_response(wire_server, status):
    async with wire_server(status, length=100, hold_open=True) as peer:
        async with BrightDataClient(token="local_test_token", auto_create_zones=False) as client:
            client.engine.BASE_URL = peer.url
            client.engine.timeout = aiohttp.ClientTimeout(total=0.2)
            with pytest.raises(TimeoutError) as error:
                await retry_with_backoff(
                    lambda: client.search.business.companies("query", mode="instant"),
                    max_retries=1,
                    initial_delay=0,
                )
            assert_wire_error_context(error.value, peer, status)
            assert error.value.retry_after == 2
            assert error.value.req_id is None and error.value.response_json is None
            assert isinstance(error.value.__cause__, asyncio.TimeoutError)
            assert not is_retryable(error.value)
            await asyncio.wait_for(peer.disconnected.wait(), timeout=2)
            assert len(peer.requests) == 1
            assert not client.engine._session.closed


@pytest.mark.parametrize("status", [200, 429])
async def test_wire_body_cancellation_propagates_and_closes_response(
    wire_server, monkeypatch, status
):
    reading = asyncio.Event()
    original_text = aiohttp.ClientResponse.text

    async def observe_read(response, *args, **kwargs):
        reading.set()
        return await original_text(response, *args, **kwargs)

    monkeypatch.setattr(aiohttp.ClientResponse, "text", observe_read)
    async with wire_server(status, length=100, hold_open=True) as peer:
        async with BrightDataClient(token="local_test_token", auto_create_zones=False) as client:
            client.engine.BASE_URL = peer.url
            task = asyncio.create_task(client.search.business.companies("query", mode="instant"))
            try:
                await asyncio.wait_for(reading.wait(), timeout=2)
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
                await asyncio.wait_for(peer.disconnected.wait(), timeout=2)
                assert len(peer.requests) == 1
                assert not client.engine._session.closed
            finally:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
