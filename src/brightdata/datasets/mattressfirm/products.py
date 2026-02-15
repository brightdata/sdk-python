"""
Mattressfirm Products dataset.

Mattress and bedding product listings from Mattress Firm.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class MattressfirmProducts(BaseDataset):
    """Mattressfirm Products dataset."""

    DATASET_ID = "gd_legw5t6c2bvw9d7e4k"
    NAME = "mattressfirm_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
