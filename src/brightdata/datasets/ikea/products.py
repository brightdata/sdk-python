"""
Ikea Products dataset.

Furniture and home product listings from Ikea.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class IkeaProducts(BaseDataset):
    """Ikea Products dataset."""

    DATASET_ID = "gd_le2lfu10qrjmrqo60"
    NAME = "ikea_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
