"""
BBC News dataset.

BBC news articles dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class BBCNews(BaseDataset):
    """BBCNews dataset."""

    DATASET_ID = "gd_ly5lkfzd1h8c85feyh"
    NAME = "bbc_news"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
