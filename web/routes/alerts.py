"""Alerts API routes."""

from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('', methods=['GET'])
def get_alerts():
    """Get alert history.

    Query Params:
        stock_id: Filter by stock ID
        limit: Number of records (default: 50)
        offset: Offset for pagination (default: 0)
    """
    try:
        stock_id = request.args.get('stock_id', type=int)
        limit = request.args.get('limit', default=50, type=int)
        offset = request.args.get('offset', default=0, type=int)

        alerts = current_app.db_manager.get_alert_history(
            stock_id=stock_id,
            limit=limit,
            offset=offset
        )

        # Get stock symbols for the alerts
        alert_list = []
        for alert in alerts:
            stock = current_app.db_manager.get_stock_by_id(alert.stock_id)

            alert_list.append({
                "id": alert.id,
                "symbol": stock.symbol if stock else "Unknown",
                "target_type": alert.target_type,
                "current_price": alert.current_price,
                "target_price": alert.target_price,
                "alert_note": alert.alert_note,
                "email_sent": alert.email_sent,
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None
            })

        return jsonify({
            "alerts": alert_list,
            "total": len(alert_list),
            "limit": limit,
            "offset": offset
        })

    except Exception as e:
        logger.error(f"Error fetching alerts: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@alerts_bp.route('/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert from history."""
    try:
        success = current_app.db_manager.delete_alert_history(alert_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Alert not found"}), 404

    except Exception as e:
        logger.error(f"Error deleting alert {alert_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
