"""Minimal output formatter."""

import json
from typing import Any
from .base import BaseFormatter


class MinimalFormatter(BaseFormatter):
    """
    Format results in minimal format (just the data).

    Provides clean data output without metadata,
    ideal for piping to other commands or data processing.
    """

    def format(self, result: Any) -> str:
        """Format result in minimal format (data only)."""
        if hasattr(result, "data"):
            return json.dumps(result.data, indent=2, default=str)
        return json.dumps(result, indent=2, default=str)

    def get_extension(self) -> str:
        """Get file extension."""
        return ".json"
