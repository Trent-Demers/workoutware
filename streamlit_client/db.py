"""
MySQL connection utilities for the Streamlit client.

Connections are pooled and retried to avoid stale sockets. Each helper uses
dictionary cursors for ergonomic access in the UI layer.

================================================================================
SETUP INSTRUCTIONS - DATABASE CONNECTION
================================================================================

PREREQUISITES:
    1. MySQL database must be running and accessible
    2. Database schema must be initialized (run sql/workoutware_db_setup.sql)
    3. Database credentials configured (see streamlit_client/config.py)

CONNECTION POOL CONFIGURATION:
    - Pool size: 8 connections (configurable in _get_pool function)
    - Auto-commit: Disabled (manual commit/rollback)
    - Retry logic: 3 attempts with exponential backoff

VERIFYING CONNECTION:
    If connection fails, check:
    1. MySQL container is running: docker ps
    2. Database exists: mysql -u root -p -e "SHOW DATABASES;"
    3. Credentials match config.py settings
    4. Network connectivity to MySQL host

TROUBLESHOOTING CONNECTION ERRORS:
    - "Can't connect to MySQL server": Check if MySQL is running
    - "Access denied": Verify username/password in config.py
    - "Unknown database": Run sql/workoutware_db_setup.sql first
    - "Connection pool exhausted": Increase pool_size in _get_pool()

TESTING CONNECTION:
    Test database connection from Python:
    from streamlit_client.db import get_connection
    with get_connection() as conn:
        print("Connection successful!")
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

