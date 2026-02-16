"""
L.L. Bean Products dataset.

Outdoor and casual product listings from L.L. Bean.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class LLBeanProducts(BaseDataset):
    """L.L. Bean Products dataset."""

    DATASET_ID = "gd_lemtwv4s1mglzlzh57"
    NAME = "llbean_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
