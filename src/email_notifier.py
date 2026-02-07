"""Email notification service using smtplib."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Sends email notifications for stock alerts."""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str,
                 sender_password: str, recipient_email: str):
        """Initialize email notifier.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            sender_email: Sender email address
            sender_password: Sender email password/app password
            recipient_email: Recipient email address
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

    def send_alert(self, subject: str, body: str) -> bool:
        """Send an email alert.

        Args:
            subject: Email subject
            body: Email body content

        Returns:
            True if successful, False otherwise
        """
        try:
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = self.recipient_email
            message['Subject'] = subject

            message.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {self.recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_multiple_alerts(self, alerts: List) -> bool:
        """Send email with multiple alerts.

        Args:
            alerts: List of Alert objects

        Returns:
            True if successful, False otherwise
        """
        if not alerts:
            logger.info("No alerts to send")
            return True

        subject = f"Stock Alert: {len(alerts)} Target(s) Met"

        body = "Stock Tracker Alert\n"
        body += "=" * 50 + "\n\n"

        for alert in alerts:
            body += alert.get_message()
            body += "\n" + "-" * 50 + "\n\n"

        body += "This is an automated message from your Stock Tracker.\n"

        return self.send_alert(subject, body)
