"""
Lego Products dataset.

Product listings from Lego.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class LegoProducts(BaseDataset):
    """Lego Products dataset."""

    DATASET_ID = "gd_leenwt162rg85apy87"
    NAME = "lego_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
