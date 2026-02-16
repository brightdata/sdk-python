"""
Mediamarkt.de Products dataset.

Product listings from Mediamarkt Germany with prices and details.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class MediamarktProducts(BaseDataset):
    """
    Mediamarkt.de Products dataset.

    Electronics and appliance products from Mediamarkt Germany.

    Example:
        >>> products = client.datasets.mediamarkt_products
        >>> metadata = await products.get_metadata()
        >>> snapshot_id = await products(records_limit=100)
        >>> data = await products.download(snapshot_id)
    """

    DATASET_ID = "gd_lbl2lo6y11m37z3gwq"
    NAME = "mediamarkt_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
