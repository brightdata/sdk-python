"""
Macys Products dataset.

Macys.com products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class MacysProducts(BaseDataset):
    """MacysProducts dataset."""

    DATASET_ID = "gd_miebqh4a18ivg65bpa"
    NAME = "macys_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: dict[str, list[str]] | None = None
