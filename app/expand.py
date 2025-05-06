from urllib.parse import urlparse, parse_qs
import requests
from logging_config import logger  # Import the logger

class LinkExpander:
    def __init__(self):
        pass

    async def expand_url(self, url: str) -> str:
        toReturn = {
            "expanded": True,
            "url": url,
            "expanded_url": url,
            "error_message": '',
        }
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url
            response = requests.get(url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                # Check if the URL is a redirect
                if response.history:
                    # Get the final URL after all redirects
                    expanded_url = response.url
                    toReturn["expanded_url"] = expanded_url
                else:
                    toReturn["expanded_url"] = url
            else:
                toReturn["expanded"] = False
                toReturn["error_message"] = f"Error: {response.status_code}"
            return toReturn
        except Exception as e:
            toReturn["expanded"] = False
            toReturn["error_message"] = f"Error expanding URL: {e}"
            logger.exception(f"Error expanding URL: {e}")
            return toReturn

    async def handle_url(self, request_body: dict) -> dict:
        url = request_body.get("url", "")
        toReturn = {
            "expanded": True,
            "url": url,
            "expanded_url": url,
            "error_message": '',
        }
        try:
            if not (
                "www.flipkart.com" in url
                or "www.myntra.com" in url
                or "www.amazon.in" in url
                or "www.meesho.com" in url
                or "lehlah.club" in url
            ):
                expanded_url_data = await self.expand_url(url)
                if expanded_url_data is None:
                    toReturn["expanded"] = False
                    toReturn["error_message"] = "Error in expand_url"
                    return toReturn
                elif expanded_url_data["expanded"] is False:
                    toReturn["expanded"] = False
                    toReturn["error_message"] = expanded_url_data["error_message"]
                else:
                    toReturn["expanded_url"] = expanded_url_data["expanded_url"]

            # Handle specific URL patterns
            if "linkredirect.in" in toReturn["expanded_url"]:
                try:
                    parsed_url = urlparse(toReturn["expanded_url"])
                    toReturn["expanded_url"] = parse_qs(parsed_url.query).get(
                        "dl", [toReturn["expanded_url"]]
                    )[0]
                    if toReturn["expanded_url"] != "":
                        toReturn["expanded_url"] = toReturn["expanded_url"]
                except Exception as error:
                    toReturn["expanded"] = False
                    toReturn["error_message"] = str(error)
                    logger.exception(f"Error handling 'linkredirect.in' URL: {error}")

            if "hypd.store" in toReturn["expanded_url"]:
                try:
                    expand_hypdr_url_data = await self.expand_hypdr_url(
                        toReturn["expanded_url"]
                    )
                    if expand_hypdr_url_data is None:
                        toReturn["expanded"] = False
                        toReturn["error_message"] = "Error in expand_hypdr_url"
                        return toReturn
                    elif expand_hypdr_url_data["expanded"] is False:
                        toReturn["expanded"] = False
                        toReturn["error_message"] = expand_hypdr_url_data["error_message"]
                    else:
                        toReturn["expanded_url"] = expand_hypdr_url_data["expanded_url"]
                except Exception as error:
                    logger.exception(f"Error handling 'hypd.store' URL: {error}")

            return toReturn
        except Exception as e:
            logger.exception(f"Exception in handle_url: {e}")
            return {"error": f"An error occurred: {e}"}

    async def expand_hypdr_url(self, url: str) -> str:
        toReturn = {
            "expanded": True,
            "url": url,
            "expanded_url": url,
            "error_message": '',
        }
        if "https://hypd.store/ssdeals/afflink/" in url:
            uid = url.split("/")[-1]
            api_url = f"https://catalog2.hypd.store/api/app/influencer/deeplink/{uid}"
            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        payload = data.get("payload")
                        toReturn["expanded_url"] = payload
                        # expanded_url_data = await self.expand_url(payload)
                        # if expanded_url_data is None:
                        #     toReturn["expanded"] = False
                        #     toReturn["error_message"] = "Error in expand_url"
                        #     return toReturn
                        # elif expanded_url_data["expanded"] is False:
                        #     toReturn["expanded"] = False
                        #     toReturn["error_message"] = expanded_url_data.error_message
                        # else:
                        #     toReturn["expanded_url"] = expanded_url_data.expanded_url
            except Exception as e:
                logger.exception(f"Error expanding Hypd URL: {e}")
                toReturn["expanded"] = False
                toReturn["error_message"] = f"Error expanding Hypd URL: {e}"
        return toReturn