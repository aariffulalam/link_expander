import re
from urllib.parse import urlparse, parse_qs
import requests

async def expand_url(url: str) -> str:
    try:
        # Validate and fix the URL if necessary
        parsed_url = urlparse(url)
        if not parsed_url.scheme:  # Check if the URL is missing a scheme (http/https)
            url = "https://" + url  # Default to https:// if no scheme is provided

        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.url
    except Exception as e:
        print(f"Error expanding URL: {e}")
        return f"expand_url func Error: {e}"

async def expand_hypdr_url(url: str) -> str:
    if "https://hypd.store/ssdeals/afflink/" in url:
        uid = url.split("/")[-1]
        api_url = f"https://catalog2.hypd.store/api/app/influencer/deeplink/{uid}"
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"): 
                    payload = data.get("payload")
                    return await expand_url(payload)
        except Exception as e:
            print(f"Error expanding Hypd URL: {e}")
    return url

async def handle_url(request_body: dict) -> dict:

    print(f"handle_url function Received URL: {url}")
    try:
        # Extract the 'url' field from the request body
        url = request_body.get("url", "")

        expanded_url = url

        # Check if the URL is not from specific domains
        if not (
            "www.flipkart.com" in url or
            "www.myntra.com" in url or
            "www.amazon.in" in url or
            "www.meesho.com" in url or
            "lehlah.club" in url
        ):
            expanded_url = await expand_url(url)

        # Handle "linkredirect.in" URLs
        if "linkredirect.in" in expanded_url:
            try:
                parsed_url = urlparse(expanded_url)
                expanded_url = parse_qs(parsed_url.query).get("dl", [expanded_url])[0]
            except Exception as error:
                print(f"Error handling 'linkredirect.in' URL {expanded_url}: {error}")

        # Handle "hypd.store" URLs
        if "hypd.store" in expanded_url:
            try:
                expanded_url = await expand_hypdr_url(expanded_url)
            except Exception as error:
                print(f"Error handling 'hypd.store' URL {expanded_url}: {error}")

        print(f"Original URL: {url}")
        print(f"Expanded URL: {expanded_url}")
        return {"originalUrl": url, "expandedUrl": expanded_url}

    except Exception as e:
        print(f"Error in handle_url function: {e}")
        return {"error": "An error occurred while processing the URL"}