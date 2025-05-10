from urllib.parse import urlparse, parse_qs
import requests
from logging_config import logger  # Import the logger


class LinkExpander:
    # def __init__(self):
    #     pass

    def expand_url(self, url: str) -> tuple[bool, str]:

        try:
            expanded_url = url
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url
            response = requests.get(url, allow_redirects=True, timeout=30)
            if response.status_code == 200:
                # Check if the URL is a redirect
                if response.history:
                    # Get the final URL after all redirects
                    expanded_url = response.url
            else:
                return False, f"Error: {response.status_code}"
            return True, expanded_url
        except Exception as e:
            logger.exception("Error expanding URL: %s", e)
            return False, f"Error expanding URL: {e}"

    def handle_url(self, url: str) -> tuple[bool, str]:

        try:
            expanded_url = url
            if not (
                "www.flipkart.com" in url
                or "www.myntra.com" in url
                or "www.amazon.in" in url
                or "www.meesho.com" in url
                or "lehlah.club" in url
            ):
                success, url_or_error = self.expand_url(url)
                if not success:
                    return success, url_or_error
                expanded_url = url_or_error

            # Handle specific URL patterns
            if "linkredirect.in" in expanded_url:
                try:
                    parsed_url = urlparse(expanded_url)
                    expanded_url = parse_qs(parsed_url.query).get("dl", [expanded_url])[0]
                    if expanded_url != "":
                        return True, expanded_url
                    return False, "Error: No 'dl' parameter found in URL"
                except Exception as error:
                    logger.exception("Error handling 'linkredirect.in' URL: %s", error)
                    return False, f"Error handling 'linkredirect.in' URL: {error}"

            if "hypd.store" in expanded_url:
                try:
                    return self.expand_hypd_url(expanded_url)
                except Exception as error:
                    logger.exception("Error handling 'hypd.store' URL: %s", error)
                    return False, f"Error handling 'hypd.store' URL: {error}"

            return True, expanded_url
        except Exception as e:
            logger.exception("Exception in handle_url: %s", e)
            return False, f"Exception in handle_url: {e}"

    def expand_hypd_url(self, url: str) -> tuple[bool, str]:
        expanded_url = url
        if "https://hypd.store/ssdeals/afflink/" in expanded_url:
            uid = expanded_url.split("/")[-1]
            api_url = f"https://catalog2.hypd.store/api/app/influencer/deeplink/{uid}"
            try:
                response = requests.get(api_url, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        payload = data.get("payload")
                        expanded_url = payload
                        return True, expanded_url
                    return False, "Error: Failed to expand Hypd URL"
                return False, f"Error: Hypd -- {response.status_code}"

            except Exception as e:
                logger.exception("Error expanding Hypd URL: %s", e)
                return False, f"Error expanding Hypd URL: {e}"
        return True, expanded_url
