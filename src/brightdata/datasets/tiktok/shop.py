"""
TikTok Shop dataset.

TikTok Shop product listings with pricing, ratings, and seller details.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class TikTokShop(BaseDataset):
    """TikTokShop dataset."""

    DATASET_ID = "gd_m45m1u911dsa4274pi"
    NAME = "tiktok_shop"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
