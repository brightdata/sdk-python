"""
Instagram Profiles dataset.

Instagram user profiles with follower counts, bio, posts, and engagement data.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class InstagramProfiles(BaseDataset):
    """
    Instagram Profiles dataset.

    User profiles with follower metrics, bio information,
    and engagement statistics.

    Example:
        >>> profiles = client.datasets.instagram_profiles
        >>> metadata = await profiles.get_metadata()
        >>> snapshot_id = await profiles(
        ...     filter={"name": "followers", "operator": ">=", "value": "10000"},
        ...     records_limit=100
        ... )
        >>> data = await profiles.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vikfch901nx3by4"
    NAME = "instagram_profiles"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
