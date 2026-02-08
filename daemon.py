#!/usr/bin/env python3
"""Daemon mode for continuous stock monitoring in the background."""

import logging
import sys
import schedule
import time
from dotenv import load_dotenv

from src.config import Config
from src.stock_fetcher import StockFetcher
from src.db_manager import DatabaseManager
from src.alert_checker import AlertChecker
from src.email_notifier import EmailNotifier
from src.telegram_notifier import TelegramNotifier


def setup_logging():
    """Configure logging for the daemon."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('stock_tracker.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def check_stocks():
    """Check stock prices and send alerts if needed."""
    logger = logging.getLogger(__name__)
    logger.info("="*50)
    logger.info("Running scheduled stock check")

    try:
        # Initialize components
        config = Config()
        db_manager = DatabaseManager("stock_tracker.db")
        stock_fetcher = StockFetcher()
        alert_checker = AlertChecker()

        # Get all stocks with active targets from database
        stocks = db_manager.get_all_stocks()
        if not stocks:
            logger.warning("No stocks in database")
            return

        # Build watchlist-like structure from database
        watchlist = []
        symbols = set()

        for stock in stocks:
            symbols.add(stock.symbol)
            # Get active targets for this stock
            targets = db_manager.get_targets_for_stock(stock.id)
            active_targets = [t for t in targets if t.is_active]

            for target in active_targets:
                entry = {
                    'symbol': stock.symbol,
                    'stock_id': stock.id,
                    'target_id': target.id,
                    'target_type': target.target_type,
                    'target_price': target.target_price,
                    'trim_percentage': target.trim_percentage,
                    'alert_note': target.alert_note
                }
                watchlist.append(entry)

        if not watchlist:
            logger.warning("No active targets found")
            return

        logger.info(f"Checking {len(symbols)} stocks with {len(watchlist)} active targets")

        # Fetch current prices
        prices = stock_fetcher.get_multiple_prices(list(symbols))

        # Check for alerts
        alerts = alert_checker.check_all_alerts(watchlist, prices)

        if alerts:
            logger.info(f"Found {len(alerts)} alert(s), recording and sending notification")

            # Record alerts in database
            for alert in alerts:
                # Find the matching watchlist entry to get stock_id, target_id and alert_note
                matching_entry = next(
                    (e for e in watchlist if e['symbol'] == alert.symbol
                     and e['target_type'] == alert.target_type
                     and e['target_price'] == alert.target_price),
                    None
                )

                if matching_entry:
                    db_manager.create_alert_history(
                        stock_id=matching_entry['stock_id'],
                        target_id=matching_entry['target_id'],
                        current_price=alert.current_price,
                        target_price=alert.target_price,
                        target_type=alert.target_type,
                        alert_note=matching_entry.get('alert_note'),
                        email_sent=False  # Will update after sending
                    )

            # Initialize email notifier
            email_config = config.email_config
            email_notifier = EmailNotifier(
                smtp_server=email_config.get('smtp_server'),
                smtp_port=email_config.get('smtp_port'),
                sender_email=email_config.get('sender_email'),
                sender_password=email_config.get('sender_password'),
                recipient_email=email_config.get('recipient_email')
            )

            # Initialize Telegram notifier
            telegram_config = config.telegram_config
            telegram_notifier = None
            if telegram_config.get('bot_token') and telegram_config.get('chat_id'):
                telegram_notifier = TelegramNotifier(
                    bot_token=telegram_config.get('bot_token'),
                    chat_id=telegram_config.get('chat_id')
                )

            # Send alerts via both channels
            email_success = False
            telegram_success = False

            # Send email notification
            if email_config.get('sender_email') and email_config.get('recipient_email'):
                email_success = email_notifier.send_multiple_alerts(alerts)
                if email_success:
                    logger.info("Email notification sent successfully")
                else:
                    logger.error("Failed to send email notification")

            # Send Telegram notification
            if telegram_notifier:
                telegram_success = telegram_notifier.send_multiple_alerts(alerts)
                if telegram_success:
                    logger.info("Telegram notification sent successfully")
                else:
                    logger.error("Failed to send Telegram notification")

            # Log notification status
            if email_success or telegram_success:
                logger.info("Notifications sent successfully")
                # Update alert history to mark notification as sent
                # Note: This is a simple implementation. Could be improved to track specific alerts
            else:
                logger.warning("All notification channels failed")
        else:
            logger.info("No alerts triggered")

    except Exception as e:
        logger.error(f"Error during stock check: {e}", exc_info=True)


def main():
    """Run the stock tracker daemon."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Stock Tracker Daemon Starting")
    logger.info("Running checks every hour during market hours (9 AM - 5 PM EST)")
    logger.info("Press Ctrl+C to stop")

    # Load environment variables
    load_dotenv()

    # Schedule checks every hour during typical market hours
    # You can adjust these times based on your needs
    for hour in range(9, 18):  # 9 AM to 5 PM
        schedule.every().day.at(f"{hour:02d}:00").do(check_stocks)

    # Optional: Run an immediate check on startup
    logger.info("Running initial check...")
    check_stocks()

    # Keep the daemon running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks
    except KeyboardInterrupt:
        logger.info("Stock Tracker Daemon stopping...")
        sys.exit(0)


if __name__ == "__main__":
    main()
