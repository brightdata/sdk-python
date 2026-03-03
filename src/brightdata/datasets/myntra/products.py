"""
Myntra Products dataset.

Myntra products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class MyntraProducts(BaseDataset):
    """MyntraProducts dataset."""

    DATASET_ID = "gd_lptvxr8b1qx1d9thgp"
    NAME = "myntra_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
