"""Timeframe repository for investment timeframe operations."""

import sqlite3
from typing import List, Optional, Tuple, Dict
from datetime import datetime

from src.repositories.base_repository import BaseRepository
from src.models import Timeframe


class TimeframeRepository(BaseRepository):
    """Repository for investment timeframe database operations."""

    def get_all_timeframes(self) -> List[Tuple[Timeframe, int]]:
        """Get all investment timeframes with stock counts.

        Returns:
            List of (Timeframe, count) tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, COUNT(st.stock_id) as stock_count
                FROM investment_timeframes t
                LEFT JOIN stock_timeframes st ON t.id = st.timeframe_id
                GROUP BY t.id
                ORDER BY t.name
            """)

            results = []
            for row in cursor.fetchall():
                timeframe = Timeframe(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    description=row['description'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                results.append((timeframe, row['stock_count']))

            return results

    def get_timeframe_by_id(self, timeframe_id: int) -> Optional[Timeframe]:
        """Get timeframe by ID.

        Args:
            timeframe_id: Timeframe ID

        Returns:
            Timeframe object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM investment_timeframes WHERE id = ?", (timeframe_id,))
            row = cursor.fetchone()

            if row:
                return Timeframe(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    description=row['description'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
            return None

    def get_timeframes_for_stock(self, stock_id: int) -> List[Timeframe]:
        """Get all timeframes for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            List of Timeframe objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.* FROM investment_timeframes t
                JOIN stock_timeframes st ON t.id = st.timeframe_id
                WHERE st.stock_id = ?
                ORDER BY t.name
            """, (stock_id,))

            timeframes = []
            for row in cursor.fetchall():
                timeframes.append(Timeframe(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    description=row['description'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))

            return timeframes

    def get_timeframes_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, List[Timeframe]]:
        """Get timeframes for multiple stocks in a single query.

        Args:
            stock_ids: List of stock IDs

        Returns:
            Dictionary mapping stock_id to list of Timeframe objects
        """
        if not stock_ids:
            return {}

        with self.get_connection() as conn:
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(stock_ids))
            query = f"""
                SELECT st.stock_id, tf.*
                FROM stock_timeframes st
                JOIN investment_timeframes tf ON st.timeframe_id = tf.id
                WHERE st.stock_id IN ({placeholders})
            """

            cursor.execute(query, stock_ids)
            rows = cursor.fetchall()

            # Group timeframes by stock_id
            result = {stock_id: [] for stock_id in stock_ids}
            for row in rows:
                timeframe = Timeframe(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    description=row['description'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                result[row['stock_id']].append(timeframe)

            return result

    def add_timeframe_to_stock(self, stock_id: int, timeframe_id: int) -> bool:
        """Add a timeframe to a stock.

        Args:
            stock_id: Stock ID
            timeframe_id: Timeframe ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO stock_timeframes (stock_id, timeframe_id) VALUES (?, ?)", (stock_id, timeframe_id))
                return True
            except sqlite3.IntegrityError:
                return False  # Already exists

    def remove_timeframe_from_stock(self, stock_id: int, timeframe_id: int) -> bool:
        """Remove a timeframe from a stock.

        Args:
            stock_id: Stock ID
            timeframe_id: Timeframe ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stock_timeframes WHERE stock_id = ? AND timeframe_id = ?", (stock_id, timeframe_id))
            return cursor.rowcount > 0

    def create_timeframe(self, name: str, color: Optional[str] = None, description: Optional[str] = None) -> int:
        """Create a new investment timeframe.

        Args:
            name: Timeframe name
            color: Hex color code
            description: Description

        Returns:
            ID of created timeframe
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO investment_timeframes (name, color, description) VALUES (?, ?, ?)", (name, color, description))
            return cursor.lastrowid

    def update_timeframe(self, timeframe_id: int, name: Optional[str] = None, color: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Update a timeframe.

        Args:
            timeframe_id: Timeframe ID
            name: New name
            color: New color
            description: New description

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)

            if color is not None:
                updates.append("color = ?")
                params.append(color)

            if description is not None:
                updates.append("description = ?")
                params.append(description)

            if not updates:
                return False

            params.append(timeframe_id)
            query = f"UPDATE investment_timeframes SET {', '.join(updates)} WHERE id = ?"

            cursor.execute(query, params)
            return cursor.rowcount > 0

    def delete_timeframe(self, timeframe_id: int) -> bool:
        """Delete a timeframe.

        Args:
            timeframe_id: Timeframe ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM investment_timeframes WHERE id = ?", (timeframe_id,))
            return cursor.rowcount > 0
