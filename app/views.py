from fastapi import Request
from pydantic import BaseModel
from app.expand import LinkExpander
from app.pwScrapper import PWScrapper
from services.SNSService import SnsEmailService  # Updated to use SnsEmailService
from logging_config import logger  # Import the logger

# Initialize the LinkExpander class
link_expander = LinkExpander()

# Initialize the PWScrapper class
pwscrapper = PWScrapper()

# Initialize the EmailService class
email_service = SnsEmailService()  # Updated to use SnsEmailService


class URLRequest(BaseModel):
    url: str


class URLViews:
    def __init__(self):
        self.link_expander = link_expander
        self.email_service = email_service  # Updated to use SnsEmailService

    async def expand_url_view(self, request: Request):
        body = await request.json()
        url = body.get("url", "")
        toReturn = self.initialize_response(url)

        if not url:
            return self.handle_missing_url(toReturn)
        try:
            toReturn = await self.handle_url_expansion(url, toReturn)
            if toReturn["expanded"] is True:
                self.send_success_email(url, toReturn)
                logger.warning(f"URL expansion failed for {url}")
            await self.check_flipkart_and_unknown_patterns(url, toReturn)
        except Exception as e:
            toReturn = self.handle_exception(e, toReturn)

        return toReturn, 200 if toReturn["expanded"] else 500

    def initialize_response(self, url):
        return {
            "expanded": True,
            "url": url,
            "expanded_url": url,
            "error_message": '',
        }

    def handle_missing_url(self, toReturn):
        toReturn["expanded"] = False
        toReturn["error_message"] = "URL is required"
        logger.warning("URL is missing in the request body")
        return toReturn, 400

    async def handle_url_expansion(self, url, toReturn):
        try:
            response = await self.link_expander.handle_url({"url": url})
            if response is None or not response.get("expanded", False):
                toReturn["expanded"] = False
                toReturn["error_message"] = response.get(
                    "error_message", "Error in LinkExpander"
                )
                logger.error(f"Error in LinkExpander: {toReturn['error_message']}")
            else:
                toReturn["expanded_url"] = response["expanded_url"]
                logger.info(f"URL expanded successfully: {response['expanded_url']}")
        except Exception as e:
            toReturn["expanded"] = False
            toReturn["error_message"] = str(e)
            logger.exception(f"Exception in handle_url: {e}")
        return toReturn

    def send_success_email(self, url, toReturn):
        try:
            email_params = {
                "URL": url,
                "Expanded_URL": toReturn["expanded_url"],
                "Error": toReturn["error_message"],
            }
            subject = "URL Expansion Failed Notification"

            # Define the recipients
            recipients = ["aarif@jetbro.in"]

            # Send email to each recipient
            for recipient in recipients:
                message_id = self.email_service.send_email(
                    to_email=recipient, subject=subject, params=email_params
                )
                if message_id:
                    logger.info(
                        f"Email sent successfully to {recipient}! Message ID: {message_id}"
                    )
                else:
                    logger.error(f"Failed to send email to {recipient}.")
        except Exception as email_error:
            logger.exception(f"Error sending email: {email_error}")

    async def check_flipkart_and_unknown_patterns(self, url, toReturn):
        """
        Checks for Flipkart-specific patterns and handles cases where toReturn["expanded"] is False.
        """
        flipkart_patterns = [
            "flipkart.com/s/",
            "fkrt.it",
            "fkrt.cc",
            "fkrt.to",
            "fkrt.co",
        ]

        try:
            # Check if the URL matches any Flipkart-specific patterns
            if (
                any(
                    pattern in toReturn["expanded_url"] for pattern in flipkart_patterns
                )
                or toReturn['expanded'] is False
            ):
                logger.info(
                    f"Flipkart pattern detected in URL: {toReturn['expanded_url']}"
                )
                responseOfPWScrapper = await pwscrapper.expand_urls_sync([url])
                if responseOfPWScrapper and len(responseOfPWScrapper) > 0:
                    expanded = responseOfPWScrapper[0]
                    toReturn["expanded_url"] = expanded
                    logger.info(
                        f"PWScrapper expanded Flipkart URL successfully: {expanded}"
                    )
                else:
                    toReturn["expanded"] = False
                    toReturn["error_message"] = "Error in PWScrapper"
                    logger.error(f"Error in PWScrapper: {toReturn['error_message']}")
            else:
                # Handle unknown patterns
                logger.warning(
                    f"Unknown pattern detected in URL: {toReturn['expanded_url']}"
                )
                toReturn["expanded"] = False
                toReturn["error_message"] = "Unknown URL pattern"
        except Exception as e:
            toReturn["expanded"] = False
            toReturn["error_message"] = str(e)
            logger.exception(f"Exception in check_flipkart_and_unknown_patterns: {e}")

    def handle_exception(self, e, toReturn):
        toReturn["expanded"] = False
        toReturn["error_message"] = str(e)
        logger.exception(f"Exception in expand_url_view: {e}")
        return toReturn
