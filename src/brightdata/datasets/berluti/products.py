"""
Berluti Products dataset.

Luxury product listings from Berluti.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class BerlutiProducts(BaseDataset):
    """Berluti Products dataset."""

    DATASET_ID = "gd_lh7sef5p16tcupyuy3"
    NAME = "berluti_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
