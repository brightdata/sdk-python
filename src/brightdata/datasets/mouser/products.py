"""
Mouser Products dataset.

Electronic components product listings from Mouser Electronics.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class MouserProducts(BaseDataset):
    """Mouser Products dataset."""

    DATASET_ID = "gd_lfjty8942ogxzhmp8t"
    NAME = "mouser_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
