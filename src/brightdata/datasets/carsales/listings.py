"""
Carsales Listings dataset.

Carsales car listings dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class CarsalesListings(BaseDataset):
    """CarsalesListings dataset."""

    DATASET_ID = "gd_m8h7qkn317z9rvlngb"
    NAME = "carsales_listings"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
