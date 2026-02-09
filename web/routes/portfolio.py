"""Portfolio API routes."""

from flask import Blueprint, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/summary', methods=['GET'])
def get_portfolio_summary():
    """Get portfolio summary with total values."""
    try:
        # Get all stocks with holdings
        stocks = current_app.db_manager.get_all_stocks()
        stock_ids = [s.id for s in stocks]

        holdings_batch = current_app.db_manager.get_holdings_for_stocks_batch(stock_ids)

        if not holdings_batch:
            return jsonify({
                "positions_count": 0,
                "total_cost_basis": 0,
                "total_current_value": 0,
                "total_gain_loss": 0,
                "total_gain_loss_percent": 0
            })

        # Fetch current prices for stocks with holdings
        symbols_with_holdings = []
        stock_id_to_symbol = {}
        for stock in stocks:
            if stock.id in holdings_batch:
                symbols_with_holdings.append(stock.symbol)
                stock_id_to_symbol[stock.id] = stock.symbol

        prices = current_app.stock_fetcher.get_multiple_prices(symbols_with_holdings)

        # Calculate totals
        total_cost_basis = 0
        total_current_value = 0
        positions_count = 0

        for stock_id, holding in holdings_batch.items():
            symbol = stock_id_to_symbol.get(stock_id)
            current_price = prices.get(symbol) if symbol else None

            positions_count += 1

            if holding.average_cost:
                total_cost_basis += holding.shares * holding.average_cost

            if current_price:
                total_current_value += holding.shares * current_price

        total_gain_loss = total_current_value - total_cost_basis if total_cost_basis else 0
        total_gain_loss_percent = (total_gain_loss / total_cost_basis * 100) if total_cost_basis else 0

        return jsonify({
            "positions_count": positions_count,
            "total_cost_basis": round(total_cost_basis, 2),
            "total_current_value": round(total_current_value, 2),
            "total_gain_loss": round(total_gain_loss, 2),
            "total_gain_loss_percent": round(total_gain_loss_percent, 2)
        })

    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
