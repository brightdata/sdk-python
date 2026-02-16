"""
OLX Brazil dataset.

Marketplace ads from OLX Brazil.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class OLXBrazil(BaseDataset):
    """OLX Brazil marketplace ads dataset."""

    DATASET_ID = "gd_lguvsr0wp4rx7fjfo"
    NAME = "olx_brazil"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
