"""Bing SERP service."""

from typing import Optional
from .base import BaseSERPService
from .url_builder import BingURLBuilder
from .data_normalizer import BingDataNormalizer
from ...core.engine import AsyncEngine


class BingSERPService(BaseSERPService):
    """Bing Search Engine Results Page service."""

    SEARCH_ENGINE = "bing"

    def __init__(
        self,
        engine: AsyncEngine,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """Initialize Bing SERP service."""
        url_builder = BingURLBuilder()
        data_normalizer = BingDataNormalizer()
        super().__init__(
            engine=engine,
            url_builder=url_builder,
            data_normalizer=data_normalizer,
            timeout=timeout,
            max_retries=max_retries,
        )
