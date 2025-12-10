"""
Configuration helpers for the Streamlit client.

Values are sourced from environment variables so the app can point at the
existing MySQL instance without code changes. Defaults are safe for local
docker-compose usage.

================================================================================
SETUP INSTRUCTIONS - CONFIGURATION
================================================================================

ENVIRONMENT VARIABLES:
    Configure database connection via environment variables. If not set, defaults
    are used (shown below).

    DB_HOST: MySQL host address (default: 127.0.0.1)
    DB_PORT: MySQL port number (default: 3306)
    DB_NAME: Database name (default: workoutware)
    DB_USER: MySQL username (default: root)
    DB_PASSWORD: MySQL password (default: Rutgers123)

SETTING ENVIRONMENT VARIABLES:

    Windows (PowerShell):
        $env:DB_HOST="127.0.0.1"
        $env:DB_PORT="3306"
        $env:DB_NAME="workoutware"
        $env:DB_USER="root"
        $env:DB_PASSWORD="Rutgers123"

    Windows (Command Prompt):
        set DB_HOST=127.0.0.1
        set DB_PORT=3306
        set DB_NAME=workoutware
        set DB_USER=root
        set DB_PASSWORD=Rutgers123

    Mac/Linux:
        export DB_HOST=127.0.0.1
        export DB_PORT=3306
        export DB_NAME=workoutware
        export DB_USER=root
        export DB_PASSWORD=Rutgers123

    Using .env file (recommended):
        Create a .env file in project root:
        DB_HOST=127.0.0.1
        DB_PORT=3306
        DB_NAME=workoutware
        DB_USER=root
        DB_PASSWORD=Rutgers123

VALIDATION SETTINGS:
    PR_OUTLIER_PCT: Percentage threshold for PR detection (default: 0.15 = 15%)
    SUSPICIOUS_LOW_PCT: Percentage threshold for suspiciously low values (default: 0.30 = 30%)

IMPORTANT:
    - Database credentials must match Django settings.py configuration
    - Ensure MySQL container is running before starting Streamlit
    - Default password 'Rutgers123' should be changed in production
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

