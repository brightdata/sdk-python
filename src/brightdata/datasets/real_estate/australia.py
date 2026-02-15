"""
Australia Real Estate Properties dataset.

Property listings from Australia with prices, locations, and details.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class AustraliaRealEstate(BaseDataset):
    """
    Australia Real Estate Properties dataset.

    Property listings with prices, locations, features,
    and agent information.

    Example:
        >>> properties = client.datasets.australia_real_estate
        >>> metadata = await properties.get_metadata()
        >>> snapshot_id = await properties(
        ...     filter={"name": "state", "operator": "=", "value": "NSW"},
        ...     records_limit=100
        ... )
        >>> data = await properties.download(snapshot_id)
    """

    DATASET_ID = "gd_l3cvjh111l943r4awk"
    NAME = "australia_real_estate"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
