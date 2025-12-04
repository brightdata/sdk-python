"""Formatter registry for managing output formatters."""

from typing import Dict, Type, List
from .base import BaseFormatter


class FormatterRegistry:
    """
    Registry for output formatters using Registry Pattern.

    Provides centralized formatter management and makes it easy
    to add new output formats without modifying existing code.

    Example:
        >>> FormatterRegistry.register("csv", CSVFormatter)
        >>> formatter = FormatterRegistry.get_formatter("csv")
        >>> output = formatter.format(result)
    """

    _formatters: Dict[str, Type[BaseFormatter]] = {}

    @classmethod
    def register(cls, name: str, formatter: Type[BaseFormatter]) -> None:
        """
        Register a formatter.

        Args:
            name: Format name (e.g., "json", "markdown")
            formatter: Formatter class implementing BaseFormatter
        """
        cls._formatters[name.lower()] = formatter

    @classmethod
    def get_formatter(cls, name: str) -> BaseFormatter:
        """
        Get formatter instance by name.

        Args:
            name: Format name (case-insensitive)

        Returns:
            Formatter instance

        Raises:
            ValueError: If format name not registered
        """
        name_lower = name.lower()
        if name_lower not in cls._formatters:
            available = ", ".join(cls.list_formats())
            raise ValueError(f"Unknown format: '{name}'. Available formats: {available}")
        return cls._formatters[name_lower]()

    @classmethod
    def list_formats(cls) -> List[str]:
        """
        List all registered format names.

        Returns:
            List of format names
        """
        return sorted(list(cls._formatters.keys()))

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a format is registered.

        Args:
            name: Format name to check

        Returns:
            True if registered, False otherwise
        """
        return name.lower() in cls._formatters
