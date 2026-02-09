"""Database manager for SQLite operations.

This module provides a facade over domain-specific repositories,
maintaining backward compatibility while improving code organization.
"""

import sqlite3
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from contextlib import contextmanager

from src.models import Stock, Target, Tag, Note, AlertHistory, Timeframe
from src.repositories import (
    StockRepository,
    TargetRepository,
    TagRepository,
    NoteRepository,
    AlertRepository,
    TimeframeRepository
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Facade for database operations - delegates to domain repositories.

    This class maintains backward compatibility by delegating all operations
    to specialized repository classes while preserving the original API.
    """

    def __init__(self, db_path: str = "stock_tracker.db"):
        """Initialize database manager with domain repositories.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Initialize database schema first
        self.init_database()

        # Initialize domain repositories
        self.stocks = StockRepository(db_path)
        self.targets = TargetRepository(db_path)
        self.tags = TagRepository(db_path)
        self.notes = NoteRepository(db_path)
        self.alerts = AlertRepository(db_path)
        self.timeframes = TimeframeRepository(db_path)

    @contextmanager
    def get_connection(self):
        """Get database connection with context manager.

        Provides direct connection management for backward compatibility.
        """
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
                    exchange VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol)")

            # Migration: Add exchange column if it doesn't exist
            cursor.execute("PRAGMA table_info(stocks)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'exchange' not in columns:
                logger.info("Migrating stocks table: adding exchange column")
                cursor.execute("ALTER TABLE stocks ADD COLUMN exchange VARCHAR(50)")
                logger.info("Migration complete: exchange column added")

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

    def create_stock(self, symbol: str, company_name: Optional[str] = None, exchange: Optional[str] = None) -> int:
        """Create a new stock (delegates to StockRepository)."""
        return self.stocks.create_stock(symbol, company_name, exchange)

    def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        """Get stock by symbol (delegates to StockRepository)."""
        return self.stocks.get_stock_by_symbol(symbol)

    def get_stock_by_id(self, stock_id: int) -> Optional[Stock]:
        """Get stock by ID (delegates to StockRepository)."""
        return self.stocks.get_stock_by_id(stock_id)

    def get_all_stocks(self, tag: Optional[str] = None, search: Optional[str] = None) -> List[Stock]:
        """Get all stocks with optional filters (delegates to StockRepository)."""
        return self.stocks.get_all_stocks(tag, search)

    def update_stock(self, stock_id: int, company_name: Optional[str] = None, exchange: Optional[str] = None) -> bool:
        """Update stock information (delegates to StockRepository)."""
        return self.stocks.update_stock(stock_id, company_name, exchange)

    def delete_stock(self, stock_id: int) -> bool:
        """Delete a stock and all related data (delegates to StockRepository)."""
        return self.stocks.delete_stock(stock_id)

    # ==================== TARGET OPERATIONS ====================

    def create_target(self, stock_id: int, target_type: str, target_price: float,
                     trim_percentage: Optional[float] = None, alert_note: Optional[str] = None) -> int:
        """Create a new price target (delegates to TargetRepository)."""
        return self.targets.create_target(stock_id, target_type, target_price, trim_percentage, alert_note)

    def get_targets_for_stock(self, stock_id: int, active_only: bool = False) -> List[Target]:
        """Get all targets for a stock (delegates to TargetRepository)."""
        return self.targets.get_targets_for_stock(stock_id, active_only)

    def get_all_active_targets(self) -> List[Tuple[Stock, Target]]:
        """Get all active targets with their stocks (delegates to TargetRepository)."""
        return self.targets.get_all_active_targets()

    def update_target(self, target_id: int, target_price: Optional[float] = None,
                     alert_note: Optional[str] = None, trim_percentage: Optional[float] = None) -> bool:
        """Update a target (delegates to TargetRepository)."""
        return self.targets.update_target(target_id, target_price, alert_note, trim_percentage)

    def toggle_target_active(self, target_id: int) -> bool:
        """Toggle target active status (delegates to TargetRepository)."""
        return self.targets.toggle_target_active(target_id)

    def delete_target(self, target_id: int) -> bool:
        """Delete a target (delegates to TargetRepository)."""
        return self.targets.delete_target(target_id)

    # ==================== TAG OPERATIONS ====================

    def create_tag(self, name: str, color: Optional[str] = None) -> int:
        """Create a new tag (delegates to TagRepository)."""
        return self.tags.create_tag(name, color)

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get tag by name (delegates to TagRepository)."""
        return self.tags.get_tag_by_name(name)

    def get_all_tags(self) -> List[Tuple[Tag, int]]:
        """Get all tags with stock counts (delegates to TagRepository)."""
        return self.tags.get_all_tags()

    def get_tags_for_stock(self, stock_id: int) -> List[Tag]:
        """Get all tags for a stock (delegates to TagRepository)."""
        return self.tags.get_tags_for_stock(stock_id)

    def add_tag_to_stock(self, stock_id: int, tag_id: int) -> bool:
        """Add a tag to a stock (delegates to TagRepository)."""
        return self.tags.add_tag_to_stock(stock_id, tag_id)

    def remove_tag_from_stock(self, stock_id: int, tag_id: int) -> bool:
        """Remove a tag from a stock (delegates to TagRepository)."""
        return self.tags.remove_tag_from_stock(stock_id, tag_id)

    def update_tag(self, tag_id: int, name: Optional[str] = None, color: Optional[str] = None) -> bool:
        """Update a tag (delegates to TagRepository)."""
        return self.tags.update_tag(tag_id, name, color)

    def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag (delegates to TagRepository)."""
        return self.tags.delete_tag(tag_id)

    # ==================== TIMEFRAME OPERATIONS ====================

    def get_all_timeframes(self) -> List[Tuple[Timeframe, int]]:
        """Get all investment timeframes with stock counts (delegates to TimeframeRepository)."""
        return self.timeframes.get_all_timeframes()

    def get_timeframe_by_id(self, timeframe_id: int) -> Optional[Timeframe]:
        """Get timeframe by ID (delegates to TimeframeRepository)."""
        return self.timeframes.get_timeframe_by_id(timeframe_id)

    def get_timeframes_for_stock(self, stock_id: int) -> List[Timeframe]:
        """Get all timeframes for a stock (delegates to TimeframeRepository)."""
        return self.timeframes.get_timeframes_for_stock(stock_id)

    def add_timeframe_to_stock(self, stock_id: int, timeframe_id: int) -> bool:
        """Add a timeframe to a stock (delegates to TimeframeRepository)."""
        return self.timeframes.add_timeframe_to_stock(stock_id, timeframe_id)

    def remove_timeframe_from_stock(self, stock_id: int, timeframe_id: int) -> bool:
        """Remove a timeframe from a stock (delegates to TimeframeRepository)."""
        return self.timeframes.remove_timeframe_from_stock(stock_id, timeframe_id)

    def create_timeframe(self, name: str, color: Optional[str] = None, description: Optional[str] = None) -> int:
        """Create a new investment timeframe (delegates to TimeframeRepository)."""
        return self.timeframes.create_timeframe(name, color, description)

    def update_timeframe(self, timeframe_id: int, name: Optional[str] = None, color: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Update a timeframe (delegates to TimeframeRepository)."""
        return self.timeframes.update_timeframe(timeframe_id, name, color, description)

    def delete_timeframe(self, timeframe_id: int) -> bool:
        """Delete a timeframe (delegates to TimeframeRepository)."""
        return self.timeframes.delete_timeframe(timeframe_id)

    # ==================== NOTE OPERATIONS ====================

    def create_note(self, stock_id: int, title: str, content: str, note_date: date) -> int:
        """Create a new note (delegates to NoteRepository)."""
        return self.notes.create_note(stock_id, title, content, note_date)

    def get_notes_for_stock(self, stock_id: int, limit: Optional[int] = None) -> List[Note]:
        """Get all notes for a stock (delegates to NoteRepository)."""
        return self.notes.get_notes_for_stock(stock_id, limit)

    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Get a note by ID (delegates to NoteRepository)."""
        return self.notes.get_note_by_id(note_id)

    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> bool:
        """Update a note (delegates to NoteRepository)."""
        return self.notes.update_note(note_id, title, content)

    def delete_note(self, note_id: int) -> bool:
        """Delete a note (delegates to NoteRepository)."""
        return self.notes.delete_note(note_id)

    def get_notes_count_for_stock(self, stock_id: int) -> int:
        """Get count of notes for a stock (delegates to NoteRepository)."""
        return self.notes.get_notes_count_for_stock(stock_id)

    # ==================== ALERT HISTORY OPERATIONS ====================

    def create_alert_history(self, stock_id: int, target_id: int, current_price: float,
                            target_price: float, target_type: str, alert_note: Optional[str] = None,
                            email_sent: bool = False) -> int:
        """Create an alert history entry (delegates to AlertRepository)."""
        return self.alerts.create_alert_history(stock_id, target_id, current_price, target_price, target_type, alert_note, email_sent)

    def get_alert_history(self, stock_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[AlertHistory]:
        """Get alert history (delegates to AlertRepository)."""
        return self.alerts.get_alert_history(stock_id, limit, offset)

    def get_latest_alert_for_stock(self, stock_id: int) -> Optional[AlertHistory]:
        """Get most recent alert for a stock (delegates to AlertRepository)."""
        return self.alerts.get_latest_alert_for_stock(stock_id)

    def delete_alert_history(self, alert_id: int) -> bool:
        """Delete an alert history entry (delegates to AlertRepository)."""
        return self.alerts.delete_alert_history(alert_id)

    # ============================================================================
    # BATCH QUERY METHODS (to prevent N+1 query problems)
    # ============================================================================

    def get_targets_for_stocks_batch(self, stock_ids: List[int], active_only: bool = False) -> Dict[int, List[Target]]:
        """Get targets for multiple stocks in a single query (delegates to TargetRepository)."""
        return self.targets.get_targets_for_stocks_batch(stock_ids, active_only)

    def get_tags_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, List[Tag]]:
        """Get tags for multiple stocks in a single query (delegates to TagRepository)."""
        return self.tags.get_tags_for_stocks_batch(stock_ids)

    def get_timeframes_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, List[Timeframe]]:
        """Get timeframes for multiple stocks in a single query (delegates to TimeframeRepository)."""
        return self.timeframes.get_timeframes_for_stocks_batch(stock_ids)

    def get_notes_count_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, int]:
        """Get notes count for multiple stocks in a single query (delegates to NoteRepository)."""
        return self.notes.get_notes_count_for_stocks_batch(stock_ids)

    def get_latest_alert_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, Optional[AlertHistory]]:
        """Get latest alert for multiple stocks in a single query (delegates to AlertRepository)."""
        return self.alerts.get_latest_alert_for_stocks_batch(stock_ids)
