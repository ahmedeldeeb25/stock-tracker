"""Stock repository for stock CRUD operations."""

from typing import List, Optional
from datetime import datetime

from src.repositories.base_repository import BaseRepository
from src.models import Stock


class StockRepository(BaseRepository):
    """Repository for stock database operations."""

    def create_stock(self, symbol: str, company_name: Optional[str] = None, exchange: Optional[str] = None) -> int:
        """Create a new stock.

        Args:
            symbol: Stock ticker symbol
            company_name: Optional company name
            exchange: Optional exchange where stock is traded (e.g., 'NYSE', 'NASDAQ')

        Returns:
            ID of created stock
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stocks (symbol, company_name, exchange) VALUES (?, ?, ?)",
                (symbol.upper(), company_name, exchange)
            )
            return cursor.lastrowid

    def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        """Get stock by symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Stock object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stocks WHERE symbol = ?", (symbol.upper(),))
            row = cursor.fetchone()

            if row:
                return Stock(
                    id=row['id'],
                    symbol=row['symbol'],
                    company_name=row['company_name'],
                    exchange=row['exchange'] if 'exchange' in row.keys() else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
            return None

    def get_stock_by_id(self, stock_id: int) -> Optional[Stock]:
        """Get stock by ID.

        Args:
            stock_id: Stock ID

        Returns:
            Stock object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stocks WHERE id = ?", (stock_id,))
            row = cursor.fetchone()

            if row:
                return Stock(
                    id=row['id'],
                    symbol=row['symbol'],
                    company_name=row['company_name'],
                    exchange=row['exchange'] if 'exchange' in row.keys() else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
            return None

    def get_all_stocks(self, tag: Optional[str] = None, search: Optional[str] = None) -> List[Stock]:
        """Get all stocks with optional filters.

        Args:
            tag: Filter by tag name
            search: Search in symbol or company name

        Returns:
            List of Stock objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if tag:
                query = """
                    SELECT DISTINCT stocks.* FROM stocks
                    JOIN stock_tags ON stocks.id = stock_tags.stock_id
                    JOIN tags ON stock_tags.tag_id = tags.id
                    WHERE tags.name = ?
                """
                params = [tag]
            else:
                query = "SELECT * FROM stocks"
                params = []

            if search:
                if tag:
                    query += " AND (stocks.symbol LIKE ? OR stocks.company_name LIKE ?)"
                else:
                    query += " WHERE symbol LIKE ? OR company_name LIKE ?"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])

            query += " ORDER BY stocks.symbol" if tag else " ORDER BY symbol"
            cursor.execute(query, params)

            stocks = []
            for row in cursor.fetchall():
                stocks.append(Stock(
                    id=row['id'],
                    symbol=row['symbol'],
                    company_name=row['company_name'],
                    exchange=row['exchange'] if 'exchange' in row.keys() else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                ))

            return stocks

    def update_stock(self, stock_id: int, company_name: Optional[str] = None, exchange: Optional[str] = None) -> bool:
        """Update stock information.

        Args:
            stock_id: Stock ID
            company_name: New company name
            exchange: New exchange

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic update query based on provided fields
            updates = []
            params = []

            if company_name is not None:
                updates.append("company_name = ?")
                params.append(company_name)

            if exchange is not None:
                updates.append("exchange = ?")
                params.append(exchange)

            if not updates:
                return True  # Nothing to update

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(stock_id)

            query = f"UPDATE stocks SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            return cursor.rowcount > 0

    def delete_stock(self, stock_id: int) -> bool:
        """Delete a stock and all related data.

        Args:
            stock_id: Stock ID

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stocks WHERE id = ?", (stock_id,))
            return cursor.rowcount > 0
