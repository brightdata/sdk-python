"""
CLI utilities for formatting output, handling errors, and managing API keys.
"""

import json
import sys
from typing import Optional, Any
import click

from ..client import BrightDataClient
from ..exceptions import (
    BrightDataError,
    ValidationError,
    AuthenticationError,
    APIError,
)


def get_api_key(api_key: Optional[str] = None) -> str:
    """
    Get API key from parameter, environment variable, or prompt.

    Args:
        api_key: Optional API key from command line

    Returns:
        Valid API key string

    Raises:
        click.Abort: If user cancels the prompt
    """
    # Priority: parameter > environment > prompt
    if api_key:
        return api_key.strip()

    import os

    env_key = os.getenv("BRIGHTDATA_API_TOKEN")
    if env_key:
        return env_key.strip()

    # Prompt user for API key
    api_key = click.prompt("Enter your Bright Data API key", hide_input=True, type=str)

    if not api_key or len(api_key.strip()) < 10:
        raise click.BadParameter(
            "API key must be at least 10 characters long", param_hint="--api-key"
        )

    return api_key.strip()


def create_client(api_key: Optional[str] = None, **kwargs) -> BrightDataClient:
    """
    Create a BrightDataClient instance with API key validation.

    Args:
        api_key: Optional API key (will be prompted if not provided)
        **kwargs: Additional client configuration

    Returns:
        BrightDataClient instance
    """
    key = get_api_key(api_key)
    return BrightDataClient(token=key, **kwargs)


def format_result(result: Any, output_format: str = "json") -> str:
    """
    Format result for output.

    Args:
        result: Result object (ScrapeResult, SearchResult, etc.)
        output_format: Output format ("json", "pretty", "minimal")

    Returns:
        Formatted string
    """
    if output_format == "json":
        if hasattr(result, "to_dict"):
            data = result.to_dict()
        elif hasattr(result, "__dict__"):
            from dataclasses import asdict, is_dataclass

            if is_dataclass(result):
                data = asdict(result)
            else:
                data = result.__dict__
        else:
            data = result
        return json.dumps(data, indent=2, default=str)
    elif output_format == "pretty":
        return format_result_pretty(result)
    elif output_format == "minimal":
        return format_result_minimal(result)
    else:
        return str(result)


def format_result_pretty(result: Any) -> str:
    """Format result in a human-readable way."""
    lines = []

    if hasattr(result, "success"):
        status = "✓ Success" if result.success else "✗ Failed"
        lines.append(f"Status: {status}")

        if hasattr(result, "error") and result.error:
            lines.append(f"Error: {result.error}")

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


def format_result_minimal(result: Any) -> str:
    """Format result in minimal format (just the data)."""
    if hasattr(result, "data"):
        return json.dumps(result.data, indent=2, default=str)
    return json.dumps(result, indent=2, default=str)


def handle_error(error: Exception) -> None:
    """
    Handle and display errors in a user-friendly way.

    Args:
        error: Exception to handle
    """
    if isinstance(error, click.ClickException):
        raise error

    if isinstance(error, ValidationError):
        click.echo(f"Validation Error: {error}", err=True)
    elif isinstance(error, AuthenticationError):
        click.echo(f"Authentication Error: {error}", err=True)
        click.echo("\nPlease check your API key at: https://brightdata.com/cp/api_keys", err=True)
    elif isinstance(error, APIError):
        click.echo(f"API Error: {error}", err=True)
    elif isinstance(error, BrightDataError):
        click.echo(f"Bright Data Error: {error}", err=True)
    else:
        click.echo(f"Unexpected Error: {type(error).__name__}: {error}", err=True)
        if "--debug" in sys.argv:
            import traceback

            traceback.print_exc()


def output_result(
    result: Any, output_format: str = "json", output_file: Optional[str] = None
) -> None:
    """
    Output result to stdout or file.

    Args:
        result: Result to output
        output_format: Output format ("json", "pretty", "minimal")
        output_file: Optional file path to write to
    """
    formatted = format_result(result, output_format)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted)
        click.echo(f"Result saved to: {output_file}")
    else:
        click.echo(formatted)
