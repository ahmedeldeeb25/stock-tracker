"""Telegram notification service using Telegram Bot API."""

import requests
from typing import List
import logging

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends Telegram notifications for stock alerts."""

    def __init__(self, bot_token: str, chat_id: str):
        """Initialize Telegram notifier.

        Args:
            bot_token: Telegram Bot API token (get from @BotFather)
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send a message via Telegram.

        Args:
            text: Message text to send
            parse_mode: Parse mode (HTML, Markdown, or None)

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Telegram message sent successfully to chat {self.chat_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False

    def send_alert(self, subject: str, body: str) -> bool:
        """Send a Telegram alert.

        Args:
            subject: Alert subject/title
            body: Alert body content

        Returns:
            True if successful, False otherwise
        """
        # Format message with HTML for better readability
        message = f"<b>{subject}</b>\n\n{body}"
        return self.send_message(message)

    def send_multiple_alerts(self, alerts: List) -> bool:
        """Send Telegram message with multiple alerts.

        Args:
            alerts: List of Alert objects

        Returns:
            True if successful, False otherwise
        """
        if not alerts:
            logger.info("No alerts to send")
            return True

        # Build formatted message
        message = f"<b>🔔 Stock Alert: {len(alerts)} Target(s) Met</b>\n"
        message += "═" * 30 + "\n\n"

        for i, alert in enumerate(alerts, 1):
            # Parse the alert message and format for Telegram
            alert_text = alert.get_message()

            # Format each alert nicely
            lines = alert_text.strip().split('\n')
            symbol_line = lines[0] if lines else ""

            message += f"<b>{i}. {symbol_line.replace('🔔 ALERT: ', '')}</b>\n"

            for line in lines[1:]:
                if line.strip():
                    if "Target Type:" in line:
                        message += f"<b>{line}</b>\n"
                    elif "Current Price:" in line or "Target Price:" in line:
                        message += f"<code>{line}</code>\n"
                    else:
                        message += f"{line}\n"

            if i < len(alerts):
                message += "\n" + "─" * 30 + "\n\n"

        message += "\n<i>📱 Automated message from Stock Tracker</i>"

        return self.send_message(message)

    def test_connection(self) -> bool:
        """Test the Telegram bot connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                logger.info(f"Telegram bot connected: @{bot_info.get('username')}")
                return True
            else:
                logger.error("Telegram bot connection failed")
                return False

        except Exception as e:
            logger.error(f"Failed to test Telegram connection: {e}")
            return False
