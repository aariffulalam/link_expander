import asyncio
from playwright.async_api import async_playwright  # Third-party import
from playwright.async_api import Browser, BrowserContext  # Third-party import
from logging_config import logger  # Local import


class PwScrapper:
    def __init__(self) -> None:
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    async def initialize(self) -> None:
        async with async_playwright() as p:
            self.browser = await p.firefox.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-quic",  # Disable QUIC protocol
                    "--disable-http2",  # Explicitly enable HTTP/2
                    "--disable-blink-features=AutomationControlled",
                    "--enable-features=NetworkService,NetworkServiceInProcess",
                    "--ignore-certificate-errors",  # Ignore certificate errors
                ],
            )
            self.context = await self.browser.new_context(
                viewport={
                    "width": 1280,
                    "height": 800,
                },  # Set viewport size to typical screen size
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                ),
                locale="en-US",
                geolocation={
                    "latitude": 23.0225,
                    "longitude": 72.5714,
                },  # Ahmedabad geolocation
                permissions=["geolocation"],
            )

    async def expand_short_url(self, url: str) -> tuple[bool, str]:
        try:
            if not self.browser or not self.context:
                raise RuntimeError("Browser or context not initialized. Call `initialize` first.")
            page = await self.context.new_page()
            try:
                await page.goto(url)
                expanded_url = page.url
                logger.info("URL expanded using Playwright: %s -> %s", url, expanded_url)
                await page.close()
                return True, expanded_url
            except Exception as e:
                logger.exception("Error expanding URL with Playwright: %s", e)
                await page.close()
                return False, f"Error expanding URL: {e}"
        except Exception as e:
            logger.exception("Error expanding URL with Playwright: %s", e)
            return False, f"Error expanding URL: {e}"

    async def close(self) -> None:
        if self.browser:
            await self.browser.close()

    def expand_url_sync(self, url: str) -> tuple[bool, str]:
        logger.info("Starting synchronous URL expansion")
        if not self.browser or not self.context:
            asyncio.run(self.initialize())
        return asyncio.run(self.expand_short_url(url))
