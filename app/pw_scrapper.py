from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    BrowserContext,
    Page,
)
from logging_config import logger


class PwScrapper:
    def __init__(self) -> None:
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def initialize(self) -> None:
        # Initialize playwright, browser, and context only once.
        if not self.playwright:
            self.playwright = await async_playwright().start()
            # Using chromium instead of firefox
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-quic",
                    "--disable-http2",
                    "--disable-blink-features=AutomationControlled",
                    "--enable-features=NetworkService,NetworkServiceInProcess",
                    "--ignore-certificate-errors",
                ],
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                ),
                locale="en-US",
                geolocation={"latitude": 23.0225, "longitude": 72.5714},
                permissions=["geolocation"],
            )
        if self.context is None:
            raise RuntimeError("Browser context is not initialized.")
        # Instead of always creating a new page, check if one exists already.
        if not self.page:
            if self.context.pages:
                logger.debug("Reusing existing page from context.")
                self.page = self.context.pages[0]
            else:
                logger.debug("Creating a reusable page...")
                self.page = await self.context.new_page()

    async def expand_short_url(self, url: str) -> tuple[bool, str]:
        try:
            if not (self.browser and self.context and self.page):
                logger.warning("Browser, context, or page not initialized. Reinitializing...")
                await self.initialize()
                if not (self.browser and self.context and self.page):
                    raise RuntimeError("Failed to initialize browser, context, or page.")

            await self.page.goto(url)
            expanded_url = self.page.url
            logger.info("URL expanded using Playwright: %s -> %s", url, expanded_url)
            return True, expanded_url
        except Exception as e:
            logger.exception("Error expanding URL with Playwright: %s", e)
            return False, f"Error expanding URL: {e}"

    async def close(self) -> None:
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def expand_url_sync(self, url: str) -> tuple[bool, str]:
        logger.info("Starting synchronous URL expansion")
        if not (self.browser and self.context):
            await self.initialize()
        return await self.expand_short_url(url)
