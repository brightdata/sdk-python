"""
Google News dataset.

Google News articles dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class GoogleNews(BaseDataset):
    """GoogleNews dataset."""

    DATASET_ID = "gd_lnsxoxzi1omrwnka5r"
    NAME = "google_news"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
