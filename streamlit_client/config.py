"""
Configuration helpers for the Streamlit client.

Values are sourced from environment variables so the app can point at the
existing MySQL instance without code changes. Defaults are safe for local
docker-compose usage.
"""

from dataclasses import dataclass
import os
from functools import lru_cache
from typing import Dict, Any


@dataclass(frozen=True)
class Settings:
    """Container for app-level settings."""

    app_name: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    pr_outlier_pct: float
    suspicious_low_pct: float

    def mysql_kwargs(self) -> Dict[str, Any]:
        """Return kwargs suitable for mysql.connector.connect."""
        return {
            "host": self.db_host,
            "port": self.db_port,
            "database": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Fetch settings from environment with sensible defaults.

    Environment variables:
        DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    """
    return Settings(
        app_name=os.getenv("APP_NAME", "Workoutware"),
        db_host=os.getenv("DB_HOST", "127.0.0.1"),
        db_port=int(os.getenv("DB_PORT", "3306")),
        db_name=os.getenv("DB_NAME", "workoutware"),
        db_user=os.getenv("DB_USER", "root"),
        db_password=os.getenv("DB_PASSWORD", "Rutgers123"),
        pr_outlier_pct=float(os.getenv("PR_OUTLIER_PCT", "0.15")),
        suspicious_low_pct=float(os.getenv("SUSPICIOUS_LOW_PCT", "0.30")),
    )

