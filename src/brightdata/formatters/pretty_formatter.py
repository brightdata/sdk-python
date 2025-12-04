"""Pretty output formatter."""

import json
from typing import Any
from .base import BaseFormatter


class PrettyFormatter(BaseFormatter):
    """
    Format results in human-readable pretty format.

    Provides formatted output with:
    - Success/failure indicators
    - Cost and timing information
    - Readable data display
    """

    def format(self, result: Any) -> str:
        """Format result in pretty, human-readable way."""
        lines = []

        if hasattr(result, "success"):
            status = "✓ Success" if result.success else "✗ Failed"
            lines.append(f"Status: {status}")

            if hasattr(result, "cost") and result.cost:
                lines.append(f"Cost: ${result.cost:.4f} USD")

            if hasattr(result, "elapsed_ms"):
                elapsed = result.elapsed_ms()
                lines.append(f"Elapsed: {elapsed:.2f}ms")

            if hasattr(result, "data") and result.data:
                lines.append("\nData:")
                lines.append(json.dumps(result.data, indent=2))
        else:
            lines.append(json.dumps(result, indent=2))

        return "\n".join(lines)

    def get_extension(self) -> str:
        """Get file extension."""
        return ".txt"
