"""
Digikey Products dataset.

Electronic components from Digikey.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class DigikeyProducts(BaseDataset):
    """Digikey Products dataset."""

    DATASET_ID = "gd_lj74waf72416ro0k65"
    NAME = "digikey_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
