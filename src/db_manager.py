"""Database manager for SQLite operations."""

import sqlite3
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from contextlib import contextmanager

from src.models import Stock, Target, Tag, Note, AlertHistory, Timeframe

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages all database operations for the stock tracker."""

    def __init__(self, db_path: str = "stock_tracker.db"):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Stocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol VARCHAR(10) NOT NULL UNIQUE,
                    company_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol)")

            # Targets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_id INTEGER NOT NULL,
                    target_type VARCHAR(10) NOT NULL,
                    target_price DECIMAL(10, 2) NOT NULL,
                    trim_percentage DECIMAL(5, 2),
                    alert_note TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_targets_stock_id ON targets(stock_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_targets_active ON targets(is_active)")

            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    color VARCHAR(7),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")

            # Stock_tags junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_tags (
                    stock_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (stock_id, tag_id),
                    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            # Notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_id INTEGER NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    note_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_stock_id ON notes(stock_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_date ON notes(note_date)")

            # Alert history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    current_price DECIMAL(10, 2) NOT NULL,
                    target_price DECIMAL(10, 2) NOT NULL,
                    target_type VARCHAR(10) NOT NULL,
                    alert_note TEXT,
                    email_sent BOOLEAN DEFAULT 0,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
                    FOREIGN KEY (target_id) REFERENCES targets(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alert_history_stock_id ON alert_history(stock_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alert_history_triggered_at ON alert_history(triggered_at)")

            # Investment timeframes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_timeframes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    color VARCHAR(7),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeframes_name ON investment_timeframes(name)")

            # Stock_timeframes junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_timeframes (
                    stock_id INTEGER NOT NULL,
                    timeframe_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (stock_id, timeframe_id),
                    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
                    FOREIGN KEY (timeframe_id) REFERENCES investment_timeframes(id) ON DELETE CASCADE
                )
            """)

            # Insert default timeframes if not exists
            cursor.execute("SELECT COUNT(*) FROM investment_timeframes")
            if cursor.fetchone()[0] == 0:
                default_timeframes = [
                    ('Long Term', '#10B981', 'Hold for 1+ years'),
                    ('Medium Term', '#3B82F6', 'Hold for 3-12 months'),
                    ('Short Term', '#F59E0B', 'Hold for weeks to 3 months'),
                    ('Swing Trade', '#8B5CF6', 'Hold for days to weeks'),
                    ('Day Trade', '#EF4444', 'Intraday positions')
                ]
                cursor.executemany(
                    "INSERT INTO investment_timeframes (name, color, description) VALUES (?, ?, ?)",
                    default_timeframes
                )
                logger.info("Default investment timeframes created")

            logger.info("Database initialized successfully")

    # ==================== STOCK OPERATIONS ====================

    def create_stock(self, symbol: str, company_name: Optional[str] = None) -> int:
        """Create a new stock.

        Args:
            symbol: Stock ticker symbol
            company_name: Optional company name

        Returns:
            ID of created stock
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stocks (symbol, company_name) VALUES (?, ?)",
                (symbol.upper(), company_name)
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
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                ))

            return stocks

    def update_stock(self, stock_id: int, company_name: Optional[str] = None) -> bool:
        """Update stock information.

        Args:
            stock_id: Stock ID
            company_name: New company name

        Returns:
            True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE stocks SET company_name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (company_name, stock_id)
            )
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

    # ==================== TARGET OPERATIONS ====================

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
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )

                # Column indices shift after stocks columns (id, symbol, company_name, created_at, updated_at = 5 columns)
                target = Target(
                    id=row[5],
                    stock_id=row[6],
                    target_type=row[7],
                    target_price=row[8],
                    trim_percentage=row[9],
                    alert_note=row[10],
                    is_active=bool(row[11]),
                    created_at=datetime.fromisoformat(row[12]) if row[12] else None
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

    # ==================== TAG OPERATIONS ====================

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

    # ==================== TIMEFRAME OPERATIONS ====================

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

    # ==================== NOTE OPERATIONS ====================

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

    # ==================== ALERT HISTORY OPERATIONS ====================

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
