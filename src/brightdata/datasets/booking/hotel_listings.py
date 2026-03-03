"""
Booking Hotel Listings dataset.

Booking.com hotel listings dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class BookingHotelListings(BaseDataset):
    """BookingHotelListings dataset."""

    DATASET_ID = "gd_m5mbdl081229ln6t4a"
    NAME = "booking_hotel_listings"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
