"""
Bottega Veneta Products dataset.

Luxury product listings from Bottega Veneta.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class BottegaVenetaProducts(BaseDataset):
    """Bottega Veneta Products dataset."""

    DATASET_ID = "gd_lh7os5q91y20h69xj"
    NAME = "bottegaveneta_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
