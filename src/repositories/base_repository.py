"""Base repository for shared database connection management."""

import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository providing connection management for all domain repositories."""

    def __init__(self, db_path: str):
        """Initialize base repository.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """Get database connection with context manager.

        Yields:
            sqlite3.Connection: Database connection with row factory

        Raises:
            Exception: If database error occurs (after rollback)
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
