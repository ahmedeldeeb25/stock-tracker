#!/usr/bin/env python3
"""Script to update exchange information for all existing stocks."""

import sys
import os
import time
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db_manager import DatabaseManager
from src.stock_fetcher import StockFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_all_exchanges():
    """Fetch and update exchange information for all stocks."""

    # Initialize services
    db = DatabaseManager()
    fetcher = StockFetcher()

    # Get all stocks
    stocks = db.get_all_stocks()

    if not stocks:
        logger.info("No stocks found in database")
        return

    logger.info(f"Found {len(stocks)} stocks to update")

    updated = 0
    skipped = 0
    failed = 0

    for stock in stocks:
        # Skip if exchange already set
        if stock.exchange:
            logger.info(f"Skipping {stock.symbol} - exchange already set to {stock.exchange}")
            skipped += 1
            continue

        logger.info(f"Fetching exchange for {stock.symbol}...")

        try:
            # Fetch company info (includes exchange)
            company_info = fetcher.get_company_info(stock.symbol)

            if company_info and company_info.get('exchange'):
                exchange = company_info['exchange']
                company_name = company_info.get('name') or stock.company_name

                # Update stock with exchange and company name
                db.update_stock(
                    stock.id,
                    company_name=company_name,
                    exchange=exchange
                )

                logger.info(f"✓ Updated {stock.symbol}: {exchange} - {company_name}")
                updated += 1
            else:
                logger.warning(f"✗ Could not fetch exchange for {stock.symbol}")
                failed += 1

            # Rate limiting - be nice to yfinance
            time.sleep(1)

        except Exception as e:
            logger.error(f"✗ Error updating {stock.symbol}: {e}")
            failed += 1

    # Summary
    logger.info("\n" + "="*50)
    logger.info("Exchange Update Summary")
    logger.info("="*50)
    logger.info(f"Total stocks: {len(stocks)}")
    logger.info(f"Updated: {updated}")
    logger.info(f"Skipped (already had exchange): {skipped}")
    logger.info(f"Failed: {failed}")
    logger.info("="*50)


if __name__ == '__main__':
    logger.info("Starting exchange update process...")
    try:
        update_all_exchanges()
        logger.info("Exchange update complete!")
    except KeyboardInterrupt:
        logger.info("\nUpdate interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
