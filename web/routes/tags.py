"""Tags API routes."""

from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('', methods=['GET'])
def get_tags():
    """Get all tags with stock counts."""
    try:
        tags_with_counts = current_app.db_manager.get_all_tags()

        return jsonify({
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "color": tag.color,
                    "stock_count": count,
                    "created_at": tag.created_at.isoformat() if tag.created_at else None
                }
                for tag, count in tags_with_counts
            ]
        })

    except Exception as e:
        logger.error(f"Error fetching tags: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@tags_bp.route('', methods=['POST'])
def create_tag():
    """Create a new tag.

    Body:
        {
            "name": "fintech",
            "color": "#8B5CF6"
        }
    """
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({"error": "name is required"}), 400

        # Check if tag already exists
        existing_tag = current_app.db_manager.get_tag_by_name(data['name'])
        if existing_tag:
            return jsonify({"error": f"Tag '{data['name']}' already exists"}), 400

        tag_id = current_app.db_manager.create_tag(
            name=data['name'],
            color=data.get('color')
        )

        tag = current_app.db_manager.get_tag_by_name(data['name'])

        return jsonify({
            "id": tag.id,
            "name": tag.name,
            "color": tag.color
        }), 201

    except Exception as e:
        logger.error(f"Error creating tag: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@tags_bp.route('/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """Update a tag.

    Body:
        {
            "name": "financial-tech",
            "color": "#6366F1"
        }
    """
    try:
        data = request.get_json()

        success = current_app.db_manager.update_tag(
            tag_id=tag_id,
            name=data.get('name'),
            color=data.get('color')
        )

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Tag not found"}), 404

    except Exception as e:
        logger.error(f"Error updating tag {tag_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@tags_bp.route('/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """Delete a tag (removes from all stocks)."""
    try:
        success = current_app.db_manager.delete_tag(tag_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Tag not found"}), 404

    except Exception as e:
        logger.error(f"Error deleting tag {tag_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
