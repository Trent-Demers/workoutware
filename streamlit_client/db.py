"""
MySQL connection utilities for the Streamlit client.

Connections are pooled and retried to avoid stale sockets. Each helper uses
dictionary cursors for ergonomic access in the UI layer.
"""

from contextlib import contextmanager
from time import sleep
from typing import Any, Dict, Iterable, List, Optional, Tuple

import mysql.connector
from mysql.connector import pooling, Error

from .config import get_settings

_POOL: Optional[pooling.MySQLConnectionPool] = None


def _get_pool() -> pooling.MySQLConnectionPool:
    """Return a singleton connection pool."""
    global _POOL
    if _POOL:
        return _POOL

    settings = get_settings()
    _POOL = pooling.MySQLConnectionPool(
        pool_name="ww_pool",
        pool_size=8,
        pool_reset_session=True,
        **settings.mysql_kwargs(),
    )
    return _POOL


@contextmanager
def get_connection():
    """
    Context manager yielding a pooled MySQL connection with retry logic.

    Rolls back on errors to avoid partial writes.
    """
    pool = _get_pool()
    conn = None

    for attempt in range(3):
        try:
            conn = pool.get_connection()
            conn.autocommit = False
            break
        except Error:
            if attempt == 2:
                raise
            sleep(0.75 * (attempt + 1))

    try:
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def fetch_all(query: str, params: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    """Execute a read-only query and return all rows as dicts."""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or [])
        rows = cursor.fetchall()
        cursor.close()
        return rows


def fetch_one(query: str, params: Optional[Iterable[Any]] = None) -> Optional[Dict[str, Any]]:
    """Execute a read-only query and return a single row as dict."""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or [])
        row = cursor.fetchone()
        cursor.close()
        return row


def execute(query: str, params: Optional[Iterable[Any]] = None) -> int:
    """
    Execute a write query and return the lastrowid when available.

    Returns 0 if the backend does not expose a last insert id.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        last_id = cursor.lastrowid or 0
        cursor.close()
        return last_id


def execute_many(query: str, rows: List[Tuple[Any, ...]]) -> None:
    """Execute many rows with a single prepared statement."""
    if not rows:
        return
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, rows)
        cursor.close()

