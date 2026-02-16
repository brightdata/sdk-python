"""
Inmuebles24 Mexico dataset.

Real estate property listings from Inmuebles24 Mexico.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class Inmuebles24Mexico(BaseDataset):
    """Inmuebles24 Mexico real estate dataset."""

    DATASET_ID = "gd_lfsa1vgv183347v45m"
    NAME = "inmuebles24_mexico"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
