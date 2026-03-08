import logging
from smtplib import SMTPException

from flask_mail import Mail, Message

mail = Mail()

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str) -> None:
    """Send a single HTML email.

    Catches SMTPException to prevent crashing the caller.
    """
    try:
        msg = Message(subject=subject, recipients=[to], html=html_body)
        mail.send(msg)
        logger.info("Email sent to %s | subject: %s", to, subject)
    except SMTPException:
        logger.exception("Failed to send email to %s", to)
