"""
Webmotors Brasil dataset.

Vehicle listings from Webmotors (Brazil).

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class WebmotorsBrasil(BaseDataset):
    """Webmotors Brasil vehicle listings dataset."""

    DATASET_ID = "gd_ld73zt91j10sphddj"
    NAME = "webmotors_brasil"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
