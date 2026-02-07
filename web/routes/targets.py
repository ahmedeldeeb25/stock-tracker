"""Targets API routes."""

from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

targets_bp = Blueprint('targets', __name__)


@targets_bp.route('/<int:target_id>', methods=['PUT'])
def update_target(target_id):
    """Update a target.

    Body:
        {
            "target_price": 260.00,
            "alert_note": "Updated note",
            "trim_percentage": 30
        }
    """
    try:
        data = request.get_json()

        success = current_app.db_manager.update_target(
            target_id=target_id,
            target_price=data.get('target_price'),
            alert_note=data.get('alert_note'),
            trim_percentage=data.get('trim_percentage')
        )

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Target not found"}), 404

    except Exception as e:
        logger.error(f"Error updating target {target_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@targets_bp.route('/<int:target_id>', methods=['DELETE'])
def delete_target(target_id):
    """Delete a target."""
    try:
        success = current_app.db_manager.delete_target(target_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Target not found"}), 404

    except Exception as e:
        logger.error(f"Error deleting target {target_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@targets_bp.route('/<int:target_id>/toggle', methods=['PATCH'])
def toggle_target(target_id):
    """Toggle target active status."""
    try:
        new_status = current_app.db_manager.toggle_target_active(target_id)

        return jsonify({"is_active": new_status, "success": True})

    except Exception as e:
        logger.error(f"Error toggling target {target_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
