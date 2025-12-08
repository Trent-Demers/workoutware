"""
Smart validation and PR detection helpers.

This module centralizes the thresholds described in the PRD and writes to the
`data_validation` table so the Streamlit UI can surface the same flags as the
Django app.
"""

from typing import Any, Dict, Optional, Tuple

from ..config import get_settings
from ..db import fetch_one, execute


def _baseline_for_exercise(user_id: int, exercise_id: int) -> Tuple[Optional[float], Optional[float]]:
    """
    Return (max_weight, avg_weight) for the given user/exercise across completed sessions.
    """
    row = fetch_one(
        """
        SELECT
            MAX(s.weight) AS max_weight,
            AVG(s.weight) AS avg_weight
        FROM sets s
        JOIN session_exercises se ON se.session_exercise_id = s.session_exercise_id
        JOIN workout_sessions ws ON ws.session_id = se.session_id
        WHERE
            ws.user_id = %s
            AND se.exercise_id = %s
            AND ws.is_template = 0
            AND ws.completed = 1
            AND s.completed = 1
            AND s.is_warmup = 0
            AND s.weight IS NOT NULL
        """,
        [user_id, exercise_id],
    )
    if not row:
        return None, None
    return (
        float(row["max_weight"]) if row["max_weight"] is not None else None,
        float(row["avg_weight"]) if row["avg_weight"] is not None else None,
    )


def evaluate_set(user_id: int, exercise_id: int, weight: float) -> Dict[str, Any]:
    """
    Determine validation status for a set based on PR/outlier thresholds.

    Returns dict with:
        status: 'pr' | 'outlier' | 'suspicious_low' | 'normal'
        expected_max: previous max weight (if any)
        avg_weight: average baseline (if any)
        is_pr: whether this beats the previous best
    """
    settings = get_settings()
    previous_max, avg_weight = _baseline_for_exercise(user_id, exercise_id)

    status = "normal"
    is_pr = False

    if previous_max is None:
        status = "pr"
        is_pr = True
    else:
        outlier_threshold = previous_max * (1 + settings.pr_outlier_pct)
        if weight > outlier_threshold:
            status = "outlier"
            is_pr = True
        elif weight > previous_max:
            status = "pr"
            is_pr = True
        elif avg_weight and weight < avg_weight * (1 - settings.suspicious_low_pct):
            status = "suspicious_low"

    return {
        "status": status,
        "expected_max": previous_max,
        "avg_weight": avg_weight,
        "is_pr": is_pr,
    }


def record_validation(
    user_id: int,
    set_id: Optional[int],
    exercise_id: int,
    input_weight: float,
    expected_max: Optional[float],
    flagged_as: str,
    user_action: Optional[str] = None,
) -> None:
    """Insert a validation row into data_validation."""
    execute(
        """
        INSERT INTO data_validation (
            user_id, set_id, exercise_id, input_weight,
            expected_max, flagged_as, user_action, timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """,
        [
            user_id,
            set_id,
            exercise_id,
            input_weight,
            expected_max,
            flagged_as,
            user_action,
        ],
    )
