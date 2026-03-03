"""
Zillow Price History dataset.

Historical pricing data for Zillow properties with date and price change records.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class ZillowPriceHistory(BaseDataset):
    """ZillowPriceHistory dataset."""

    DATASET_ID = "gd_lxu1cz9r88uiqsosl"
    NAME = "zillow_price_history"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
