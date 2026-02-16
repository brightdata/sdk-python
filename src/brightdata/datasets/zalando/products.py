"""
Zalando Products dataset.

Fashion product listings from Zalando.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class ZalandoProducts(BaseDataset):
    """Zalando Products dataset."""

    DATASET_ID = "gd_lbqj6l5s28ofha6mlk"
    NAME = "zalando_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
