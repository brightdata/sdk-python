"""Markdown output formatter."""

import json
from typing import Any, Dict, List
from .base import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """
    Format results as GitHub-flavored Markdown.

    Features:
    - Tables for structured data
    - Code blocks for complex data
    - Status badges (✅/❌)
    - Metadata section with timing/cost
    - Smart column limiting for readability
    """

    def format(self, result: Any) -> str:
        """
        Format result as markdown.

        Args:
            result: Result object to format

        Returns:
            GitHub-flavored markdown string
        """
        lines = []

        # Header with status badge
        if hasattr(result, "success"):
            status_badge = "✅ Success" if result.success else "❌ Failed"
            lines.append(f"# Result: {status_badge}")
            lines.append("")
        else:
            lines.append("# Result")
            lines.append("")

        # Metadata table
        metadata_lines = self._format_metadata(result)
        if metadata_lines:
            lines.extend(metadata_lines)
            lines.append("")

        # Data section
        if hasattr(result, "data") and result.data is not None:
            lines.append("## Data")
            lines.append("")

            if isinstance(result.data, list):
                lines.append(self._format_list_as_table(result.data))
            elif isinstance(result.data, dict):
                lines.append(self._format_dict_as_table(result.data))
            elif isinstance(result.data, str):
                lines.append("```")
                lines.append(result.data[:1000])  # Limit to 1000 chars
                if len(result.data) > 1000:
                    lines.append(f"... ({len(result.data) - 1000} more characters)")
                lines.append("```")
            else:
                lines.append(f"```json\n{json.dumps(result.data, indent=2)}\n```")

            lines.append("")

        # Error section
        if hasattr(result, "error") and result.error:
            lines.append("## Error")
            lines.append("")
            lines.append(f"> ⚠️ {result.error}")
            lines.append("")

        return "\n".join(lines)

    def _format_metadata(self, result: Any) -> List[str]:
        """Format metadata as markdown table."""
        lines = []
        metadata = []

        # Collect metadata fields
        if hasattr(result, "platform") and result.platform:
            metadata.append(("Platform", f"`{result.platform}`"))

        if hasattr(result, "method") and result.method:
            metadata.append(("Method", f"`{result.method}`"))

        if hasattr(result, "cost") and result.cost is not None:
            metadata.append(("Cost", f"${result.cost:.4f} USD"))

        if hasattr(result, "elapsed_ms"):
            try:
                elapsed = result.elapsed_ms()
                metadata.append(("Time", f"{elapsed:.2f}ms"))
            except Exception:
                pass

        if hasattr(result, "snapshot_id") and result.snapshot_id:
            metadata.append(("Snapshot ID", f"`{result.snapshot_id}`"))

        if hasattr(result, "url") and result.url:
            url_display = result.url[:60] + "..." if len(result.url) > 60 else result.url
            metadata.append(("URL", url_display))

        # Build table if we have metadata
        if metadata:
            lines.append("## Metadata")
            lines.append("")
            lines.append("| Field | Value |")
            lines.append("|-------|-------|")
            for key, value in metadata:
                lines.append(f"| {key} | {value} |")

        return lines

    def _format_list_as_table(self, data: List) -> str:
        """Format list as markdown table."""
        if not data:
            return "_No data_"

        # Handle list of dicts (most common case)
        if isinstance(data[0], dict):
            return self._format_list_of_dicts_as_table(data)

        # Handle simple list
        lines = []
        lines.append("| Index | Value |")
        lines.append("|-------|-------|")

        for i, item in enumerate(data[:20]):  # Limit to 20 items
            value = str(item)[:100]  # Limit value length
            lines.append(f"| {i} | {value} |")

        if len(data) > 20:
            lines.append("")
            lines.append(f"_... and {len(data) - 20} more items_")

        return "\n".join(lines)

    def _format_list_of_dicts_as_table(self, data: List[Dict]) -> str:
        """Format list of dictionaries as markdown table."""
        if not data:
            return "_No data_"

        # Get all unique keys from first 10 items
        keys = set()
        for item in data[:10]:
            if isinstance(item, dict):
                keys.update(item.keys())

        # Select most important columns (limit to 5 for readability)
        priority_keys = ["name", "title", "url", "price", "final_price", "rating"]
        selected_keys = []

        # Add priority keys first
        for key in priority_keys:
            if key in keys:
                selected_keys.append(key)
                if len(selected_keys) >= 5:
                    break

        # Fill remaining slots with other keys
        if len(selected_keys) < 5:
            for key in sorted(keys):
                if key not in selected_keys:
                    selected_keys.append(key)
                    if len(selected_keys) >= 5:
                        break

        if not selected_keys:
            # Fallback to JSON if no keys
            return f"```json\n{json.dumps(data[:10], indent=2)}\n```"

        # Build table
        lines = []
        lines.append("| " + " | ".join(selected_keys) + " |")
        lines.append("| " + " | ".join(["---"] * len(selected_keys)) + " |")

        for item in data[:10]:  # Limit to 10 rows for readability
            if isinstance(item, dict):
                values = []
                for key in selected_keys:
                    value = item.get(key, "")
                    # Truncate long values
                    value_str = str(value)[:50]
                    if len(str(value)) > 50:
                        value_str += "..."
                    values.append(value_str)
                lines.append("| " + " | ".join(values) + " |")

        if len(data) > 10:
            lines.append("")
            lines.append(f"_... and {len(data) - 10} more items_")

        return "\n".join(lines)

    def _format_dict_as_table(self, data: Dict) -> str:
        """Format dictionary as markdown table."""
        if not data:
            return "_No data_"

        lines = []
        lines.append("| Key | Value |")
        lines.append("|-----|-------|")

        # Show top 20 fields
        for key, value in list(data.items())[:20]:
            # Truncate long values
            value_str = str(value)[:100]
            if len(str(value)) > 100:
                value_str += "..."

            # Escape pipes in values
            value_str = value_str.replace("|", "\\|")

            lines.append(f"| `{key}` | {value_str} |")

        if len(data) > 20:
            lines.append("")
            lines.append(f"_... and {len(data) - 20} more fields_")

        return "\n".join(lines)

    def get_extension(self) -> str:
        """Get file extension."""
        return ".md"
