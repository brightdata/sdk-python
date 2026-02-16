"""
Toctoc Properties dataset.

Real estate property listings from Toctoc.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class ToctocProperties(BaseDataset):
    """Toctoc Properties dataset."""

    DATASET_ID = "gd_lgfdx3l01behlrboh7"
    NAME = "toctoc_properties"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
