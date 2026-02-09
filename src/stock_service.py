"""Business logic service for stock operations."""

import logging
from typing import List, Optional, Dict, Any
from datetime import date

from src.db_manager import DatabaseManager
from src.stock_fetcher import StockFetcher
from src.models import Stock, Target, Tag, Note, StockWithDetails, Holding

logger = logging.getLogger(__name__)


class StockService:
    """Service layer for stock-related business logic."""

    def __init__(self, db_manager: DatabaseManager, stock_fetcher: StockFetcher):
        """Initialize stock service.

        Args:
            db_manager: Database manager instance
            stock_fetcher: Stock price fetcher instance
        """
        self.db = db_manager
        self.fetcher = stock_fetcher

    def create_stock_with_targets(self, symbol: str, company_name: Optional[str],
                                  targets: List[Dict[str, Any]], tags: List[str]) -> Dict[str, Any]:
        """Create a stock with targets and tags.

        Args:
            symbol: Stock ticker symbol
            company_name: Company name (will be fetched if not provided)
            targets: List of target dicts with target_type, target_price, etc.
            tags: List of tag names

        Returns:
            Dictionary with created stock data
        """
        # Check if stock already exists
        existing_stock = self.db.get_stock_by_symbol(symbol)
        if existing_stock:
            raise ValueError(f"Stock {symbol} already exists")

        # Fetch company name if not provided
        if not company_name or company_name.strip() == '':
            logger.info(f"Fetching company name for {symbol}")
            company_info = self.fetcher.get_company_info(symbol)
            if company_info and company_info.get('name'):
                company_name = company_info['name']
                logger.info(f"Fetched company name: {company_name}")

        # Create stock
        stock_id = self.db.create_stock(symbol, company_name)
        logger.info(f"Created stock: {symbol} (ID: {stock_id})")

        # Create targets
        created_targets = []
        for target_data in targets:
            target_id = self.db.create_target(
                stock_id=stock_id,
                target_type=target_data['target_type'],
                target_price=target_data['target_price'],
                trim_percentage=target_data.get('trim_percentage'),
                alert_note=target_data.get('alert_note')
            )
            created_targets.append(target_id)
            logger.info(f"Created target: {target_data['target_type']} @ ${target_data['target_price']}")

        # Add tags
        for tag_name in tags:
            tag = self.db.get_tag_by_name(tag_name)
            if not tag:
                # Create tag if it doesn't exist
                tag_id = self.db.create_tag(tag_name)
                logger.info(f"Created new tag: {tag_name}")
            else:
                tag_id = tag.id

            self.db.add_tag_to_stock(stock_id, tag_id)

        return {
            "id": stock_id,
            "symbol": symbol,
            "company_name": company_name,
            "targets": created_targets,
            "tags": tags
        }

    def get_stock_with_details(self, symbol: str, include_price: bool = True) -> Optional[Dict[str, Any]]:
        """Get stock with all details including current price.

        Args:
            symbol: Stock ticker symbol
            include_price: Whether to fetch current price

        Returns:
            Dictionary with stock details
        """
        stock = self.db.get_stock_by_symbol(symbol)
        if not stock:
            return None

        # Get related data
        targets = self.db.get_targets_for_stock(stock.id)
        tags = self.db.get_tags_for_stock(stock.id)
        timeframes = self.db.get_timeframes_for_stock(stock.id)
        notes = self.db.get_notes_for_stock(stock.id)
        notes_count = self.db.get_notes_count_for_stock(stock.id)
        latest_alert = self.db.get_latest_alert_for_stock(stock.id)
        holding = self.db.get_holding_for_stock(stock.id)

        result = {
            "id": stock.id,
            "symbol": stock.symbol,
            "company_name": stock.company_name,
            "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags],
            "timeframes": [{"id": tf.id, "name": tf.name, "color": tf.color, "description": tf.description} for tf in timeframes],
            "targets": [self._target_to_dict(t) for t in targets],
            "notes": [self._note_to_dict(n) for n in notes],
            "notes_count": notes_count,
            "created_at": stock.created_at.isoformat() if stock.created_at else None,
            "updated_at": stock.updated_at.isoformat() if stock.updated_at else None
        }

        # Add latest alert if exists
        if latest_alert:
            result["latest_alert"] = {
                "triggered_at": latest_alert.triggered_at.isoformat() if latest_alert.triggered_at else None,
                "target_type": latest_alert.target_type,
                "target_price": latest_alert.target_price
            }

        # Fetch current price and RSI
        if include_price:
            current_price = self.fetcher.get_current_price(stock.symbol)
            if current_price:
                result["current_price"] = current_price

                # Add status for each target
                for target_dict in result["targets"]:
                    target_dict.update(self._calculate_target_status(current_price, target_dict))

                # Add holding with calculated values
                if holding:
                    result["holding"] = self._calculate_holding_values(holding, current_price)

            # Fetch RSI
            rsi = self.fetcher.get_rsi(stock.symbol)
            if rsi:
                result["rsi"] = rsi

            # Fetch after-hours price
            after_hours = self.fetcher.get_after_hours_price(stock.symbol)
            if after_hours:
                result["after_hours"] = after_hours

            # Fetch fundamental data
            fundamental_data = self.fetcher.get_fundamental_data(stock.symbol)
            if fundamental_data:
                result["fundamental_data"] = fundamental_data

        return result

    def get_all_stocks_with_details(self, tag: Optional[str] = None, search: Optional[str] = None,
                                    include_prices: bool = False) -> List[Dict[str, Any]]:
        """Get all stocks with details.

        Args:
            tag: Filter by tag name
            search: Search term
            include_prices: Whether to fetch current prices

        Returns:
            List of stock dictionaries
        """
        stocks = self.db.get_all_stocks(tag=tag, search=search)
        results = []

        # Early return if no stocks
        if not stocks:
            return results

        # Fetch all prices at once if needed
        prices = {}
        info_dict = {}  # Store ticker.info for all stocks
        if include_prices:
            symbols = [s.symbol for s in stocks]
            # Batch fetch prices using optimized yfinance.download
            prices = self.fetcher.get_multiple_prices(symbols)
            # Batch fetch ticker.info in parallel (for after-hours + price change)
            info_dict = self.fetcher.get_multiple_info(symbols)

        # Batch fetch all related data to avoid N+1 queries (HIGH-008 fix)
        stock_ids = [s.id for s in stocks]
        targets_batch = self.db.get_targets_for_stocks_batch(stock_ids)
        tags_batch = self.db.get_tags_for_stocks_batch(stock_ids)
        timeframes_batch = self.db.get_timeframes_for_stocks_batch(stock_ids)
        notes_counts = self.db.get_notes_count_for_stocks_batch(stock_ids)
        latest_alerts = self.db.get_latest_alert_for_stocks_batch(stock_ids)
        holdings_batch = self.db.get_holdings_for_stocks_batch(stock_ids)

        for stock in stocks:
            # Retrieve pre-fetched data from batch results
            targets = targets_batch.get(stock.id, [])
            tags = tags_batch.get(stock.id, [])
            timeframes = timeframes_batch.get(stock.id, [])
            notes_count = notes_counts.get(stock.id, 0)
            latest_alert = latest_alerts.get(stock.id)

            stock_dict = {
                "id": stock.id,
                "symbol": stock.symbol,
                "company_name": stock.company_name,
                "exchange": stock.exchange,
                "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags],
                "timeframes": [{"id": tf.id, "name": tf.name, "color": tf.color, "description": tf.description} for tf in timeframes],
                "targets": [self._target_to_dict(t) for t in targets],
                "notes_count": notes_count,
                "created_at": stock.created_at.isoformat() if stock.created_at else None,
                "updated_at": stock.updated_at.isoformat() if stock.updated_at else None
            }

            if latest_alert:
                stock_dict["latest_alert"] = {
                    "triggered_at": latest_alert.triggered_at.isoformat() if latest_alert.triggered_at else None,
                    "target_type": latest_alert.target_type,
                    "target_price": latest_alert.target_price
                }

            # Add price data
            if include_prices:
                current_price = prices.get(stock.symbol)
                if current_price:
                    stock_dict["current_price"] = current_price

                    # Add status for each target
                    for target_dict in stock_dict["targets"]:
                        target_dict.update(self._calculate_target_status(current_price, target_dict))

                    # Add holding with calculated values
                    holding = holdings_batch.get(stock.id)
                    if holding:
                        stock_dict["holding"] = self._calculate_holding_values(holding, current_price)

                # Extract after-hours and price change from batch-fetched info
                info = info_dict.get(stock.symbol)
                if info:
                    # Extract after-hours data
                    if 'postMarketPrice' in info and info['postMarketPrice']:
                        stock_dict["after_hours"] = {
                            'price': float(info['postMarketPrice']),
                            'change': float(info.get('postMarketChange', 0)),
                            'change_percent': float(info.get('postMarketChangePercent', 0)),
                            'time': info.get('postMarketTime', '')
                        }
                    elif 'preMarketPrice' in info and info['preMarketPrice']:
                        stock_dict["after_hours"] = {
                            'price': float(info['preMarketPrice']),
                            'change': float(info.get('preMarketChange', 0)),
                            'change_percent': float(info.get('preMarketChangePercent', 0)),
                            'time': info.get('preMarketTime', ''),
                            'is_premarket': True
                        }

                    # Extract daily price change
                    if 'regularMarketChangePercent' in info:
                        stock_dict["price_change_percent"] = info['regularMarketChangePercent']

            results.append(stock_dict)

        return results

    def get_stock_status(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock with current price and target status.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with stock status
        """
        return self.get_stock_with_details(symbol, include_price=True)

    def _target_to_dict(self, target: Target) -> Dict[str, Any]:
        """Convert Target object to dictionary.

        Args:
            target: Target object

        Returns:
            Dictionary representation
        """
        return {
            "id": target.id,
            "target_type": target.target_type,
            "target_price": target.target_price,
            "trim_percentage": target.trim_percentage,
            "alert_note": target.alert_note,
            "is_active": target.is_active,
            "created_at": target.created_at.isoformat() if target.created_at else None
        }

    def _note_to_dict(self, note: Note) -> Dict[str, Any]:
        """Convert Note object to dictionary.

        Args:
            note: Note object

        Returns:
            Dictionary representation
        """
        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "note_date": note.note_date.isoformat() if note.note_date else None,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None
        }

    def _calculate_target_status(self, current_price: float, target_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate target status based on current price.

        Args:
            current_price: Current stock price
            target_dict: Target dictionary

        Returns:
            Dictionary with difference and trigger status
        """
        target_price = target_dict['target_price']
        target_type = target_dict['target_type']

        difference = current_price - target_price
        difference_percent = (difference / target_price) * 100

        is_triggered = False
        if target_type in ["Buy", "DCA"]:
            is_triggered = current_price <= target_price
        elif target_type in ["Sell", "Trim"]:
            is_triggered = current_price >= target_price

        return {
            "difference": round(difference, 2),
            "difference_percent": round(difference_percent, 2),
            "is_triggered": is_triggered
        }

    def _calculate_holding_values(
        self,
        holding: Holding,
        current_price: Optional[float]
    ) -> Dict[str, Any]:
        """Calculate holding values including gain/loss.

        Args:
            holding: Holding object
            current_price: Current stock price

        Returns:
            Dictionary with calculated values
        """
        result = {
            "id": holding.id,
            "shares": holding.shares,
            "average_cost": holding.average_cost,
            "created_at": holding.created_at.isoformat() if holding.created_at else None,
            "updated_at": holding.updated_at.isoformat() if holding.updated_at else None
        }

        # Calculate position value
        if current_price:
            result["position_value"] = round(holding.shares * current_price, 2)

        # Calculate gain/loss if average_cost is set
        if holding.average_cost and current_price:
            cost_basis_total = holding.shares * holding.average_cost
            position_value = holding.shares * current_price
            gain_loss = position_value - cost_basis_total
            gain_loss_percent = (gain_loss / cost_basis_total) * 100

            result["cost_basis_total"] = round(cost_basis_total, 2)
            result["gain_loss"] = round(gain_loss, 2)
            result["gain_loss_percent"] = round(gain_loss_percent, 2)

        return result
