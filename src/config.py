"""Configuration management for the stock tracker."""

import json
import os
from typing import Dict, Any


class Config:
    """Manages application configuration."""

    def __init__(self, config_path: str = "config.json"):
        """Initialize configuration.

        Args:
            config_path: Path to the configuration JSON file
        """
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment variables."""
        config = {}

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)

        # Override with environment variables if present
        config['email'] = {
            'smtp_server': os.getenv('SMTP_SERVER', config.get('email', {}).get('smtp_server', 'smtp.gmail.com')),
            'smtp_port': int(os.getenv('SMTP_PORT', config.get('email', {}).get('smtp_port', 587))),
            'sender_email': os.getenv('SENDER_EMAIL', config.get('email', {}).get('sender_email', '')),
            'sender_password': os.getenv('SENDER_PASSWORD', config.get('email', {}).get('sender_password', '')),
            'recipient_email': os.getenv('RECIPIENT_EMAIL', config.get('email', {}).get('recipient_email', ''))
        }

        config['telegram'] = {
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', config.get('telegram', {}).get('bot_token', '')),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID', config.get('telegram', {}).get('chat_id', ''))
        }

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    @property
    def email_config(self) -> Dict[str, Any]:
        """Get email configuration."""
        return self._config.get('email', {})

    @property
    def telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration."""
        return self._config.get('telegram', {})
