import boto3
from botocore.exceptions import BotoCoreError, ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


class EmailService:
    def __init__(self):
        self.ses_client = boto3.client(
            "ses",
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.sender_email = os.getenv("EMAIL_FROM_EMAIL")
        self.sender_name = os.getenv("EMAIL_FROM_NAME")

    def send_email(self, to_emails, subject, body, is_html=True):
        """
        Send an email using AWS SES.
        """
        try:
            # Prepare the email content
            if isinstance(to_emails, str):
                to_emails = [to_emails]

            charset = "UTF-8"
            email_subject = subject
            email_body = body

            # Send the email
            response = self.ses_client.send_email(
                Source=f"{self.sender_name} <{self.sender_email}>",
                Destination={"ToAddresses": to_emails},
                Message={
                    "Subject": {"Data": email_subject, "Charset": charset},
                    "Body": {
                        "Html" if is_html else "Text": {"Data": email_body, "Charset": charset}
                    },
                },
            )
            print(f"Email sent! Message ID: {response['MessageId']}")
            return response["MessageId"]
        except (BotoCoreError, ClientError) as error:
            print(f"Error sending email: {error}")
            return None

    def send_email_with_attachment(self, to_emails, subject, body, attachment_path):
        """
        Send an email with a PDF attachment using AWS SES.
        """
        try:
            # Prepare the email content
            if isinstance(to_emails, str):
                to_emails = [to_emails]

            msg = MIMEMultipart()
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject

            # Add the email body
            msg.attach(MIMEText(body, "html"))

            # Attach the file
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}",
                )
                msg.attach(part)

            # Send the email
            response = self.ses_client.send_raw_email(
                Source=f"{self.sender_name} <{self.sender_email}>",
                Destinations=to_emails,
                RawMessage={"Data": msg.as_string()},
            )
            print(f"Email with attachment sent! Message ID: {response['MessageId']}")
            return response["MessageId"]
        except (BotoCoreError, ClientError, FileNotFoundError) as error:
            print(f"Error sending email with attachment: {error}")
            return None


# Example usage
if __name__ == "__main__":
    email_service = EmailService()

    # Send a simple email
    email_service.send_email(
        to_emails=["recipient@example.com"],
        subject="Test Email",
        body="<h1>Hello, this is a test email!</h1>",
    )

    # Send an email with a PDF attachment
    email_service.send_email_with_attachment(
        to_emails=["recipient@example.com"],
        subject="Test Email with Attachment",
        body="<h1>Please find the attached PDF.</h1>",
        attachment_path="path/to/your/file.pdf",
    )