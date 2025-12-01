"""
ANSI art banner for Bright Data Python SDK CLI.
"""

import sys
import os


def _supports_color() -> bool:
    """Check if terminal supports ANSI colors."""
    # Check if we're in a terminal
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False

    # Windows 10+ supports ANSI colors
    if sys.platform == "win32":
        # Check if Windows version supports ANSI
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            # Enable ANSI escape sequences on Windows
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False

    # Check for common environment variables
    if os.getenv("TERM") in ("xterm", "xterm-256color", "screen", "screen-256color"):
        return True

    return False


def get_banner() -> str:
    """
    Get ANSI art banner for Bright Data Python SDK.

    Returns:
        Formatted banner string with colors
    """
    banner = """
    
    \033[1;33m██████╗ ██████╗ ██╗ ██████╗ ██╗  ██╗████████╗\033[0m
    \033[1;33m██╔══██╗██╔══██╗██║██╔════╝ ██║  ██║╚══██╔══╝\033[0m
    \033[1;33m██████╔╝██████╔╝██║██║  ███╗███████║   ██║   \033[0m
    \033[1;33m██╔══██╗██╔══██╗██║██║   ██║██╔══██║   ██║   \033[0m
    \033[1;33m██████╔╝██║  ██║██║╚██████╔╝██║  ██║   ██║   \033[0m
    \033[1;33m╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   \033[0m
    
    \033[1;35m██████╗  █████╗ ████████╗ █████╗ \033[0m
    \033[1;35m██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗\033[0m
    \033[1;35m██║  ██║███████║   ██║   ███████║\033[0m
    \033[1;35m██║  ██║██╔══██║   ██║   ██╔══██║\033[0m
    \033[1;35m██████╔╝██║  ██║   ██║   ██║  ██║\033[0m
    \033[1;35m╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝\033[0m
    
    \033[1;32m██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗\033[0m
    \033[1;32m██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║\033[0m
    \033[1;32m██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║\033[0m
    \033[1;32m██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║\033[0m
    \033[1;32m██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║\033[0m
    \033[1;32m╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝\033[0m
    
    \033[1;37m███████╗██████╗ ██╗  ██╗\033[0m
    \033[1;37m██╔════╝██╔══██╗██║ ██╔╝\033[0m
    \033[1;37m███████╗██║  ██║█████╔╝ \033[0m
    \033[1;37m╚════██║██║  ██║██╔═██╗ \033[0m
    \033[1;37m███████║██████╔╝██║  ██╗\033[0m
    \033[1;37m╚══════╝╚═════╝ ╚═╝  ╚═╝\033[0m
    
    \033[1;93m🐍\033[0m
    
    """
    return banner


def print_banner() -> None:
    """Print the banner to stdout with proper encoding and color support."""
    # Enable color support on Windows
    supports_color = _supports_color()

    banner = get_banner()

    # If no color support, strip ANSI codes
    if not supports_color:
        import re

        # Remove ANSI escape sequences
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        banner = ansi_escape.sub("", banner)

    # Ensure UTF-8 encoding for Windows compatibility
    try:
        if hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
            sys.stdout.buffer.write(banner.encode("utf-8"))
            sys.stdout.buffer.write(b"\n")
        else:
            print(banner)
    except (AttributeError, UnicodeEncodeError):
        # Fallback: print without special characters
        print(banner.encode("ascii", "ignore").decode("ascii"))
