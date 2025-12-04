"""Output formatters for results."""

from .registry import FormatterRegistry
from .base import BaseFormatter
from .json_formatter import JSONFormatter
from .pretty_formatter import PrettyFormatter
from .minimal_formatter import MinimalFormatter
from .markdown import MarkdownFormatter

# Auto-register formatters
FormatterRegistry.register("json", JSONFormatter)
FormatterRegistry.register("pretty", PrettyFormatter)
FormatterRegistry.register("minimal", MinimalFormatter)
FormatterRegistry.register("markdown", MarkdownFormatter)
FormatterRegistry.register("md", MarkdownFormatter)  # Alias

__all__ = [
    "FormatterRegistry",
    "BaseFormatter",
    "JSONFormatter",
    "PrettyFormatter",
    "MinimalFormatter",
    "MarkdownFormatter",
]
