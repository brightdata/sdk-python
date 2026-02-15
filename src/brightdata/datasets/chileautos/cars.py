"""
Chileautos Chile dataset.

Car listings from Chileautos (Chile).

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class ChileautosChile(BaseDataset):
    """Chileautos Chile car listings dataset."""

    DATASET_ID = "gd_lfsbqgb01iiit5ppju"
    NAME = "chileautos_chile"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
