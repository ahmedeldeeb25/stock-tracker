"""Alert logic for checking if price targets are met."""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Alert:
    """Represents a price alert."""

    def __init__(self, symbol: str, current_price: float, target_price: float,
                 target_type: str, trim_percentage: Optional[float] = None):
        """Initialize an alert.

        Args:
            symbol: Stock ticker symbol
            current_price: Current stock price
            target_price: Target price
            target_type: Type of target (Buy, Sell, DCA, Trim)
            trim_percentage: Percentage to sell (for Trim type)
        """
        self.symbol = symbol
        self.current_price = current_price
        self.target_price = target_price
        self.target_type = target_type
        self.trim_percentage = trim_percentage

    def get_message(self) -> str:
        """Generate alert message.

        Returns:
            Formatted alert message
        """
        base_msg = (
            f"🔔 ALERT: {self.symbol}\n"
            f"Target Type: {self.target_type}\n"
            f"Current Price: ${self.current_price:.2f}\n"
            f"Target Price: ${self.target_price:.2f}\n"
        )

        if self.target_type in ["Buy", "DCA"]:
            base_msg += f"Price dropped below target! Consider {self.target_type.lower()}ing.\n"
        elif self.target_type == "Sell":
            base_msg += f"Price rose above target! Consider selling.\n"
        elif self.target_type == "Trim":
            base_msg += f"Price rose above target! Consider trimming {self.trim_percentage}% of position.\n"

        return base_msg


class AlertChecker:
    """Checks if stock prices meet alert criteria."""

    def check_alert(self, entry: Dict[str, Any], current_price: float) -> Optional[Alert]:
        """Check if a single watchlist entry triggers an alert.

        Args:
            entry: Watchlist entry with target information
            current_price: Current stock price

        Returns:
            Alert object if triggered, None otherwise
        """
        if current_price is None:
            return None

        symbol = entry['symbol']
        target_price = entry['target_price']
        target_type = entry['target_type']
        trim_percentage = entry.get('trim_percentage')

        # Buy/DCA: Alert if price drops below target
        if target_type in ["Buy", "DCA"]:
            if current_price <= target_price:
                logger.info(f"Alert triggered for {symbol}: {target_type} target met")
                return Alert(symbol, current_price, target_price, target_type)

        # Sell/Trim: Alert if price rises above target
        elif target_type in ["Sell", "Trim"]:
            if current_price >= target_price:
                logger.info(f"Alert triggered for {symbol}: {target_type} target met")
                return Alert(symbol, current_price, target_price, target_type, trim_percentage)

        return None

    def check_all_alerts(self, watchlist: List[Dict[str, Any]],
                        prices: Dict[str, Optional[float]]) -> List[Alert]:
        """Check all watchlist entries for alerts.

        Args:
            watchlist: List of watchlist entries
            prices: Dictionary mapping symbols to current prices

        Returns:
            List of triggered alerts
        """
        alerts = []

        for entry in watchlist:
            symbol = entry['symbol']
            current_price = prices.get(symbol)

            alert = self.check_alert(entry, current_price)
            if alert:
                alerts.append(alert)

        logger.info(f"Found {len(alerts)} alert(s)")
        return alerts
