"""
Quora Posts dataset.

Quora posts dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class QuoraPosts(BaseDataset):
    """QuoraPosts dataset."""

    DATASET_ID = "gd_lvz1rbj81afv3m6n5y"
    NAME = "quora_posts"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
