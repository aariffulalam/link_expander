from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    BrowserContext,
    Page,
)  # Import Page
from logging_config import logger  # Local import


class PwScrapper:
    def __init__(self) -> None:
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None  # Update type hint to include Page

    async def initialize(self) -> None:
        # Start Playwright explicitly
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(
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
        self.page = await self.context.new_page()  # Create a reusable page

    async def expand_short_url(self, url: str) -> tuple[bool, str]:
        try:
            print('expand_short_url')
            # Ensure browser, context, and page are initialized
            if not self.browser or not self.context or not self.page:
                print('expand_short_url 111111111111')
                logger.warning("Browser, context, or page not initialized. Reinitializing...")
                await self.initialize()
                print('expand_short_url 111111111111 end')
                if (
                    not self.browser or not self.context or not self.page
                ):  # Double-check after initialization
                    print('expand_short_url 222222222222')
                    raise RuntimeError("Failed to initialize browser, context, or page.")

            print('expand_short_url 333333333333')
            try:
                print('expand_short_url 555555555555')
                await self.page.goto(url)
                print('expand_short_url 666666666666')
                expanded_url = self.page.url
                print('expand_short_url 777777777777')
                print('expand url last', expanded_url)
                logger.info("URL expanded using Playwright: %s -> %s", url, expanded_url)
                return True, expanded_url
            except Exception as e:
                logger.exception("Error expanding URL with Playwright: %s", e)
                return False, f"Error expanding URL: {e}"
        except Exception as e:
            logger.exception("Error expanding URL with Playwright: %s", e)
            return False, f"Error expanding URL: {e}"

    async def close(self) -> None:
        # Close the browser and Playwright explicitly
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def expand_url_sync(self, url: str) -> tuple[bool, str]:
        logger.info("Starting synchronous URL expansion")
        if not self.browser or not self.context:
            print('await self.initialize() 111111111111')
            await self.initialize()
            print('await self.initialize() 111111111111 end')

        return await self.expand_short_url(url)
