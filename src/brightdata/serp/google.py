"""Google SERP service."""

from typing import Optional

from ..core.engine import AsyncEngine
from .base import BaseSERPService
from .data_normalizer import GoogleDataNormalizer
from .url_builder import GoogleURLBuilder


class GoogleSERPService(BaseSERPService):
    """
    Google Search Engine Results Page service.

    Provides normalized Google search results including:
    - Organic search results with ranking positions
    - Featured snippets
    - Knowledge panels
    - People Also Ask
    - Related searches
    - Sponsored/ad results
    """

    SEARCH_ENGINE = "google"

    def __init__(
        self,
        engine: AsyncEngine,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """Initialize Google SERP service."""
        url_builder = GoogleURLBuilder()
        data_normalizer = GoogleDataNormalizer()
        super().__init__(
            engine=engine,
            url_builder=url_builder,
            data_normalizer=data_normalizer,
            timeout=timeout,
            max_retries=max_retries,
        )
