"""Holding repository for stock holding CRUD operations."""

from typing import Optional, Dict, List
from datetime import datetime

from src.repositories.base_repository import BaseRepository
from src.models import Holding


class HoldingRepository(BaseRepository):
    """Repository for stock holding database operations."""

    def create_or_update_holding(
        self,
        stock_id: int,
        shares: float,
        average_cost: Optional[float] = None
    ) -> int:
        """Create or update a stock holding (upsert).

        Args:
            stock_id: Stock ID
            shares: Number of shares
            average_cost: Average cost per share (optional)

        Returns:
            ID of created/updated holding
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stock_holdings (stock_id, shares, average_cost)
                VALUES (?, ?, ?)
                ON CONFLICT(stock_id) DO UPDATE SET
                    shares = excluded.shares,
                    average_cost = excluded.average_cost,
                    updated_at = CURRENT_TIMESTAMP
            """, (stock_id, shares, average_cost))

            # Get the ID (either new or existing)
            cursor.execute(
                "SELECT id FROM stock_holdings WHERE stock_id = ?",
                (stock_id,)
            )
            return cursor.fetchone()[0]

    def get_holding_for_stock(self, stock_id: int) -> Optional[Holding]:
        """Get holding for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            Holding object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM stock_holdings WHERE stock_id = ?",
                (stock_id,)
            )
            row = cursor.fetchone()

            if row:
                return Holding(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    shares=float(row['shares']),
                    average_cost=float(row['average_cost']) if row['average_cost'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
            return None

    def get_holdings_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, Holding]:
        """Get holdings for multiple stocks in a single query.

        Args:
            stock_ids: List of stock IDs

        Returns:
            Dictionary mapping stock_id to Holding
        """
        if not stock_ids:
            return {}

        with self.get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(stock_ids))
            cursor.execute(
                f"SELECT * FROM stock_holdings WHERE stock_id IN ({placeholders})",
                stock_ids
            )

            holdings = {}
            for row in cursor.fetchall():
                holding = Holding(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    shares=float(row['shares']),
                    average_cost=float(row['average_cost']) if row['average_cost'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
                holdings[row['stock_id']] = holding

            return holdings

    def delete_holding(self, stock_id: int) -> bool:
        """Delete a holding for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            True if deleted, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM stock_holdings WHERE stock_id = ?",
                (stock_id,)
            )
            return cursor.rowcount > 0

    def get_portfolio_summary(self) -> Dict[str, float]:
        """Get total portfolio summary (all stocks with holdings).

        Returns:
            Dictionary with total_shares, total_cost_basis
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    COUNT(*) as positions,
                    SUM(shares * COALESCE(average_cost, 0)) as total_cost_basis
                FROM stock_holdings
            """)
            row = cursor.fetchone()

            return {
                "positions": row['positions'] or 0,
                "total_cost_basis": float(row['total_cost_basis']) if row['total_cost_basis'] else 0.0
            }
