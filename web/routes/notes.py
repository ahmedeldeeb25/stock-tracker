"""Notes API routes."""

from flask import Blueprint, request, jsonify, current_app
from datetime import date
import logging

logger = logging.getLogger(__name__)

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a single note."""
    try:
        note = current_app.db_manager.get_note_by_id(note_id)

        if not note:
            return jsonify({"error": "Note not found"}), 404

        return jsonify({
            "id": note.id,
            "stock_id": note.stock_id,
            "title": note.title,
            "content": note.content,
            "note_date": note.note_date.isoformat() if note.note_date else None,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None
        })

    except Exception as e:
        logger.error(f"Error fetching note {note_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note.

    Body:
        {
            "title": "Updated title",
            "content": "Updated content"
        }
    """
    try:
        data = request.get_json()

        success = current_app.db_manager.update_note(
            note_id=note_id,
            title=data.get('title'),
            content=data.get('content')
        )

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Note not found"}), 404

    except Exception as e:
        logger.error(f"Error updating note {note_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note."""
    try:
        success = current_app.db_manager.delete_note(note_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Note not found"}), 404

    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
