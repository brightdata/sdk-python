"""Yandex SERP service."""

from typing import Optional
from .base import BaseSERPService
from .url_builder import YandexURLBuilder
from .data_normalizer import YandexDataNormalizer
from ...core.engine import AsyncEngine


class YandexSERPService(BaseSERPService):
    """Yandex Search Engine Results Page service."""

    SEARCH_ENGINE = "yandex"

    def __init__(
        self,
        engine: AsyncEngine,
        timeout: Optional[int] = None,
        max_retries: int = 3,
    ):
        """Initialize Yandex SERP service."""
        url_builder = YandexURLBuilder()
        data_normalizer = YandexDataNormalizer()
        super().__init__(
            engine=engine,
            url_builder=url_builder,
            data_normalizer=data_normalizer,
            timeout=timeout,
            max_retries=max_retries,
        )
