"""Browser API service — builds CDP WebSocket URLs for Playwright/Puppeteer."""

from typing import Optional


class BrowserService:
    """
    Builds CDP WebSocket connection URLs for Bright Data's Browser API.

    Browser API provides cloud-hosted Chrome instances connected via the
    Chrome DevTools Protocol (CDP). The SDK builds the connection URL;
    you connect with Playwright, Puppeteer, or Selenium yourself.

    Example:
        >>> client = BrightDataClient(
        ...     browser_username="brd-customer-hl_1cdf8003-zone-scraping_browser1",
        ...     browser_password="f05i50grymt3",
        ... )
        >>> url = client.browser.get_connect_url()
        >>>
        >>> # Connect with Playwright:
        >>> from playwright.async_api import async_playwright
        >>> async with async_playwright() as pw:
        ...     browser = await pw.chromium.connect_over_cdp(url)
        ...     page = await browser.new_page()
        ...     await page.goto("https://example.com")
        ...     html = await page.content()
        ...     await browser.close()
    """

    DEFAULT_HOST = "brd.superproxy.io"
    DEFAULT_PORT = 9222

    def __init__(
        self,
        username: str,
        password: str,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
    ):
        self._username = username
        self._password = password
        self._host = host
        self._port = port

    def get_connect_url(self, country: Optional[str] = None) -> str:
        """
        Return the CDP WebSocket URL for connecting to a remote browser.

        Args:
            country: Optional 2-letter country code for geo-targeting
                     (e.g., "us", "gb", "de"). Appended to the username
                     as ``-country-{code}`` per Bright Data's format.

        Returns:
            WebSocket URL like
            ``wss://brd-customer-abc-zone-mybrowser:pass@brd.superproxy.io:9222``
        """
        username = self._username
        if country:
            username = f"{username}-country-{country}"
        return f"wss://{username}:{self._password}@{self._host}:{self._port}"
