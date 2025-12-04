"""JSON output formatter."""

import json
from typing import Any
from dataclasses import asdict, is_dataclass
from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """
    Format results as JSON.

    Provides clean, structured JSON output suitable for:
    - API consumption
    - Data processing
    - Automation
    """

    def format(self, result: Any) -> str:
        """Format result as JSON string."""
        if hasattr(result, "to_dict"):
            data = result.to_dict()
        elif hasattr(result, "__dict__"):
            if is_dataclass(result):
                data = asdict(result)
            else:
                data = result.__dict__
        else:
            data = result

        return json.dumps(data, indent=2, default=str)

    def get_extension(self) -> str:
        """Get file extension."""
        return ".json"
