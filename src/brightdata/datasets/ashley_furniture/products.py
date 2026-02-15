"""
Ashley Furniture Products dataset.

Furniture product listings from Ashley Furniture.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class AshleyFurnitureProducts(BaseDataset):
    """Ashley Furniture Products dataset."""

    DATASET_ID = "gd_le1ddqrs16uevi5vc4"
    NAME = "ashley_furniture_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
