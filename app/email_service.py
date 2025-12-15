import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import settings
from app.models import EmailRequest

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.recipient_email = str(settings.recipient_email)
        self.recipient_name = settings.recipient_name

    async def send_notification_email(self, email_request: EmailRequest) -> None:
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = f"New Contact: {email_request.fullname}"
            message['From'] = self.smtp_username
            message['To'] = self.recipient_email
            message['Reply-To'] = str(email_request.email)

            template = jinja_env.get_template('notification.html')
            html_content = template.render(
                fullname=email_request.fullname,
                email=str(email_request.email),
                phone=email_request.phone,
                company=email_request.company,
                message=email_request.message,
                recipient_name=self.recipient_name
            )

            text_content = f"""
New Contact Form Submission

Name: {email_request.fullname}
Email: {email_request.email}
Phone: {email_request.phone}
Company: {email_request.company}
Message: {email_request.message or 'N/A'}

---
Sent via Mailbridge
            """.strip()

            part_text = MIMEText(text_content, 'plain')
            part_html = MIMEText(html_content, 'html')
            message.attach(part_text)
            message.attach(part_html)

            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls,
                timeout=10,
            )

            logger.info(f"Email sent to {self.recipient_email} from {email_request.email}")

        except aiosmtplib.SMTPException as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise


email_service = EmailService()
