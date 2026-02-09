"""Alert repository for alert history operations."""

from typing import List, Optional, Dict
from datetime import datetime

from src.repositories.base_repository import BaseRepository
from src.models import AlertHistory


class AlertRepository(BaseRepository):
    """Repository for alert history database operations."""

    def create_alert_history(self, stock_id: int, target_id: int, current_price: float,
                            target_price: float, target_type: str, alert_note: Optional[str] = None,
                            email_sent: bool = False) -> int:
        """Create an alert history entry.

        Args:
            stock_id: Stock ID
            target_id: Target ID
            current_price: Current price when alert triggered
            target_price: Target price
            target_type: Type of target
            alert_note: Alert note
            email_sent: Whether email was sent

        Returns:
            ID of created alert history entry
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO alert_history
                   (stock_id, target_id, current_price, target_price, target_type, alert_note, email_sent)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (stock_id, target_id, current_price, target_price, target_type, alert_note, email_sent)
            )
            return cursor.lastrowid

    def get_alert_history(self, stock_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[AlertHistory]:
        """Get alert history.

        Args:
            stock_id: Optional stock ID filter
            limit: Number of records to return
            offset: Offset for pagination

        Returns:
            List of AlertHistory objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if stock_id:
                query = "SELECT * FROM alert_history WHERE stock_id = ? ORDER BY triggered_at DESC LIMIT ? OFFSET ?"
                params = [stock_id, limit, offset]
            else:
                query = "SELECT * FROM alert_history ORDER BY triggered_at DESC LIMIT ? OFFSET ?"
                params = [limit, offset]

            cursor.execute(query, params)

            alerts = []
            for row in cursor.fetchall():
                alerts.append(AlertHistory(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    target_id=row['target_id'],
                    current_price=row['current_price'],
                    target_price=row['target_price'],
                    target_type=row['target_type'],
                    alert_note=row['alert_note'],
                    email_sent=bool(row['email_sent']),
                    triggered_at=datetime.fromisoformat(row['triggered_at']) if row['triggered_at'] else None
                ))

            return alerts

    def get_latest_alert_for_stock(self, stock_id: int) -> Optional[AlertHistory]:
        """Get most recent alert for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            AlertHistory object or None
        """
        alerts = self.get_alert_history(stock_id=stock_id, limit=1)
        return alerts[0] if alerts else None

    def get_latest_alert_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, Optional[AlertHistory]]:
        """Get latest alert for multiple stocks in a single query.

        Args:
            stock_ids: List of stock IDs

        Returns:
            Dictionary mapping stock_id to latest AlertHistory object (or None)
        """
        if not stock_ids:
            return {}

        with self.get_connection() as conn:
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(stock_ids))
            query = f"""
                SELECT ah1.*
                FROM alert_history ah1
                INNER JOIN (
                    SELECT stock_id, MAX(triggered_at) as max_triggered
                    FROM alert_history
                    WHERE stock_id IN ({placeholders})
                    GROUP BY stock_id
                ) ah2 ON ah1.stock_id = ah2.stock_id
                    AND ah1.triggered_at = ah2.max_triggered
            """

            cursor.execute(query, stock_ids)
            rows = cursor.fetchall()

            # Initialize all stock_ids with None
            result = {stock_id: None for stock_id in stock_ids}
            for row in rows:
                alert = AlertHistory(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    target_id=row['target_id'],
                    current_price=row['current_price'],
                    target_price=row['target_price'],
                    target_type=row['target_type'],
                    alert_note=row['alert_note'],
                    email_sent=bool(row['email_sent']),
                    triggered_at=datetime.fromisoformat(row['triggered_at']) if row['triggered_at'] else None
                )
                result[alert.stock_id] = alert

            return result

    def delete_alert_history(self, alert_id: int) -> bool:
        """Delete an alert history entry.

        Args:
            alert_id: Alert history ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alert_history WHERE id = ?", (alert_id,))
            return cursor.rowcount > 0
