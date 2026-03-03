"""
Creative Commons Images dataset.

Creative Commons images dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class CreativeCommonsImages(BaseDataset):
    """CreativeCommonsImages dataset."""

    DATASET_ID = "gd_m23cxdw82ct6k022y3"
    NAME = "creative_commons_images"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
