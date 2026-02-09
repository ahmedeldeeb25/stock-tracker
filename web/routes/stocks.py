"""Stocks API routes."""

from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

stocks_bp = Blueprint('stocks', __name__)


@stocks_bp.route('/search', methods=['GET'])
def search_symbols():
    """Search for stock symbols using Yahoo Finance.

    Query Params:
        q: Search query (required)
        limit: Maximum results (default: 10)

    Returns:
        List of matching symbols with name and exchange
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))

        if not query:
            return jsonify({"results": []})

        results = current_app.stock_fetcher.search_symbols(query, limit)
        return jsonify({"results": results})

    except Exception as e:
        logger.error(f"Error searching symbols: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/validate/<symbol>', methods=['GET'])
def validate_symbol(symbol):
    """Validate if a stock symbol exists and get basic info.

    Returns:
        Symbol info if valid, error if invalid
    """
    try:
        # Check if symbol already exists in our database
        existing = current_app.db_manager.get_stock_by_symbol(symbol.upper())
        if existing:
            return jsonify({
                "valid": True,
                "exists_in_db": True,
                "symbol": existing.symbol,
                "name": existing.company_name,
                "message": f"{symbol.upper()} is already in your watchlist"
            })

        # Validate with Yahoo Finance
        result = current_app.stock_fetcher.validate_symbol(symbol)
        if result:
            return jsonify({
                "valid": True,
                "exists_in_db": False,
                "symbol": result["symbol"],
                "name": result["name"],
                "exchange": result["exchange"],
                "type": result["type"]
            })
        else:
            return jsonify({
                "valid": False,
                "message": f"Symbol '{symbol.upper()}' not found"
            }), 404

    except Exception as e:
        logger.error(f"Error validating symbol {symbol}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/check/<symbol>', methods=['GET'])
def check_symbol_exists(symbol):
    """Check if a stock symbol exists in our database.

    Returns:
        exists: true/false
    """
    try:
        existing = current_app.db_manager.get_stock_by_symbol(symbol.upper())
        return jsonify({
            "exists": existing is not None,
            "symbol": symbol.upper()
        })

    except Exception as e:
        logger.error(f"Error checking symbol {symbol}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('', methods=['GET'])
def get_stocks():
    """Get all stocks with optional filters.

    Query Params:
        tag: Filter by tag name
        search: Search in symbol or company name
        include_prices: Include current prices (default: false)
    """
    try:
        tag = request.args.get('tag')
        search = request.args.get('search')
        include_prices = request.args.get('include_prices', 'false').lower() == 'true'

        stocks = current_app.stock_service.get_all_stocks_with_details(
            tag=tag,
            search=search,
            include_prices=include_prices
        )

        # Get all available tags with counts
        tags_with_counts = current_app.db_manager.get_all_tags()
        available_tags = [
            {"id": tag.id, "name": tag.name, "color": tag.color, "count": count}
            for tag, count in tags_with_counts
        ]

        return jsonify({
            "stocks": stocks,
            "total": len(stocks),
            "available_tags": available_tags
        })

    except Exception as e:
        logger.error(f"Error fetching stocks: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<symbol>', methods=['GET'])
def get_stock(symbol):
    """Get single stock with full details."""
    try:
        stock = current_app.stock_service.get_stock_with_details(symbol, include_price=True)

        if not stock:
            return jsonify({"error": f"Stock {symbol} not found"}), 404

        # Get alert history
        stock_obj = current_app.db_manager.get_stock_by_symbol(symbol)
        if stock_obj:
            alerts = current_app.db_manager.get_alert_history(stock_id=stock_obj.id, limit=10)
            stock["alert_history"] = [
                {
                    "id": alert.id,
                    "target_type": alert.target_type,
                    "current_price": alert.current_price,
                    "target_price": alert.target_price,
                    "alert_note": alert.alert_note,
                    "email_sent": alert.email_sent,
                    "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None
                }
                for alert in alerts
            ]

        return jsonify(stock)

    except Exception as e:
        logger.error(f"Error fetching stock {symbol}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('', methods=['POST'])
def create_stock():
    """Create a new stock with targets and tags.

    Body:
        {
            "symbol": "NVDA",
            "company_name": "NVIDIA Corporation",
            "targets": [
                {
                    "target_type": "Buy",
                    "target_price": 800.00,
                    "alert_note": "Good entry point",
                    "trim_percentage": null
                }
            ],
            "tags": ["tech", "AI"]
        }
    """
    try:
        data = request.get_json()

        if not data.get('symbol'):
            return jsonify({"error": "Symbol is required"}), 400

        result = current_app.stock_service.create_stock_with_targets(
            symbol=data['symbol'],
            company_name=data.get('company_name'),
            targets=data.get('targets', []),
            tags=data.get('tags', [])
        )

        # Fetch full details to return
        stock = current_app.stock_service.get_stock_with_details(data['symbol'])

        return jsonify(stock), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating stock: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>', methods=['PUT'])
def update_stock(stock_id):
    """Update stock information.

    Body:
        {
            "company_name": "Updated Name"
        }
    """
    try:
        data = request.get_json()

        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        success = current_app.db_manager.update_stock(
            stock_id=stock_id,
            company_name=data.get('company_name')
        )

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to update stock"}), 500

    except Exception as e:
        logger.error(f"Error updating stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    """Delete a stock and all related data."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        success = current_app.db_manager.delete_stock(stock_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to delete stock"}), 500

    except Exception as e:
        logger.error(f"Error deleting stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/fetch-info', methods=['POST'])
def fetch_stock_info(stock_id):
    """Fetch and update company information from yfinance.

    Body: (optional)
        {
            "force": true/false  # Force refetch even if name exists
        }
    """
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        data = request.get_json() or {}
        force = data.get('force', False)

        # Check if we need to fetch
        if stock.company_name and not force:
            return jsonify({
                "company_name": stock.company_name,
                "message": "Company name already exists"
            })

        # Fetch company info
        company_info = current_app.stock_fetcher.get_company_info(stock.symbol)

        if not company_info or not company_info.get('name'):
            return jsonify({"error": "Could not fetch company information"}), 404

        # Update stock with name and exchange
        company_name = company_info['name']
        exchange = company_info.get('exchange')
        current_app.db_manager.update_stock(
            stock_id,
            company_name=company_name,
            exchange=exchange
        )

        return jsonify({
            "company_name": company_name,
            "exchange": exchange,
            "success": True,
            "message": "Company information updated"
        })

    except Exception as e:
        logger.error(f"Error fetching info for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/targets', methods=['GET'])
def get_stock_targets(stock_id):
    """Get all targets for a stock."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        targets = current_app.db_manager.get_targets_for_stock(stock_id)

        return jsonify({
            "targets": [
                {
                    "id": t.id,
                    "target_type": t.target_type,
                    "target_price": t.target_price,
                    "trim_percentage": t.trim_percentage,
                    "alert_note": t.alert_note,
                    "is_active": t.is_active,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in targets
            ]
        })

    except Exception as e:
        logger.error(f"Error fetching targets for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/targets', methods=['POST'])
def add_stock_target(stock_id):
    """Add a new target to a stock.

    Body:
        {
            "target_type": "Sell",
            "target_price": 250.00,
            "alert_note": "Take profits",
            "trim_percentage": 25
        }
    """
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        data = request.get_json()

        if not data.get('target_type') or not data.get('target_price'):
            return jsonify({"error": "target_type and target_price are required"}), 400

        target_id = current_app.db_manager.create_target(
            stock_id=stock_id,
            target_type=data['target_type'],
            target_price=data['target_price'],
            trim_percentage=data.get('trim_percentage'),
            alert_note=data.get('alert_note')
        )

        return jsonify({"id": target_id, "success": True}), 201

    except Exception as e:
        logger.error(f"Error adding target to stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/tags', methods=['POST'])
def add_stock_tag(stock_id):
    """Add a tag to a stock.

    Body:
        {
            "tag_id": 3
        }
    """
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        data = request.get_json()
        tag_id = data.get('tag_id')

        if not tag_id:
            return jsonify({"error": "tag_id is required"}), 400

        success = current_app.db_manager.add_tag_to_stock(stock_id, tag_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Tag already added or doesn't exist"}), 400

    except Exception as e:
        logger.error(f"Error adding tag to stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_stock_tag(stock_id, tag_id):
    """Remove a tag from a stock."""
    try:
        success = current_app.db_manager.remove_tag_from_stock(stock_id, tag_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Tag not found on stock"}), 404

    except Exception as e:
        logger.error(f"Error removing tag from stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/timeframes', methods=['POST'])
def add_stock_timeframe(stock_id):
    """Add a timeframe to a stock.

    Body:
        {
            "timeframe_id": 1
        }
    """
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        data = request.get_json()
        timeframe_id = data.get('timeframe_id')

        if not timeframe_id:
            return jsonify({"error": "timeframe_id is required"}), 400

        success = current_app.db_manager.add_timeframe_to_stock(stock_id, timeframe_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Timeframe already added or doesn't exist"}), 400

    except Exception as e:
        logger.error(f"Error adding timeframe to stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/timeframes/<int:timeframe_id>', methods=['DELETE'])
def remove_stock_timeframe(stock_id, timeframe_id):
    """Remove a timeframe from a stock."""
    try:
        success = current_app.db_manager.remove_timeframe_from_stock(stock_id, timeframe_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Timeframe not found on stock"}), 404

    except Exception as e:
        logger.error(f"Error removing timeframe from stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/notes', methods=['GET'])
def get_stock_notes(stock_id):
    """Get all notes for a stock."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        limit = request.args.get('limit', type=int)
        notes = current_app.db_manager.get_notes_for_stock(stock_id, limit=limit)

        return jsonify({
            "notes": [
                {
                    "id": n.id,
                    "title": n.title,
                    "content": n.content,
                    "note_date": n.note_date.isoformat() if n.note_date else None,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                    "updated_at": n.updated_at.isoformat() if n.updated_at else None
                }
                for n in notes
            ]
        })

    except Exception as e:
        logger.error(f"Error fetching notes for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/notes', methods=['POST'])
def add_stock_note(stock_id):
    """Add a new note to a stock.

    Body:
        {
            "title": "Q4 Earnings",
            "content": "Strong results...",
            "note_date": "2026-02-07"
        }
    """
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        data = request.get_json()

        if not data.get('title') or not data.get('content') or not data.get('note_date'):
            return jsonify({"error": "title, content, and note_date are required"}), 400

        from datetime import date
        note_date = date.fromisoformat(data['note_date'])

        note_id = current_app.db_manager.create_note(
            stock_id=stock_id,
            title=data['title'],
            content=data['content'],
            note_date=note_date
        )

        return jsonify({"id": note_id, "success": True}), 201

    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {e}"}), 400
    except Exception as e:
        logger.error(f"Error adding note to stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/status', methods=['GET'])
def get_stock_status(stock_id):
    """Get stock status with current price and alert status."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        stock_data = current_app.stock_service.get_stock_status(stock.symbol)
        return jsonify(stock_data)

    except Exception as e:
        logger.error(f"Error fetching stock status {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/batch/update-exchanges', methods=['POST'])
def batch_update_exchanges():
    """Batch update exchange information for all stocks missing exchange data.

    This endpoint fetches exchange information from yfinance for all stocks
    that don't have an exchange set and updates them in the database.
    """
    try:
        # Get all stocks
        stocks = current_app.db_manager.get_all_stocks()

        if not stocks:
            return jsonify({
                "message": "No stocks found",
                "updated": 0,
                "skipped": 0,
                "failed": 0
            })

        updated = 0
        skipped = 0
        failed = 0
        results = []

        for stock in stocks:
            # Skip if exchange already set
            if stock.exchange:
                logger.debug(f"Skipping {stock.symbol} - exchange already set")
                skipped += 1
                continue

            try:
                # Fetch company info (includes exchange)
                company_info = current_app.stock_fetcher.get_company_info(stock.symbol)

                if company_info and company_info.get('exchange'):
                    exchange = company_info['exchange']
                    company_name = company_info.get('name') or stock.company_name

                    # Update stock
                    current_app.db_manager.update_stock(
                        stock.id,
                        company_name=company_name,
                        exchange=exchange
                    )

                    logger.info(f"Updated {stock.symbol}: {exchange}")
                    updated += 1
                    results.append({
                        "symbol": stock.symbol,
                        "exchange": exchange,
                        "status": "updated"
                    })
                else:
                    logger.warning(f"Could not fetch exchange for {stock.symbol}")
                    failed += 1
                    results.append({
                        "symbol": stock.symbol,
                        "status": "failed",
                        "reason": "No exchange data from yfinance"
                    })

                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error updating {stock.symbol}: {e}")
                failed += 1
                results.append({
                    "symbol": stock.symbol,
                    "status": "failed",
                    "reason": str(e)
                })

        return jsonify({
            "message": "Exchange update completed",
            "total": len(stocks),
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "results": results
        })

    except Exception as e:
        logger.error(f"Error in batch exchange update: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/holding', methods=['GET'])
def get_stock_holding(stock_id):
    """Get holding for a stock."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        holding = current_app.db_manager.get_holding_for_stock(stock_id)

        if holding:
            return jsonify({
                "holding": {
                    "id": holding.id,
                    "stock_id": holding.stock_id,
                    "shares": holding.shares,
                    "average_cost": holding.average_cost,
                    "created_at": holding.created_at.isoformat() if holding.created_at else None,
                    "updated_at": holding.updated_at.isoformat() if holding.updated_at else None
                }
            })
        else:
            return jsonify({"holding": None})

    except Exception as e:
        logger.error(f"Error fetching holding for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/holding', methods=['PUT'])
def update_stock_holding(stock_id):
    """Create or update holding for a stock."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        data = request.get_json()

        # Validate shares
        shares = data.get('shares')
        if shares is None or shares <= 0:
            return jsonify({"error": "shares is required and must be greater than 0"}), 400

        # Validate average_cost if provided
        average_cost = data.get('average_cost')
        if average_cost is not None and average_cost <= 0:
            return jsonify({"error": "average_cost must be greater than 0"}), 400

        holding_id = current_app.db_manager.create_or_update_holding(
            stock_id=stock_id,
            shares=shares,
            average_cost=average_cost
        )

        holding = current_app.db_manager.get_holding_for_stock(stock_id)

        return jsonify({
            "success": True,
            "holding": {
                "id": holding.id,
                "stock_id": holding.stock_id,
                "shares": holding.shares,
                "average_cost": holding.average_cost,
                "created_at": holding.created_at.isoformat() if holding.created_at else None,
                "updated_at": holding.updated_at.isoformat() if holding.updated_at else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Error updating holding for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/holding', methods=['DELETE'])
def delete_stock_holding(stock_id):
    """Delete holding for a stock."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        success = current_app.db_manager.delete_holding(stock_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No holding found for this stock"}), 404

    except Exception as e:
        logger.error(f"Error deleting holding for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
