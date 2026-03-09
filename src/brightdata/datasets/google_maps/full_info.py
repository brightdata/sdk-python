"""
Google Maps Full Info dataset.

Complete Google Maps business information with details, hours, and contact data.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class GoogleMapsFullInfo(BaseDataset):
    """GoogleMapsFullInfo dataset."""

    DATASET_ID = "gd_m8ebnr0q2qlklc02fz"
    NAME = "google_maps_full_info"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
