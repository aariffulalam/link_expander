import os
import boto3
from dotenv import load_dotenv
from logging_config import logger  # Import the logger

# Load environment variables from .env file
load_dotenv()


class SnsEmailService:
    def __init__(self) -> None:
        """
        Initializes the SnsEmailService with an SNS client.
        """
        logger.info("Initializing SnsEmailService...")
        self.sns_client = boto3.client(
            "sns",
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    def send_notif(self, subject: str, params: dict[str, str]) -> str:
        """
        Sends an email notification using AWS SNS.

        :param topic_arn: The ARN of the SNS topic.
        :param subject: The subject of the email.
        :param params: A dictionary containing key-value pairs for the email body.
        :return: The message ID of the sent email.
        """
        try:
            # Generate the email body dynamically
            message = self.generate_message(params)

            # Publish the email to the SNS topic
            response = self.sns_client.publish(
                TopicArn=os.getenv("SNS_LEHLAH_EXPAND_NOTIF_ARN"),
                Subject=subject,
                Message=message,
            )
            logger.info("Email sent successfully! Message ID: %s", response["MessageId"])
            return response["MessageId"] or ""
        except Exception as error:
            logger.exception("Error sending email: %s", error)
            return "Error sending email."

    def generate_message(self, params: dict[str, str]) -> str:
        """
        Generates a dynamic email body based on the provided parameters.

        :param params: A dictionary containing key-value pairs for the email body.
        :return: A dynamically generated email body string.
        """
        try:
            message = "\n".join([f"{key}: {value}" for key, value in params.items()])
            logger.info("Generated email body: %s", message)    
            return message
        except Exception as error:
            logger.exception("Error generating email body: %s", error)
            return "Error generating email body."
