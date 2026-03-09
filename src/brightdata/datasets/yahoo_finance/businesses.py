"""
Yahoo Finance Businesses dataset.

Yahoo Finance business information dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class YahooFinanceBusinesses(BaseDataset):
    """YahooFinanceBusinesses dataset."""

    DATASET_ID = "gd_lmrpz3vxmz972ghd7"
    NAME = "yahoo_finance_businesses"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
