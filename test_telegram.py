#!/usr/bin/env python3
"""Test Telegram notification setup."""

import sys
from dotenv import load_dotenv

from src.config import Config
from src.telegram_notifier import TelegramNotifier


def main():
    """Test Telegram bot configuration."""
    print("🤖 Telegram Notification Test")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    # Initialize config
    config = Config()
    telegram_config = config.telegram_config

    bot_token = telegram_config.get('bot_token')
    chat_id = telegram_config.get('chat_id')

    # Check if credentials are configured
    if not bot_token or not chat_id:
        print("❌ Error: Telegram credentials not configured")
        print("\nPlease set the following environment variables in .env file:")
        print("  - TELEGRAM_BOT_TOKEN")
        print("  - TELEGRAM_CHAT_ID")
        print("\nHow to set up:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get your bot token from @BotFather")
        print("3. Send a message to your bot")
        print("4. Get your chat ID by visiting:")
        print(f"   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
        sys.exit(1)

    print(f"Bot Token: {'*' * 20}{bot_token[-10:] if len(bot_token) > 10 else bot_token}")
    print(f"Chat ID: {chat_id}")
    print()

    # Initialize notifier
    notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)

    # Test connection
    print("Testing bot connection...")
    if notifier.test_connection():
        print("✅ Bot connection successful!\n")
    else:
        print("❌ Bot connection failed\n")
        sys.exit(1)

    # Send test message
    print("Sending test message...")
    test_message = (
        "<b>🎉 Test Alert</b>\n\n"
        "Your Telegram notifications are working correctly!\n\n"
        "<b>Stock:</b> AAPL\n"
        "<b>Current Price:</b> <code>$150.00</code>\n"
        "<b>Target Price:</b> <code>$145.00</code>\n\n"
        "<i>This is a test message from Stock Tracker</i>"
    )

    if notifier.send_message(test_message):
        print("✅ Test message sent successfully!")
        print("\nCheck your Telegram to see the message.")
        print("Your Telegram notifications are configured correctly! 🎊")
    else:
        print("❌ Failed to send test message")
        sys.exit(1)


if __name__ == "__main__":
    main()
