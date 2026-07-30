"""
Montblanc Products dataset.

Luxury product listings from Montblanc.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class MontblancProducts(BaseDataset):
    """Montblanc Products dataset."""

    DATASET_ID = "gd_lhahz3n9dr6srx4cm"
    NAME = "montblanc_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: dict[str, list[str]] | None = None
