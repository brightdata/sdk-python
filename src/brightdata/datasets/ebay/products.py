"""
eBay Products dataset.

eBay products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class EbayProducts(BaseDataset):
    """EbayProducts dataset."""

    DATASET_ID = "gd_ltr9mjt81n0zzdk1fb"
    NAME = "ebay_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: dict[str, list[str]] | None = None
