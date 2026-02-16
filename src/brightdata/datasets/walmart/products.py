"""
Walmart Products dataset.

Product listings from Walmart with prices, ratings, and details.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class WalmartProducts(BaseDataset):
    """
    Walmart Products dataset.

    Product listings with prices, ratings, availability,
    and seller information.

    Example:
        >>> products = client.datasets.walmart_products
        >>> metadata = await products.get_metadata()
        >>> snapshot_id = await products(
        ...     filter={"name": "category", "operator": "=", "value": "Electronics"},
        ...     records_limit=100
        ... )
        >>> data = await products.download(snapshot_id)
    """

    DATASET_ID = "gd_l95fol7l1ru6rlo116"
    NAME = "walmart_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
