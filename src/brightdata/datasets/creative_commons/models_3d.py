"""
Creative Commons 3D Models dataset.

Creative Commons 3D models dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class CreativeCommons3DModels(BaseDataset):
    """CreativeCommons3DModels dataset."""

    DATASET_ID = "gd_m4jr2hyr2kfhtvba6e"
    NAME = "creative_commons_3d_models"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
