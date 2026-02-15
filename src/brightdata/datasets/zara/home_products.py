"""
Zara Home Products dataset.

Home decor product listings from Zara Home.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class ZaraHomeProducts(BaseDataset):
    """Zara Home Products dataset."""

    DATASET_ID = "gd_lcx5utgek9mxrsiie"
    NAME = "zara_home_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
