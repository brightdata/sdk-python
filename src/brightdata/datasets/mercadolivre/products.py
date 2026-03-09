"""
MercadoLivre Products dataset.

MercadoLivre products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class MercadolivreProducts(BaseDataset):
    """MercadolivreProducts dataset."""

    DATASET_ID = "gd_m7re62tb1w88ymy86r"
    NAME = "mercadolivre_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
