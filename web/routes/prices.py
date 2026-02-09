"""Prices API routes."""

from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

prices_bp = Blueprint('prices', __name__)


@prices_bp.route('/market-overview', methods=['GET'])
def get_market_overview():
    """Get market overview data including indices, VIX, and sentiment indicators."""
    try:
        data = current_app.stock_fetcher.get_market_overview()
        return jsonify(data)

    except Exception as e:
        logger.error(f"Error fetching market overview: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@prices_bp.route('/<symbol>', methods=['GET'])
def get_price(symbol):
    """Get current price for a symbol."""
    try:
        current_price = current_app.stock_fetcher.get_current_price(symbol.upper())

        if current_price is None:
            return jsonify({"error": f"Could not fetch price for {symbol}"}), 404

        # TODO: Calculate change and change_percent (requires historical data)
        return jsonify({
            "symbol": symbol.upper(),
            "current_price": current_price,
            "change": 0,  # Placeholder
            "change_percent": 0  # Placeholder
        })

    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@prices_bp.route('/batch', methods=['POST'])
def get_batch_prices():
    """Get prices for multiple symbols.

    Body:
        {
            "symbols": ["AMZN", "HIMS", "ZETA"]
        }
    """
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])

        if not symbols:
            return jsonify({"error": "symbols array is required"}), 400

        prices = current_app.stock_fetcher.get_multiple_prices(symbols)

        result = {}
        for symbol, price in prices.items():
            if price is not None:
                result[symbol] = {
                    "price": price,
                    "change": 0,  # Placeholder
                    "change_percent": 0  # Placeholder
                }
            else:
                result[symbol] = None

        return jsonify({"prices": result})

    except Exception as e:
        logger.error(f"Error fetching batch prices: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
