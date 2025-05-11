from urllib.parse import urlparse
import os
import requests
from fastapi import HTTPException, Request
from app.expand import LinkExpander
from app.pw_scrapper import PwScrapper
from app.sns_service import SnsEmailService  # Updated to use SnsEmailService
from logging_config import logger  # Import the logger
import json
from datetime import datetime, timedelta

# Initialize the LinkExpander class
link_expander = LinkExpander()

# Initialize the PwScrapper class
pwscrapper = PwScrapper()
# Initialize the EmailService class
email_service = SnsEmailService()  # Updated to use SnsEmailService


class URLViews:
    def __init__(self) -> None:
        self.link_expander = link_expander
        self.email_service = email_service  # Updated to use SnsEmailService

    async def expand_post_view(self, request: Request) -> dict[str, str | bool]:
        response, status_code = await self.expand_url_view(request)
        if status_code == 200:
            return response

        raise HTTPException(status_code=status_code, detail=response)

    async def expand_url_view(self, request: Request) -> tuple[dict[str, str | bool], int]:
        body = await request.json()
        url = body.get("url", "")

        # validate the URL
        if not url:
            return {"error": "URL is required"}, 400

        # validate url format
        if not url.startswith(("http://", "https://")):
            return {"error": "Invalid URL format"}, 400

        try:
            print("before link_expander.handle_url")
            success, url_or_error = self.link_expander.handle_url(url)
            print("after link_expander.handle_url")
            print(success, url_or_error)
            print("result >>>>>>>>>>>>> of link_expander.handle_url")
            if not success:
                self.send_failure_notif(url, url_or_error)
                logger.warning("URL expansion failed for %s", url)
                return {"error": url_or_error}, 500  # don't needed to send return here
            expanded_url = url_or_error
            print('before check_flipkart')
            print('expanded_url >>>>>>>>>>>>>', expanded_url)
            know_success, expanded_url = self.check_known_affiliate(expanded_url)
            print('after check_flipkart')
            print('know_success >>>>>>>>>>>>>', know_success)
            print('expanded_url >>>>>>>>>>>>>', expanded_url)
            print('result >>>>>>>>>>>>> of check_flipkart')
            if not know_success:
                self.send_failure_notif(url, expanded_url)
            success, expanded_url = await self.check_flipkart(know_success, expanded_url)
            if not success:
                logger.warning("URL expansion failed for %s", url)
                return {"error": expanded_url}, 500

        except Exception as e:
            logger.exception("Exception in expand_url_view: %s", e)
            return {"error": "Internal server error"}, 500

        return {"expanded_url": expanded_url, "original_url": url}, 200

    def send_failure_notif(self, url: str, error: str) -> None:
        try:
            email_params = {
                "URL": url,
                "Error": error,
            }
            subject = "URL Expansion Failed Notification"

            self.email_service.send_notif(subject=subject, params=email_params)

        except Exception as email_error:
            logger.exception("Error sending email: %s", email_error)

    async def check_flipkart(self, know_success: bool, expanded_url: str) -> tuple[bool, str]:
        """
        Checks for Flipkart-specific patterns and handles
        cases where to_return["expanded"] is False.
        """
        flipkart_patterns = [
            "flipkart.com/s/",
            "fkrt.it",
            "fkrt.cc",
            "fkrt.to",
            "fkrt.co",
        ]
        # Check if the URL matches any Flipkart-specific patterns
        if any(pattern in expanded_url for pattern in flipkart_patterns) or know_success is False:
            logger.info("Flipkart pattern detected in URL: %s", expanded_url)
            return await pwscrapper.expand_url_sync(expanded_url)

        return True, expanded_url

    def check_known_affiliate(self, expanded_url: str) -> tuple[bool, str]:
        print("Checking known affiliate... check_known_affiliate >>>>>>>>>>>>>")
        try:
            # Parse domain from expanded URL
            parsed_url = urlparse(expanded_url)
            domain = parsed_url.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            print("domain >>>>>>>>>>>>>", domain)
            # Fetch known affiliate domains from cache
            domain_data = self.check_and_update_cache()
            print("domain_data >>>>>>>>>>>>>", domain_data)
            known_domains = [d.lower() for d in domain_data]
            known_domains.append('web.lehlah.club')
            known_domain = domain in known_domains
            return known_domain, expanded_url

        except Exception as e:
            logger.exception("Error check known affiliate: %s", e)
            return False, expanded_url

    def check_and_update_cache(self) -> list[str]:
        print("Checking domain cache... check_and_update_cache >>>>>>>>>>>>>")
        cache_dir = "cache"
        cache_file = os.path.join(cache_dir, "domain_cache.json")
        current_time = datetime.now()

        # Ensure the cache directory exists
        os.makedirs(cache_dir, exist_ok=True)

        # Check if the cache file exists
        if os.path.exists(cache_file):
            cache_data = {}
            with open(cache_file, "r", encoding="utf-8") as file:  # Specify encoding
                cache_data = json.load(file)

            # Parse the cached time
            cached_time = datetime.fromisoformat(cache_data.get("create_at", ""))
            time_difference = current_time - cached_time

            # If the time difference is less than 15 minutes, return the cached domains
            if time_difference < timedelta(minutes=15):
                domains = cache_data.get("domains", [])
                return domains if isinstance(domains, list) else []

        # If the file doesn't exist or the time difference is more than 15 minutes, update the cache
        try:
            print("Updating domain cache... api call")
            response = requests.post(
                "https://api-staging.lehlah.club/api/affiliate_domains.json", timeout=10
            )
            print('end response >>>>>>>>')
            print(response, 'response')
            response_data = response.json()
            print(response_data, 'response_data')

            if response_data["statuscode"] == 0:
                domains = response_data["data"].get("domains", [])
                if not isinstance(domains, list):
                    domains = []
                cache_data = {
                    "create_at": current_time.isoformat(),
                    "domains": domains,
                }

                # Write the updated cache to the file
                with open(cache_file, "w", encoding="utf-8") as file:  # Specify encoding
                    json.dump(cache_data, file)
                return domains if isinstance(domains, list) else []
        except Exception as e:
            logger.exception("Error updating domain cache: %s", e)
            return []

        # Ensure a return statement in case of unexpected flow
        return []
