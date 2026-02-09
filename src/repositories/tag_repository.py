"""Tag repository for tag operations."""

import sqlite3
from typing import List, Optional, Tuple, Dict
from datetime import datetime

from src.repositories.base_repository import BaseRepository
from src.models import Tag


class TagRepository(BaseRepository):
    """Repository for tag database operations."""

    def create_tag(self, name: str, color: Optional[str] = None) -> int:
        """Create a new tag.

        Args:
            name: Tag name
            color: Hex color code

        Returns:
            ID of created tag
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tags (name, color) VALUES (?, ?)", (name.lower(), color))
            return cursor.lastrowid

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get tag by name.

        Args:
            name: Tag name

        Returns:
            Tag object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tags WHERE name = ?", (name.lower(),))
            row = cursor.fetchone()

            if row:
                return Tag(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
            return None

    def get_all_tags(self) -> List[Tuple[Tag, int]]:
        """Get all tags with stock counts.

        Returns:
            List of (Tag, count) tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, COUNT(st.stock_id) as stock_count
                FROM tags t
                LEFT JOIN stock_tags st ON t.id = st.tag_id
                GROUP BY t.id
                ORDER BY t.name
            """)

            results = []
            for row in cursor.fetchall():
                tag = Tag(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                results.append((tag, row['stock_count']))

            return results

    def get_tags_for_stock(self, stock_id: int) -> List[Tag]:
        """Get all tags for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            List of Tag objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.* FROM tags t
                JOIN stock_tags st ON t.id = st.tag_id
                WHERE st.stock_id = ?
                ORDER BY t.name
            """, (stock_id,))

            tags = []
            for row in cursor.fetchall():
                tags.append(Tag(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))

            return tags

    def get_tags_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, List[Tag]]:
        """Get tags for multiple stocks in a single query.

        Args:
            stock_ids: List of stock IDs

        Returns:
            Dictionary mapping stock_id to list of Tag objects
        """
        if not stock_ids:
            return {}

        with self.get_connection() as conn:
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(stock_ids))
            query = f"""
                SELECT st.stock_id, t.*
                FROM stock_tags st
                JOIN tags t ON st.tag_id = t.id
                WHERE st.stock_id IN ({placeholders})
            """

            cursor.execute(query, stock_ids)
            rows = cursor.fetchall()

            # Group tags by stock_id
            result = {stock_id: [] for stock_id in stock_ids}
            for row in rows:
                tag = Tag(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                result[row['stock_id']].append(tag)

            return result

    def add_tag_to_stock(self, stock_id: int, tag_id: int) -> bool:
        """Add a tag to a stock.

        Args:
            stock_id: Stock ID
            tag_id: Tag ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO stock_tags (stock_id, tag_id) VALUES (?, ?)", (stock_id, tag_id))
                return True
            except sqlite3.IntegrityError:
                return False  # Already exists

    def remove_tag_from_stock(self, stock_id: int, tag_id: int) -> bool:
        """Remove a tag from a stock.

        Args:
            stock_id: Stock ID
            tag_id: Tag ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stock_tags WHERE stock_id = ? AND tag_id = ?", (stock_id, tag_id))
            return cursor.rowcount > 0

    def update_tag(self, tag_id: int, name: Optional[str] = None, color: Optional[str] = None) -> bool:
        """Update a tag.

        Args:
            tag_id: Tag ID
            name: New name
            color: New color

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name.lower())

            if color is not None:
                updates.append("color = ?")
                params.append(color)

            if not updates:
                return False

            params.append(tag_id)
            query = f"UPDATE tags SET {', '.join(updates)} WHERE id = ?"

            cursor.execute(query, params)
            return cursor.rowcount > 0

    def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag.

        Args:
            tag_id: Tag ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
            return cursor.rowcount > 0
