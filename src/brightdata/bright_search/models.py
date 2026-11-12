"""Bright Search response models and request types."""

from __future__ import annotations

import json
import math
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast

BrightSearchMode = Literal["ludicrous", "instant", "smart"]
BrightSearchQuery = Union[str, Dict[str, Any]]
BrightSearchView = Union[str, Dict[str, List[str]]]


class BrightSearchDebug(TypedDict, total=False):
    """Optional, unstable controls requiring a debug-enabled account."""

    explain: Union[bool, int, Dict[str, Any]]
    benchmark: Union[bool, int]
    trace: Union[bool, int]
    __overrides__: Optional[Dict[str, Any]]


class BrightSearchMeta(TypedDict):
    """Paging metadata. matched is a reached count, not generally a total."""

    matched: Union[int, float]
    coverage_percent: Union[int, float]
    offset: int
    limit: int


class _DocumentDiagnostics(TypedDict, total=False):
    score: float


class BrightSearchDocument(_DocumentDiagnostics):
    """A record's identity and projected data; all fields inside data are optional."""

    bright_id: str
    data: Dict[str, Any]


@dataclass
class BrightSearchPage:
    """One search response, preserving its original body and document order.

    Attributes:
        raw: Original JSON body, including any additional or diagnostic fields.
             Accessors refer to this mapping rather than duplicating its values.
        response_headers: Selected response headers, separate from the JSON body.

    Raises:
        ValueError: If the response does not contain a valid search envelope.
    """

    raw: Dict[str, Any] = field(repr=False)
    response_headers: Dict[str, str] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.raw, dict):
            raise ValueError("response must be an object")
        for name in ("req_id", "source"):
            if not isinstance(self.raw.get(name), str):
                raise ValueError(f"{name} must be a string")

        meta = self.raw.get("meta")
        if not isinstance(meta, dict):
            raise ValueError("meta must be an object")
        for name in ("matched", "coverage_percent"):
            value = meta.get(name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or (isinstance(value, float) and not math.isfinite(value))
            ):
                raise ValueError(f"meta.{name} must be a finite number")
        for name in ("offset", "limit"):
            value = meta.get(name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"meta.{name} must be an integer")

        documents = self.raw.get("documents")
        if not isinstance(documents, list):
            raise ValueError("documents must be a list")
        for document in documents:
            if not isinstance(document, dict):
                raise ValueError("each document must be an object")
            if not isinstance(document.get("bright_id"), str):
                raise ValueError("document.bright_id must be a string")
            if not isinstance(document.get("data"), dict):
                raise ValueError("document.data must be an object")

    @property
    def req_id(self) -> str:
        return self.raw["req_id"]

    @property
    def source(self) -> str:
        return self.raw["source"]

    @property
    def meta(self) -> BrightSearchMeta:
        return cast(BrightSearchMeta, self.raw["meta"])

    @property
    def documents(self) -> List[BrightSearchDocument]:
        return cast(List[BrightSearchDocument], self.raw["documents"])

    @property
    def explain(self) -> Any:
        """Diagnostic output, if supplied; its internal shape is not stable."""
        return self.raw.get("__explain__")

    def to_dict(self) -> Dict[str, Any]:
        """Copy the wire body, preserving missing keys, nulls, and extra fields."""
        return deepcopy(self.raw)

    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize only the response body, without transport headers."""
        return json.dumps(self.raw, indent=indent, ensure_ascii=False)

    def __repr__(self) -> str:
        return (
            f"<BrightSearchPage source={self.source!r} "
            f"documents={len(self.documents)} req_id={self.req_id!r}>"
        )
