"""
X (formerly Twitter) Posts dataset.

X (formerly Twitter) posts dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class XTwitterPosts(BaseDataset):
    """XTwitterPosts dataset."""

    DATASET_ID = "gd_lwxkxvnf1cynvib9co"
    NAME = "x_twitter_posts"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: dict[str, list[str]] | None = None
