"""
Fendi Products dataset.

Luxury product listings from Fendi.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class FendiProducts(BaseDataset):
    """Fendi Products dataset."""

    DATASET_ID = "gd_lbqsfpfk71ubir3pi"
    NAME = "fendi_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
