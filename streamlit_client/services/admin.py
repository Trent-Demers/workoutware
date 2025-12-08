"""
Admin-facing helpers: KPIs and exercise library CRUD.
"""

from typing import Any, Dict, List, Optional

from ..db import execute, fetch_all, fetch_one


def admin_kpis() -> Dict[str, int]:
    """Return basic platform metrics."""
    totals = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM user_info) AS users,
            (SELECT COUNT(*) FROM workout_sessions WHERE is_template = 0) AS workouts,
            (
                SELECT COUNT(DISTINCT user_id)
                FROM workout_sessions
                WHERE session_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    AND is_template = 0
            ) AS mau,
            (SELECT COUNT(*) FROM data_validation WHERE flagged_as IN ('outlier', 'suspicious_low')) AS flagged_sets
        """
    ) or {}
    return {
        "users": int(totals.get("users") or 0),
        "workouts": int(totals.get("workouts") or 0),
        "mau": int(totals.get("mau") or 0),
        "flagged_sets": int(totals.get("flagged_sets") or 0),
    }


def recent_users(limit: int = 6) -> List[Dict[str, Any]]:
    """Recent users for admin grid."""
    return fetch_all(
        """
        SELECT user_id, username, email, date_registered
        FROM user_info
        ORDER BY date_registered DESC, user_id DESC
        LIMIT %s
        """,
        [limit],
    )


def list_exercises() -> List[Dict[str, Any]]:
    """Exercise library table."""
    return fetch_all(
        """
        SELECT exercise_id, name, exercise_type, subtype, equipment, difficulty, description
        FROM exercise
        ORDER BY name ASC
        """
    )


def create_exercise(
    name: str,
    exercise_type: str,
    subtype: Optional[str],
    equipment: Optional[str],
    difficulty: Optional[str],
    description: Optional[str],
) -> int:
    """Insert a new exercise."""
    return execute(
        """
        INSERT INTO exercise (name, exercise_type, subtype, equipment, difficulty, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        [name, exercise_type, subtype, equipment, difficulty, description],
    )


def update_exercise(
    exercise_id: int,
    name: str,
    exercise_type: str,
    subtype: Optional[str],
    equipment: Optional[str],
    difficulty: Optional[str],
    description: Optional[str],
) -> None:
    """Update an exercise."""
    execute(
        """
        UPDATE exercise
        SET name = %s,
            exercise_type = %s,
            subtype = %s,
            equipment = %s,
            difficulty = %s,
            description = %s
        WHERE exercise_id = %s
        """,
        [name, exercise_type, subtype, equipment, difficulty, description, exercise_id],
    )


def delete_exercise(exercise_id: int) -> None:
    """Remove an exercise."""
    execute("DELETE FROM exercise WHERE exercise_id = %s", [exercise_id])

