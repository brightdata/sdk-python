"""
GitHub Repositories dataset.

GitHub repository information dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class GithubRepositories(BaseDataset):
    """GithubRepositories dataset."""

    DATASET_ID = "gd_lyrexgxc24b3d4imjt"
    NAME = "github_repositories"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
