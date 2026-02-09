"""Target repository for price target operations."""

from typing import List, Optional, Tuple, Dict
from datetime import datetime

from src.repositories.base_repository import BaseRepository
from src.models import Target, Stock


class TargetRepository(BaseRepository):
    """Repository for target database operations."""

    def create_target(self, stock_id: int, target_type: str, target_price: float,
                     trim_percentage: Optional[float] = None, alert_note: Optional[str] = None) -> int:
        """Create a new price target.

        Args:
            stock_id: Stock ID
            target_type: Type of target (Buy, Sell, DCA, Trim)
            target_price: Target price
            trim_percentage: Percentage to trim (for Trim type)
            alert_note: Note to include in alert email

        Returns:
            ID of created target
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO targets (stock_id, target_type, target_price, trim_percentage, alert_note)
                   VALUES (?, ?, ?, ?, ?)""",
                (stock_id, target_type, target_price, trim_percentage, alert_note)
            )
            return cursor.lastrowid

    def get_targets_for_stock(self, stock_id: int, active_only: bool = False) -> List[Target]:
        """Get all targets for a stock.

        Args:
            stock_id: Stock ID
            active_only: Only return active targets

        Returns:
            List of Target objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM targets WHERE stock_id = ?"
            params = [stock_id]

            if active_only:
                query += " AND is_active = 1"

            query += " ORDER BY target_price"
            cursor.execute(query, params)

            targets = []
            for row in cursor.fetchall():
                targets.append(Target(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    target_type=row['target_type'],
                    target_price=row['target_price'],
                    trim_percentage=row['trim_percentage'],
                    alert_note=row['alert_note'],
                    is_active=bool(row['is_active']),
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))

            return targets

    def get_targets_for_stocks_batch(self, stock_ids: List[int], active_only: bool = False) -> Dict[int, List[Target]]:
        """Get targets for multiple stocks in a single query.

        Args:
            stock_ids: List of stock IDs
            active_only: Only return active targets

        Returns:
            Dictionary mapping stock_id to list of Target objects
        """
        if not stock_ids:
            return {}

        with self.get_connection() as conn:
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(stock_ids))
            query = f"SELECT * FROM targets WHERE stock_id IN ({placeholders})"
            params = stock_ids

            if active_only:
                query += " AND is_active = 1"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Group targets by stock_id
            result = {stock_id: [] for stock_id in stock_ids}
            for row in rows:
                target = Target(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    target_type=row['target_type'],
                    target_price=row['target_price'],
                    trim_percentage=row['trim_percentage'],
                    alert_note=row['alert_note'],
                    is_active=bool(row['is_active']),
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                result[target.stock_id].append(target)

            return result

    def get_all_active_targets(self) -> List[Tuple[Stock, Target]]:
        """Get all active targets with their stocks.

        Returns:
            List of (Stock, Target) tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stocks.*, targets.* FROM stocks
                JOIN targets ON stocks.id = targets.stock_id
                WHERE targets.is_active = 1
                ORDER BY stocks.symbol, targets.target_price
            """)

            results = []
            for row in cursor.fetchall():
                stock = Stock(
                    id=row['id'],
                    symbol=row['symbol'],
                    company_name=row['company_name'],
                    exchange=row['exchange'] if 'exchange' in row.keys() else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )

                # Column indices shift after stocks columns (id, symbol, company_name, exchange, created_at, updated_at = 6 columns)
                target = Target(
                    id=row[6],
                    stock_id=row[7],
                    target_type=row[8],
                    target_price=row[9],
                    trim_percentage=row[10],
                    alert_note=row[11],
                    is_active=bool(row[12]),
                    created_at=datetime.fromisoformat(row[13]) if row[13] else None
                )

                results.append((stock, target))

            return results

    def update_target(self, target_id: int, target_price: Optional[float] = None,
                     alert_note: Optional[str] = None, trim_percentage: Optional[float] = None) -> bool:
        """Update a target.

        Args:
            target_id: Target ID
            target_price: New target price
            alert_note: New alert note
            trim_percentage: New trim percentage

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if target_price is not None:
                updates.append("target_price = ?")
                params.append(target_price)

            if alert_note is not None:
                updates.append("alert_note = ?")
                params.append(alert_note)

            if trim_percentage is not None:
                updates.append("trim_percentage = ?")
                params.append(trim_percentage)

            if not updates:
                return False

            params.append(target_id)
            query = f"UPDATE targets SET {', '.join(updates)} WHERE id = ?"

            cursor.execute(query, params)
            return cursor.rowcount > 0

    def toggle_target_active(self, target_id: int) -> bool:
        """Toggle target active status.

        Args:
            target_id: Target ID

        Returns:
            New active status
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT is_active FROM targets WHERE id = ?", (target_id,))
            row = cursor.fetchone()

            if row:
                new_status = not bool(row['is_active'])
                cursor.execute("UPDATE targets SET is_active = ? WHERE id = ?", (new_status, target_id))
                return new_status

            return False

    def delete_target(self, target_id: int) -> bool:
        """Delete a target.

        Args:
            target_id: Target ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM targets WHERE id = ?", (target_id,))
            return cursor.rowcount > 0
