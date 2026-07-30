"""
American Eagle Products dataset.

Fashion product listings from American Eagle (AE.com).

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class AmericanEagleProducts(BaseDataset):
    """American Eagle Products dataset."""

    DATASET_ID = "gd_le6plu065keypwyir"
    NAME = "american_eagle_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: dict[str, list[str]] | None = None
