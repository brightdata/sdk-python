"""
SSL certificate error handling utilities.

Provides helpful error messages and guidance for SSL certificate issues,
particularly common on macOS systems.
"""

import sys
import ssl

try:
    import aiohttp
except ImportError:
    aiohttp = None


def is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def is_ssl_certificate_error(error: Exception) -> bool:
    """
    Check if an exception is an SSL certificate verification error.

    Args:
        error: Exception to check

    Returns:
        True if this is an SSL certificate error
    """
    # Check for SSL errors directly
    if isinstance(error, ssl.SSLError):
        return True

    # Check for aiohttp SSL-related errors
    # aiohttp.ClientConnectorError wraps SSL errors
    # aiohttp.ClientSSLError is the specific SSL error class
    if aiohttp is not None:
        if isinstance(error, (aiohttp.ClientConnectorError, aiohttp.ClientSSLError)):
            return True

    # Check error message for SSL-related keywords
    try:
        error_str = str(error)
        if error_str is None:
            error_str = ""
        error_str = error_str.lower()
    except (TypeError, AttributeError):
        # If __str__ returns None or raises an error, treat as non-SSL error
        return False
    ssl_keywords = [
        "certificate verify failed",
        "certificate verify",
        "unable to get local issuer certificate",
        "ssl: certificate",
        "ssl certificate",
        "certificate",
        "[ssl:",
    ]

    # Check if any SSL keyword is in the error message
    if any(keyword in error_str for keyword in ssl_keywords):
        return True

    # Check for OSError with SSL-related errno
    if isinstance(error, OSError):
        # SSL errors often manifest as OSError with specific messages
        if "certificate" in error_str or "ssl" in error_str:
            return True

    return False


def get_ssl_error_message(error: Exception) -> str:
    """
    Get a helpful error message for SSL certificate errors.

    Provides platform-specific guidance, especially for macOS users.

    Args:
        error: The SSL error that occurred

    Returns:
        Helpful error message with fix instructions
    """
    base_message = (
        "SSL certificate verification failed. This is a common issue, "
        "especially on macOS systems where Python doesn't have access "
        "to system certificates."
    )

    if is_macos():
        fix_instructions = """
        
To fix this on macOS, try one of the following:

1. Install/upgrade certifi:
   pip install --upgrade certifi

2. Install certificates via Homebrew (if using Homebrew Python):
   brew install ca-certificates

3. Run the Install Certificates.command script (for python.org installers):
   /Applications/Python 3.x/Install Certificates.command

4. Set SSL_CERT_FILE environment variable:
   export SSL_CERT_FILE=$(python -m certifi)

For more details, see:
https://github.com/brightdata/brightdata-python-sdk/blob/main/docs/troubleshooting.md#ssl-certificate-errors
"""
    else:
        fix_instructions = """
        
To fix this, try:

1. Install/upgrade certifi:
   pip install --upgrade certifi

2. Set SSL_CERT_FILE environment variable:
   export SSL_CERT_FILE=$(python -m certifi)

For more details, see:
https://github.com/brightdata/brightdata-python-sdk/blob/main/docs/troubleshooting.md#ssl-certificate-errors
"""

    return base_message + fix_instructions + f"\n\nOriginal error: {str(error)}"
