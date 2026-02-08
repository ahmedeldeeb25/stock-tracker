"""Investment Timeframes API routes."""

from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

timeframes_bp = Blueprint('timeframes', __name__)


@timeframes_bp.route('', methods=['GET'])
def get_timeframes():
    """Get all investment timeframes with stock counts."""
    try:
        timeframes_with_counts = current_app.db_manager.get_all_timeframes()

        timeframes = [
            {
                "id": tf.id,
                "name": tf.name,
                "color": tf.color,
                "description": tf.description,
                "stock_count": count,
                "created_at": tf.created_at.isoformat() if tf.created_at else None
            }
            for tf, count in timeframes_with_counts
        ]

        return jsonify({"timeframes": timeframes})

    except Exception as e:
        logger.error(f"Error fetching timeframes: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@timeframes_bp.route('/<int:timeframe_id>', methods=['GET'])
def get_timeframe(timeframe_id):
    """Get a single timeframe by ID."""
    try:
        timeframe = current_app.db_manager.get_timeframe_by_id(timeframe_id)

        if not timeframe:
            return jsonify({"error": "Timeframe not found"}), 404

        return jsonify({
            "id": timeframe.id,
            "name": timeframe.name,
            "color": timeframe.color,
            "description": timeframe.description,
            "created_at": timeframe.created_at.isoformat() if timeframe.created_at else None
        })

    except Exception as e:
        logger.error(f"Error fetching timeframe {timeframe_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@timeframes_bp.route('', methods=['POST'])
def create_timeframe():
    """Create a new investment timeframe.

    Body:
        {
            "name": "Long Term",
            "color": "#10B981",
            "description": "Hold for 1+ years"
        }
    """
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({"error": "Name is required"}), 400

        timeframe_id = current_app.db_manager.create_timeframe(
            name=data['name'],
            color=data.get('color'),
            description=data.get('description')
        )

        return jsonify({"id": timeframe_id, "success": True}), 201

    except Exception as e:
        logger.error(f"Error creating timeframe: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@timeframes_bp.route('/<int:timeframe_id>', methods=['PUT'])
def update_timeframe(timeframe_id):
    """Update an investment timeframe.

    Body:
        {
            "name": "Updated Name",
            "color": "#10B981",
            "description": "Updated description"
        }
    """
    try:
        timeframe = current_app.db_manager.get_timeframe_by_id(timeframe_id)

        if not timeframe:
            return jsonify({"error": "Timeframe not found"}), 404

        data = request.get_json()

        success = current_app.db_manager.update_timeframe(
            timeframe_id=timeframe_id,
            name=data.get('name'),
            color=data.get('color'),
            description=data.get('description')
        )

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to update timeframe"}), 500

    except Exception as e:
        logger.error(f"Error updating timeframe {timeframe_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@timeframes_bp.route('/<int:timeframe_id>', methods=['DELETE'])
def delete_timeframe(timeframe_id):
    """Delete an investment timeframe."""
    try:
        timeframe = current_app.db_manager.get_timeframe_by_id(timeframe_id)

        if not timeframe:
            return jsonify({"error": "Timeframe not found"}), 404

        success = current_app.db_manager.delete_timeframe(timeframe_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to delete timeframe"}), 500

    except Exception as e:
        logger.error(f"Error deleting timeframe {timeframe_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
