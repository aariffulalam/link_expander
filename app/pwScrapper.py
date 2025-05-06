import asyncio
from playwright.async_api import async_playwright
import json
import requests
from logging_config import logger  # Import the logger


class PWScrapper:

    async def expandShortUrl(self, urls):
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

            context = await browser.new_context()
            logger.info("Browser context created")
            pages = [await context.new_page() for _ in urls]
            logger.info(f"{len(pages)} pages created for URLs")
            tasks = [self.expand_short_url(page, url) for page, url in zip(pages, urls)]
            logger.info("Tasks created for URL expansion")
            expanded_urls = await asyncio.gather(*tasks)
            logger.info("Tasks gathered and executed")
            await browser.close()
            logger.info("Browser closed")
            utl_to_html = dict(zip(urls, expanded_urls))
            return utl_to_html

    async def expand_using_requests(self, urls):
        expanded_urls = []
        for url in urls:
            try:
                expanded_url = None
                response = requests.get(url, allow_redirects=True)
                if response.history:
                    expanded_url = response.url
                expanded_urls.append(expanded_url)
                logger.info(f"URL expanded using requests: {url} -> {expanded_url}")
            except Exception as e:
                logger.exception(f"Error expanding URL using requests: {url} -> {e}")
                expanded_urls.append(None)

        utl_to_html = dict(zip(urls, expanded_urls))
        return utl_to_html

    async def expand_urls(self, urls):
        # First try to expand using requests and then remaining using playwright
        logger.info("Starting URL expansion using requests")
        expanded_urls = await self.expand_using_requests(urls)
        remaining_urls = [
            url for url, expanded_url in expanded_urls.items() if expanded_url is None
        ]
        logger.info(f"{len(remaining_urls)} URLs remaining for Playwright expansion")
        remaining_expanded_urls = await self.expandShortUrl(remaining_urls)
        expanded_urls.update(remaining_expanded_urls)
        logger.info("URL expansion completed")
        return expanded_urls

    def expand_urls_sync(self, urls):
        logger.info("Starting synchronous URL expansion")
        return asyncio.run(self.expand_urls(urls))