"""
CNN News dataset.

CNN news articles dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class CNNNews(BaseDataset):
    """CNNNews dataset."""

    DATASET_ID = "gd_lycz8783197ch4wvwg"
    NAME = "cnn_news"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
