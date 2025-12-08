"""
Goal CRUD helpers.
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from ..db import execute, fetch_all, fetch_one


def _with_progress(row: Dict[str, Any]) -> Dict[str, Any]:
    """Augment a goal dict with progress percent."""
    target = float(row.get("target_value") or 0)
    current = float(row.get("current_value") or 0)
    pct = 0.0
    if target > 0:
        pct = min((current / target) * 100, 999.0)
    row["progress_percent"] = pct
    return row


def list_active_goals(user_id: int) -> List[Dict[str, Any]]:
    """Return active goals with computed progress."""
    rows = fetch_all(
        """
        SELECT
            goal_id,
            goal_type,
            goal_description,
            target_value,
            current_value,
            unit,
            target_date,
            start_date,
            status
        FROM goals
        WHERE user_id = %s AND status = 'active'
        ORDER BY target_date ASC, goal_id DESC
        """,
        [user_id],
    )
    return [_with_progress(r) for r in rows]


def create_goal(
    user_id: int,
    goal_type: str,
    description: str,
    target_value: float,
    unit: str,
    start_date: date,
    target_date: Optional[date],
    current_value: Optional[float],
    exercise_id: Optional[int] = None,
) -> int:
    """Create a goal and return its id."""
    return execute(
        """
        INSERT INTO goals (
            user_id, goal_type, goal_description, target_value, current_value,
            unit, exercise_id, start_date, target_date, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        """,
        [
            user_id,
            goal_type,
            description,
            target_value,
            current_value,
            unit,
            exercise_id,
            start_date,
            target_date,
        ],
    )


def update_progress(goal_id: int, new_value: float) -> None:
    """Update the current_value for a goal."""
    execute(
        """
        UPDATE goals
        SET current_value = %s
        WHERE goal_id = %s
        """,
        [new_value, goal_id],
    )


def complete_goal(goal_id: int) -> None:
    """Mark a goal as completed."""
    execute(
        """
        UPDATE goals
        SET status = 'completed', completion_date = CURDATE()
        WHERE goal_id = %s
        """,
        [goal_id],
    )


def delete_goal(goal_id: int, user_id: int) -> None:
    """Delete a goal for a user."""
    execute("DELETE FROM goals WHERE goal_id = %s AND user_id = %s", [goal_id, user_id])

