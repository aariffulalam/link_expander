from urllib.parse import urlparse, parse_qs
import requests


class LinkExpander:
    def __init__(self):
        pass

    async def expand_url(self, url: str) -> str:
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url
            response = requests.get(url, allow_redirects=True, timeout=10)
            return response.url
        except Exception as e:
            return f"Error expanding URL: {e}"

    async def handle_url(self, request_body: dict) -> dict:
        try:
            url = request_body.get("url", "")
            expanded_url = url
            if not (
                "www.flipkart.com" in url
                or "www.myntra.com" in url
                or "www.amazon.in" in url
                or "www.meesho.com" in url
                or "lehlah.club" in url
            ):
                expanded_url = await self.expand_url(url)
            
            # Handle specific URL patterns
            if "linkredirect.in" in expanded_url:
                try:
                    parsed_url = urlparse(expanded_url)
                    expanded_url = parse_qs(parsed_url.query).get("dl", [expanded_url])[0]
                except Exception as error:
                    print(f"Error handling 'linkredirect.in' URL {expanded_url}: {error}")

            if "hypd.store" in expanded_url:
                try:
                    expanded_url = await self.expand_hypdr_url(expanded_url)
                except Exception as error:
                    print(f"Error handling 'hypd.store' URL {expanded_url}: {error}")

            return {"originalUrl": url, "expandedUrl": expanded_url}
        except Exception as e:
            return {"error": f"An error occurred: {e}"}

    async def expand_hypdr_url(self, url: str) -> str:
        # Check if the URL contains the specific Hypd pattern
        if "https://hypd.store/ssdeals/afflink/" in url:
            uid = url.split("/")[-1]
            api_url = f"https://catalog2.hypd.store/api/app/influencer/deeplink/{uid}"
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        payload = data.get("payload")
                        return await self.expand_url(payload)
            except Exception as e:
                print(f"Error expanding Hypd URL: {e}")
        return url