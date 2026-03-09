"""
Ozon Products dataset.

Ozon.ru products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class OzonProducts(BaseDataset):
    """OzonProducts dataset."""

    DATASET_ID = "gd_lutq85sl13rlndbzai"
    NAME = "ozon_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
