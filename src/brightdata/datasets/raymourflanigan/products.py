"""
Raymour and Flanigan Products dataset.

Furniture product listings from Raymour and Flanigan.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class RaymourFlaniganProducts(BaseDataset):
    """Raymour and Flanigan Products dataset."""

    DATASET_ID = "gd_lf8cwb8wxoiqarizb"
    NAME = "raymourflanigan_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: dict[str, list[str]] | None = None
