"""Note repository for note operations."""

from typing import List, Optional, Dict
from datetime import datetime, date

from src.repositories.base_repository import BaseRepository
from src.models import Note


class NoteRepository(BaseRepository):
    """Repository for note database operations."""

    def create_note(self, stock_id: int, title: str, content: str, note_date: date) -> int:
        """Create a new note.

        Args:
            stock_id: Stock ID
            title: Note title
            content: Note content
            note_date: Date of the note

        Returns:
            ID of created note
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (stock_id, title, content, note_date) VALUES (?, ?, ?, ?)",
                (stock_id, title, content, note_date.isoformat())
            )
            return cursor.lastrowid

    def get_notes_for_stock(self, stock_id: int, limit: Optional[int] = None) -> List[Note]:
        """Get all notes for a stock.

        Args:
            stock_id: Stock ID
            limit: Optional limit on number of notes

        Returns:
            List of Note objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM notes WHERE stock_id = ? ORDER BY note_date DESC"
            params = [stock_id]

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)

            notes = []
            for row in cursor.fetchall():
                notes.append(Note(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    title=row['title'],
                    content=row['content'],
                    note_date=date.fromisoformat(row['note_date']) if row['note_date'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                ))

            return notes

    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Get a note by ID.

        Args:
            note_id: Note ID

        Returns:
            Note object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()

            if row:
                return Note(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    title=row['title'],
                    content=row['content'],
                    note_date=date.fromisoformat(row['note_date']) if row['note_date'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
            return None

    def get_notes_count_for_stock(self, stock_id: int) -> int:
        """Get count of notes for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            Count of notes
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM notes WHERE stock_id = ?", (stock_id,))
            row = cursor.fetchone()
            return row['count'] if row else 0

    def get_notes_count_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, int]:
        """Get notes count for multiple stocks in a single query.

        Args:
            stock_ids: List of stock IDs

        Returns:
            Dictionary mapping stock_id to notes count
        """
        if not stock_ids:
            return {}

        with self.get_connection() as conn:
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(stock_ids))
            query = f"""
                SELECT stock_id, COUNT(*) as count
                FROM notes
                WHERE stock_id IN ({placeholders})
                GROUP BY stock_id
            """

            cursor.execute(query, stock_ids)
            rows = cursor.fetchall()

            # Initialize all stock_ids with 0, then update with actual counts
            result = {stock_id: 0 for stock_id in stock_ids}
            for row in rows:
                result[row['stock_id']] = row['count']

            return result

    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> bool:
        """Update a note.

        Args:
            note_id: Note ID
            title: New title
            content: New content

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if title is not None:
                updates.append("title = ?")
                params.append(title)

            if content is not None:
                updates.append("content = ?")
                params.append(content)

            if not updates:
                return False

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(note_id)

            query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"

            cursor.execute(query, params)
            return cursor.rowcount > 0

    def delete_note(self, note_id: int) -> bool:
        """Delete a note.

        Args:
            note_id: Note ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return cursor.rowcount > 0
