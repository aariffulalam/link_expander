import asyncio
import requests
from playwright.async_api import async_playwright  # Third-party import
from logging_config import logger  # Local import


class pw_scrapper:
    async def expand_short_url(self, url: str) -> str:  # Adjust method signature
        async with async_playwright() as p:
            browser = await p.firefox.launch(
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
            context = await browser.new_context(
                viewport={
                    "width": 1280,
                    "height": 800,
                },  # Set viewport size to typical screen size
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                locale="en-US",
                geolocation={
                    "latitude": 23.0225,
                    "longitude": 72.5714,
                },  # Ahmedabad geolocation
                permissions=["geolocation"],
            )

            page = await context.new_page()
            logger.info("Browser context and page created")
            await page.goto(url)
            expanded_url = page.url
            logger.info("URL expanded using Playwright: %s -> %s", url, expanded_url)
            await browser.close()
            logger.info("Browser closed")
            return expanded_url

    async def expand_using_requests(self, urls: list[str]) -> dict[str, str]:
        expanded_urls = []
        for url in urls:
            try:
                expanded_url = None
                response = requests.get(
                    url, allow_redirects=True, timeout=10
                )  # Add timeout
                if response.history:
                    expanded_url = response.url
                expanded_urls.append(expanded_url)
                logger.info("URL expanded using requests: %s -> %s", url, expanded_url)
            except (
                requests.exceptions.RequestException
            ) as e:  # Narrow exception handling
                logger.exception("Error expanding URL using requests: %s -> %s", url, e)
                expanded_urls.append(None)

        utl_to_html = dict(zip(urls, expanded_urls))
        return {
            k: v for k, v in utl_to_html.items() if v is not None
        }  # Filter None values

    async def expand_urls(self, urls: list[str]) -> dict[str, str]:
        # Fix argument mismatch
        logger.info("Starting URL expansion using requests")
        expanded_urls = await self.expand_using_requests(urls)
        remaining_urls = [url for url in urls if url not in expanded_urls]
        logger.info("%d URLs remaining for Playwright expansion", len(remaining_urls))
        tasks = [self.expand_short_url(url) for url in remaining_urls]
        remaining_expanded_urls = await asyncio.gather(*tasks)
        logger.info("Tasks gathered and executed")
        expanded_urls.update(dict(zip(remaining_urls, remaining_expanded_urls)))
        logger.info("URL expansion completed")
        return expanded_urls  # Ensure return type matches dict[str, str]

    def expand_urls_sync(self, urls: list[str]) -> dict[str, str]:
        logger.info("Starting synchronous URL expansion")
        return asyncio.run(self.expand_urls(urls))