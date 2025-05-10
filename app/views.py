from fastapi import HTTPException, Request
from app.expand import LinkExpander
from app.pw_scrapper import PwScrapper
from app.sns_service import SnsEmailService  # Updated to use SnsEmailService
from logging_config import logger  # Import the logger

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
            success, url_or_error = self.link_expander.handle_url(url)
            if not success:
                self.send_failure_notif(url, url_or_error)
                logger.warning("URL expansion failed for %s", url)
                return {"error": url_or_error}, 500  # don't needed to send return here

            expanded_url = url_or_error

            success, expanded_url = self.check_flipkart(expanded_url)

            if not success:
                self.send_failure_notif(url, expanded_url)
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

    def check_flipkart(self, expanded_url: str) -> tuple[bool, str]:
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
        if any(pattern in expanded_url for pattern in flipkart_patterns):
            logger.info("Flipkart pattern detected in URL: %s", expanded_url)
            return pwscrapper.expand_url_sync(expanded_url)

        return True, expanded_url
