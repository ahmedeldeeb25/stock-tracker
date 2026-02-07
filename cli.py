#!/usr/bin/env python3
"""Command-line interface for the stock tracker."""

import click
import logging
from datetime import datetime
from src.config import Config
from src.stock_fetcher import StockFetcher
from src.db_manager import DatabaseManager
from src.alert_checker import AlertChecker
from dotenv import load_dotenv


@click.group()
def cli():
    """Stock Tracker CLI - Monitor stocks and manage watchlist."""
    pass


@cli.command()
@click.argument('symbol')
def price(symbol):
    """Get current price for a specific ticker.

    Example: python cli.py price AAPL
    """
    fetcher = StockFetcher()
    current_price = fetcher.get_current_price(symbol.upper())

    if current_price:
        click.echo(f"\n{symbol.upper()}: ${current_price:.2f}")
        click.echo(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    else:
        click.echo(f"❌ Could not fetch price for {symbol.upper()}", err=True)


@cli.command()
@click.option('--lines', '-n', default=50, help='Number of lines to display')
def logs(lines):
    """View recent log entries.

    Example: python cli.py logs --lines 100
    """
    import os

    log_file = 'stock_tracker.log'

    if not os.path.exists(log_file):
        click.echo("No log file found. Run the tracker first.")
        return

    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]
            click.echo(''.join(recent_lines))
    except Exception as e:
        click.echo(f"Error reading logs: {e}", err=True)


@cli.command()
def status():
    """Check status of all monitored stocks.

    Shows current prices and how close they are to targets.
    """
    load_dotenv()

    db_manager = DatabaseManager("stock_tracker.db")
    fetcher = StockFetcher()
    checker = AlertChecker()

    # Get all stocks from database
    stocks = db_manager.get_all_stocks()
    if not stocks:
        click.echo("No stocks in database.")
        return

    # Get symbols
    symbols = [stock.symbol for stock in stocks]
    prices = fetcher.get_multiple_prices(symbols)

    click.echo("\n" + "="*70)
    click.echo("STOCK TRACKER STATUS")
    click.echo("="*70 + "\n")

    for stock in sorted(stocks, key=lambda s: s.symbol):
        symbol = stock.symbol
        current_price = prices.get(symbol)
        if current_price is None:
            click.echo(f"❌ {symbol}: Unable to fetch price\n")
            continue

        click.echo(f"📊 {symbol}: ${current_price:.2f}")

        # Get all active targets for this stock
        targets = db_manager.get_targets_for_stock(stock.id)
        active_targets = [t for t in targets if t.is_active]

        for target in active_targets:
            target_type = target.target_type
            target_price = target.target_price
            diff = current_price - target_price
            diff_pct = (diff / target_price) * 100

            # Check if alert would trigger
            entry = {
                'symbol': symbol,
                'target_type': target_type,
                'target_price': target_price,
                'trim_percentage': target.trim_percentage
            }
            alert = checker.check_alert(entry, current_price)
            status_icon = "🔔 ALERT!" if alert else "⏳"

            trim_info = ""
            if target_type == "Trim" and target.trim_percentage:
                trim_info = f" ({target.trim_percentage}%)"

            click.echo(f"  {status_icon} {target_type}{trim_info}: "
                      f"${target_price:.2f} "
                      f"({'−' if diff < 0 else '+'}"
                      f"${abs(diff):.2f}, {diff_pct:+.2f}%)")

        click.echo()

    click.echo("="*70 + "\n")


@cli.command()
def list():
    """List all stocks in the database."""
    db_manager = DatabaseManager("stock_tracker.db")

    # Get all stocks
    stocks = db_manager.get_all_stocks()

    if not stocks:
        click.echo("No stocks in database.")
        return

    click.echo("\n" + "="*70)
    click.echo("STOCK LIST")
    click.echo("="*70 + "\n")

    count = 0
    for stock in sorted(stocks, key=lambda s: s.symbol):
        # Get targets for this stock
        targets = db_manager.get_targets_for_stock(stock.id)

        if not targets:
            count += 1
            click.echo(f"{count}. {stock.symbol} - No targets")
            continue

        for target in targets:
            count += 1
            trim_info = ""
            if target.target_type == "Trim" and target.trim_percentage:
                trim_info = f" (Trim {target.trim_percentage}%)"

            status = "✓ Active" if target.is_active else "✗ Inactive"
            click.echo(f"{count}. {stock.symbol} - "
                      f"{target.target_type}{trim_info} @ "
                      f"${target.target_price:.2f} [{status}]")

    click.echo()


@cli.command()
@click.argument('symbol')
@click.argument('target_type', type=click.Choice(['Buy', 'Sell', 'DCA', 'Trim'], case_sensitive=False))
@click.argument('target_price', type=float)
@click.option('--trim-percentage', type=float, help='Percentage to trim (for Trim type)')
@click.option('--company-name', help='Company name (optional)')
@click.option('--alert-note', help='Alert note (optional)')
def add(symbol, target_type, target_price, trim_percentage, company_name, alert_note):
    """Add a stock target to the database.

    Example: python cli.py add AAPL Buy 150.00
    Example: python cli.py add TSLA Trim 300.00 --trim-percentage 25 --alert-note "Take profits"
    """
    db_manager = DatabaseManager("stock_tracker.db")

    symbol = symbol.upper()
    target_type = target_type.capitalize()

    if target_type == "Trim" and trim_percentage is None:
        click.echo("❌ --trim-percentage is required for Trim type", err=True)
        return

    try:
        # Check if stock exists, if not create it
        stock = db_manager.get_stock_by_symbol(symbol)

        if not stock:
            stock_id = db_manager.create_stock(symbol, company_name=company_name)
            click.echo(f"✅ Created stock {symbol}")
        else:
            stock_id = stock.id

        # Add target
        target_id = db_manager.create_target(
            stock_id=stock_id,
            target_type=target_type,
            target_price=target_price,
            trim_percentage=trim_percentage,
            alert_note=alert_note
        )

        trim_info = f" (Trim {trim_percentage}%)" if trim_percentage else ""
        click.echo(f"✅ Added target: {symbol} - {target_type}{trim_info} @ ${target_price:.2f}")

    except Exception as e:
        click.echo(f"❌ Failed to add target: {e}", err=True)


@cli.command()
@click.argument('symbol')
@click.option('--target-type', help='Remove only targets with this target type')
@click.option('--delete-stock', is_flag=True, help='Delete the stock entirely (with all targets)')
def remove(symbol, target_type, delete_stock):
    """Remove targets or stock from the database.

    Example: python cli.py remove AAPL --target-type Buy
    Example: python cli.py remove AAPL --delete-stock
    """
    db_manager = DatabaseManager("stock_tracker.db")
    symbol = symbol.upper()

    try:
        stock = db_manager.get_stock_by_symbol(symbol)

        if not stock:
            click.echo(f"❌ Stock {symbol} not found in database", err=True)
            return

        if delete_stock:
            # Delete the entire stock (cascades to targets)
            success = db_manager.delete_stock(stock.id)
            if success:
                click.echo(f"✅ Deleted stock {symbol} and all its targets")
            else:
                click.echo(f"❌ Failed to delete stock {symbol}", err=True)
        elif target_type:
            # Delete specific target type
            targets = db_manager.get_targets_for_stock(stock.id)
            matching_targets = [t for t in targets if t.target_type == target_type]

            if not matching_targets:
                click.echo(f"❌ No {target_type} targets found for {symbol}", err=True)
                return

            for target in matching_targets:
                db_manager.delete_target(target.id)

            click.echo(f"✅ Removed {len(matching_targets)} {target_type} target(s) for {symbol}")
        else:
            # Delete all targets but keep the stock
            targets = db_manager.get_targets_for_stock(stock.id)

            if not targets:
                click.echo(f"❌ No targets found for {symbol}", err=True)
                return

            for target in targets:
                db_manager.delete_target(target.id)

            click.echo(f"✅ Removed all {len(targets)} target(s) for {symbol}")

    except Exception as e:
        click.echo(f"❌ Failed to remove: {e}", err=True)


@cli.command()
def check():
    """Run a single check for alerts (same as running main.py)."""
    from main import main
    main()


if __name__ == '__main__':
    cli()
