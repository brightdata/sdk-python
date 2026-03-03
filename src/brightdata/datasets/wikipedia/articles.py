"""
Wikipedia Articles dataset.

Wikipedia articles dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class WikipediaArticles(BaseDataset):
    """WikipediaArticles dataset."""

    DATASET_ID = "gd_lr9978962kkjr3nx49"
    NAME = "wikipedia_articles"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
