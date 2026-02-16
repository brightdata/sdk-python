"""
Indeed Job Listings dataset.

Job postings from Indeed with company info, salary, and requirements.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class IndeedJobs(BaseDataset):
    """
    Indeed Job Listings dataset.

    Job postings with company information, salary ranges,
    requirements, and application details.

    Example:
        >>> jobs = client.datasets.indeed_jobs
        >>> metadata = await jobs.get_metadata()
        >>> snapshot_id = await jobs(
        ...     filter={"name": "job_title", "operator": "contains", "value": "Engineer"},
        ...     records_limit=100
        ... )
        >>> data = await jobs.download(snapshot_id)
    """

    DATASET_ID = "gd_l4dx9j9sscpvs7no2"
    NAME = "indeed_jobs"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
