"""
LinkedIn Profiles Job Listings dataset.

Job listings associated with LinkedIn profiles including role details and requirements.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class LinkedInProfilesJobListings(BaseDataset):
    """LinkedInProfilesJobListings dataset."""

    DATASET_ID = "gd_m487ihp32jtc4ujg45"
    NAME = "linkedin_profiles_job_listings"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
