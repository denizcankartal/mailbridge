import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings
from app.models import EmailRequest

logger = logging.getLogger(__name__)

# Set up Jinja2 environment for email templates
TEMPLATES_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.recipient_email = str(settings.recipient_email)
        self.recipient_name = settings.recipient_name

    async def send_notification_email(self, email_request: EmailRequest) -> None:
        """
        Send a notification email to the configured recipient.

        Args:
            email_request: The email request containing sender details and message

        Raises:
            aiosmtplib.SMTPException: If email sending fails
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = email_request.subject
            message['From'] = f"{self.smtp_username}"
            message['To'] = self.recipient_email
            message['Reply-To'] = email_request.sender_email

            # Render HTML template
            template = jinja_env.get_template('notification.html')
            html_content = template.render(
                sender_name=email_request.sender_name,
                sender_email=email_request.sender_email,
                subject=email_request.subject,
                message=email_request.message,
                recipient_name=self.recipient_name
            )

            # Create plain text version (fallback)
            text_content = f"""
New notification from {email_request.sender_name}

From: {email_request.sender_email}
Subject: {email_request.subject}

Message:
{email_request.message}

---
This email was sent via Granova Email Service
            """.strip()

            # Attach both plain text and HTML versions
            part_text = MIMEText(text_content, 'plain')
            part_html = MIMEText(html_content, 'html')
            message.attach(part_text)
            message.attach(part_html)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls,
                timeout=10,
            )

            logger.info(
                f"Email sent successfully to {self.recipient_email} "
                f"from {email_request.sender_email}"
            )

        except aiosmtplib.SMTPException as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            raise


# Global email service instance
email_service = EmailService()
