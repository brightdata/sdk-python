"""
Facebook Marketplace dataset.

Facebook Marketplace listings with product details, pricing, and seller information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class FacebookMarketplace(BaseDataset):
    """FacebookMarketplace dataset."""

    DATASET_ID = "gd_lvt9iwuh6fbcwmx1a"
    NAME = "facebook_marketplace"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
