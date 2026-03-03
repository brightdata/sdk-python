"""
Realtor International Properties dataset.

Realtor international property listings dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class RealtorInternationalProperties(BaseDataset):
    """RealtorInternationalProperties dataset."""

    DATASET_ID = "gd_m517agnc1jppzwgtmw"
    NAME = "realtor_international_properties"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
