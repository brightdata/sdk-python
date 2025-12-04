"""Base formatter interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseFormatter(ABC):
    """
    Base formatter interface using Strategy Pattern.

    All formatters must implement this interface to ensure
    consistent behavior across different output formats.
    """

    @abstractmethod
    def format(self, result: Any) -> str:
        """
        Format result to string representation.

        Args:
            result: Result object (ScrapeResult, SearchResult, etc.)

        Returns:
            Formatted string representation
        """
        pass

    @abstractmethod
    def get_extension(self) -> str:
        """
        Get file extension for this format.

        Returns:
            File extension including dot (e.g., ".json", ".md")
        """
        pass
