"""
Read the API key stored by the Bright Data CLI (`brightdata login`).

The CLI persists credentials to a well-known per-platform location:

- Linux:   ~/.config/brightdata-cli/credentials.json
- macOS:   ~/Library/Application Support/brightdata-cli/credentials.json
- Windows: %APPDATA%\\brightdata-cli\\credentials.json

File format (all login flows): {"api_key": "KEY"}

The SDK treats this store as strictly read-only: it never writes into the
brightdata-cli directory and never reads the config.json that lives beside
credentials.json.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional


def _cli_credentials_path() -> Path:
    """Return the platform-specific path of the CLI's credentials.json."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:  # linux and others
        base = Path.home() / ".config"
    return base / "brightdata-cli" / "credentials.json"


def read_cli_credentials() -> Optional[str]:
    """
    Return the API key stored by `brightdata login`, or None if unavailable.

    Any failure — missing file, malformed JSON, wrong value type, empty key,
    no read permission — means "not available" and returns None. This function
    never raises and never writes.
    """
    try:
        key = json.loads(_cli_credentials_path().read_text()).get("api_key")
        return key.strip() if isinstance(key, str) and key.strip() else None
    except Exception:
        return None  # missing file, bad JSON, no permission — all mean "not available"
