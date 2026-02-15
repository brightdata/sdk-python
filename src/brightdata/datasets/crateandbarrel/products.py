"""
Crate and Barrel Products dataset.

Home furnishing and decor product listings from Crate and Barrel.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class CrateAndBarrelProducts(BaseDataset):
    """Crate and Barrel Products dataset."""

    DATASET_ID = "gd_lemtcp2p2qdyd24vq5"
    NAME = "crateandbarrel_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
