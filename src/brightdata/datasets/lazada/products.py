"""
Lazada Products dataset.

Product listings from Lazada e-commerce platform.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class LazadaProducts(BaseDataset):
    """Lazada Products dataset."""

    DATASET_ID = "gd_lk14r4zxuiw2uxpk6"
    NAME = "lazada_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
