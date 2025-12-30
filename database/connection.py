"""Database connection management"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
from config import DATABASE_PATH


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db_cursor() -> Generator[sqlite3.Cursor, None, None]:
    """Database cursor context manager"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

