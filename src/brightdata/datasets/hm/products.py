"""
H&M Products dataset.

Fashion product listings from H&M.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class HMProducts(BaseDataset):
    """H&M Products dataset."""

    DATASET_ID = "gd_lebec5ir293umvxh5g"
    NAME = "hm_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
