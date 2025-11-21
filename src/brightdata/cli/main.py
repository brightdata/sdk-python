"""
Main CLI entry point for Bright Data SDK.

Provides a unified command-line interface for all search and scrape operations.
"""

import click
import sys

from .commands import scrape_group, search_group


@click.group()
@click.version_option(version="2.0.0", prog_name="brightdata")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Bright Data CLI - Command-line interface for Bright Data SDK.
    
    Provides easy access to all search and scrape tools.
    
    All commands require an API key. You can provide it via:
    - --api-key flag
    - BRIGHTDATA_API_TOKEN environment variable
    - Interactive prompt (if neither is provided)
    """
    ctx.ensure_object(dict)
    # Store context for subcommands
    ctx.obj["api_key"] = None


# Register command groups
cli.add_command(scrape_group)
cli.add_command(search_group)


def main() -> None:
    """Entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\nOperation cancelled by user.", err=True)
        sys.exit(130)
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()

