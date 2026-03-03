"""
Facebook Events dataset.

Facebook events with dates, locations, descriptions, and attendee counts.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class FacebookEvents(BaseDataset):
    """FacebookEvents dataset."""

    DATASET_ID = "gd_m14sd0to1jz48ppm51"
    NAME = "facebook_events"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
