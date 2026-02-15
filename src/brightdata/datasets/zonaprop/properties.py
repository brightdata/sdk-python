"""
Zonaprop Argentina dataset.

Real estate property listings from Zonaprop Argentina.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class ZonapropArgentina(BaseDataset):
    """Zonaprop Argentina real estate dataset."""

    DATASET_ID = "gd_lfsbhfgo2bglgrecm6"
    NAME = "zonaprop_argentina"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
