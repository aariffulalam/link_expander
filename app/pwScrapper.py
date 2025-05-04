import asyncio
from playwright.async_api import async_playwright
import json
import requests


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
            # print("Context create")
            context = await browser.new_context()
            # print("Context created")
            pages = [await context.new_page() for _ in urls]
            # print("Pages created")
            tasks = [self.expand_short_url(page, url) for page, url in zip(pages, urls)]
            # print("Tasks created")
            expanded_urls = await asyncio.gather(*tasks)
            # print("Tasks gathered")
            await browser.close()
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
            except Exception as e:
                print(e)
                expanded_urls.append(None)

        utl_to_html = dict(zip(urls, expanded_urls))

        return utl_to_html

    async def expand_urls(self, urls):
        # first try to expand using requests and then remaining using playwright
        expanded_urls = await self.expand_using_requests(urls)
        remaining_urls = [
            url for url, expanded_url in expanded_urls.items() if expanded_url is None
        ]
        remaining_expanded_urls = await self.expandShortUrl(remaining_urls)
        expanded_urls.update(remaining_expanded_urls)
        return expanded_urls

    def expand_urls_sync(self, urls):
        return asyncio.run(self.expand_urls(urls))
