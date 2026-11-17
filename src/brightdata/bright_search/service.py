"""Direct Bright Search requests using the client's shared async engine."""

import asyncio
import json
from http import HTTPStatus
from typing import Any, Dict, Optional

import aiohttp

from ..core.engine import AsyncEngine
from ..exceptions import (
    APIError,
    BrightDataError,
    NetworkError,
    RequestTimeoutError,
    ValidationError,
)
from ..utils.http import diagnostic_response_headers, parse_retry_after
from .models import (
    BrightSearchDebug,
    BrightSearchMode,
    BrightSearchPage,
    BrightSearchQuery,
    BrightSearchView,
)


class BrightSearchService:
    """Search a supported category and return one page directly.

    Requests are not redirected, retried, or paginated automatically. Failures
    opt out of the generic retry helper because the search may have executed.
    Field/operator validation, natural-language planning, and ranking remain with the API.
    The owning client manages the engine's session.
    """

    _CATEGORY_MODES = {
        "company": ("ludicrous", "instant", "smart"),
        "people": ("ludicrous", "instant", "smart"),
        "ecommerce": ("ludicrous",),
    }
    _MODE_CAPS = {"ludicrous": (100, 1000), "instant": (100, 100), "smart": (10, 100)}
    _DEBUG_KEYS = frozenset({"explain", "benchmark", "trace", "__overrides__"})

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    async def search(
        self,
        category: str,
        query: BrightSearchQuery,
        *,
        mode: BrightSearchMode,
        source: Optional[str] = None,
        view: Optional[BrightSearchView] = None,
        offset: int = 0,
        limit: int = 10,
        debug: Optional[BrightSearchDebug] = None,
    ) -> BrightSearchPage:
        """POST one query to Company, People, or E-commerce search.

        Args:
            category: company, people, or ecommerce. Flights is experimental and
                is not exposed by this service.
            query: A native structured object for ludicrous mode, or a string
                of at most 200 characters for instant/smart.
            mode: Explicit search mode. E-commerce supports ludicrous only.
            source: Source name; None uses the category's server default.
            view: View profile or {"fields": [...]}; None uses id_only.
            offset: Page offset, up to 1000 for ludicrous. Instant and smart
                require offset + limit <= 100.
            limit: Page size, up to 100 (10 for smart).
            debug: Explicit diagnostic wire keys for a debug-enabled account.
                Nested null, false, and zero values are preserved.

        Returns:
            BrightSearchPage preserving request identity and coverage metadata.

        Raises:
            ValidationError: Invalid request shape, capability, or JSON payload.
            APIError: Upstream failure or malformed search response. Rate limits
                raise RateLimitError with retry_after; callers control recovery.
            NetworkError: The response body could not be fully received.
            RequestTimeoutError: Request/body timeout with available context;
                also catchable as the built-in TimeoutError.
        """
        payload = self._build_payload(category, query, mode, source, view, offset, limit, debug)
        endpoint = f"/search/{category}"
        try:
            return await self._request_page(endpoint, payload)
        except BrightDataError as exc:
            # This includes errors raised while entering the engine context.
            # An HTTP failure or an unreadable response can follow execution.
            exc.retryable = False
            raise

    async def _request_page(self, endpoint: str, payload: Dict[str, Any]) -> BrightSearchPage:
        async with self.engine.post(
            endpoint, json_data=payload, preserve_error_response=True, allow_redirects=False
        ) as response:
            response_headers = diagnostic_response_headers(response.headers)
            context: Dict[str, Any] = {
                "status_code": response.status,
                "url": f"{self.engine.BASE_URL}{endpoint}",
                "method": "POST",
                "retryable": False,
                "response_headers": response_headers,
                "retry_after": parse_retry_after(response.headers),
            }
            try:
                text = await response.text()
                context["raw"] = text
                data = json.loads(text)
            except asyncio.TimeoutError as exc:
                raise RequestTimeoutError(
                    f"Request timeout after {self.engine.timeout.total} seconds", **context
                ) from exc
            except (aiohttp.ClientError, OSError) as exc:
                raise NetworkError(
                    f"Network error reading Bright Search response: {exc}", **context
                ) from exc
            except (ValueError, TypeError, RecursionError) as exc:
                if isinstance(exc, UnicodeDecodeError):
                    context["raw"] = exc.object.decode(exc.encoding, errors="replace")
                message = (
                    f"Unexpected Bright Search status: {response.status}"
                    if response.status != HTTPStatus.OK
                    else "Bright Search returned an invalid JSON response"
                )
                raise APIError(message, **context) from exc

            context.update(
                req_id=data.get("req_id") if isinstance(data, dict) else None,
                response_json=data,
            )
            if response.status != HTTPStatus.OK:
                raise APIError(f"Unexpected Bright Search status: {response.status}", **context)
            try:
                return BrightSearchPage(raw=data, response_headers=response_headers)
            except ValueError as exc:
                raise APIError(f"Invalid Bright Search response: {exc}", **context) from exc

    @classmethod
    def _build_payload(
        cls,
        category: str,
        query: BrightSearchQuery,
        mode: BrightSearchMode,
        source: Optional[str],
        view: Optional[BrightSearchView],
        offset: int,
        limit: int,
        debug: Optional[BrightSearchDebug],
    ) -> Dict[str, Any]:
        if not isinstance(category, str) or category not in cls._CATEGORY_MODES:
            raise ValidationError("category must be company, people, or ecommerce")
        if not isinstance(mode, str) or mode not in cls._CATEGORY_MODES[category]:
            raise ValidationError(
                f"Unsupported mode {mode!r} for {category}; "
                f"expected one of {cls._CATEGORY_MODES[category]}"
            )
        if mode == "ludicrous":
            if not isinstance(query, dict):
                raise ValidationError("ludicrous query must be a structured object")
        elif not isinstance(query, str) or len(query) > 200:
            raise ValidationError("instant/smart query must be a string of at most 200 characters")

        max_limit, max_offset = cls._MODE_CAPS[mode]
        for name, value, maximum in (("offset", offset, max_offset), ("limit", limit, max_limit)):
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
                or value > maximum
            ):
                raise ValidationError(f"{name} must be an integer between 0 and {maximum}")
        if mode in ("instant", "smart") and offset + limit > 100:
            raise ValidationError("instant and smart require offset + limit <= 100")
        if source is not None and not isinstance(source, str):
            raise ValidationError("source must be a string")
        if view is not None and not isinstance(view, str):
            if (
                not isinstance(view, dict)
                or set(view) != {"fields"}
                or not isinstance(view["fields"], list)
                or not all(isinstance(name, str) for name in view["fields"])
            ):
                raise ValidationError('view must be a profile name or {"fields": [...]}')
        if (
            category == "ecommerce"
            and source in (None, "retail_products_live")
            and view == "summary"
        ):
            raise ValidationError("retail_products_live does not support the summary view")
        if debug is not None:
            if not isinstance(debug, dict) or not cls._DEBUG_KEYS.issuperset(debug):
                raise ValidationError(
                    "debug may contain only explain, benchmark, trace, and __overrides__"
                )

        payload: Dict[str, Any] = {"mode": mode, "query": query, "offset": offset, "limit": limit}
        if source is not None:
            payload["source"] = source
        if view is not None:
            payload["view"] = view
        if debug is not None:
            payload.update(debug)
        cls._validate_json_payload(payload)
        return payload

    @staticmethod
    def _validate_json_payload(payload: Dict[str, Any]) -> None:
        """Reject invalid JSON and object-key coercion without changing the input."""
        try:
            # The encoder checks unsupported values, non-finite numbers, cycles,
            # and nesting it cannot serialize before the request is dispatched.
            json.dumps(payload, allow_nan=False)
            pending = [payload]
            while pending:
                value = pending.pop()
                if isinstance(value, dict):
                    if any(not isinstance(key, str) for key in value):
                        raise ValueError("JSON object keys must be strings")
                    pending.extend(value.values())
                elif isinstance(value, (list, tuple)):
                    pending.extend(value)
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise ValidationError(f"Bright Search payload must be valid JSON: {exc}") from exc
