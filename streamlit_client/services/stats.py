"""
Progress, body stats, and dashboard analytics helpers.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from ..db import execute, fetch_all, fetch_one


def log_body_stats(
    user_id: int,
    log_date: date,
    weight: float,
    neck: Optional[float],
    waist: Optional[float],
    hips: Optional[float],
    body_fat_pct: Optional[float],
    notes: Optional[str],
) -> int:
    """Insert a body stats record."""
    return execute(
        """
        INSERT INTO user_stats_log (
            user_id, date, weight, neck, waist, hips, body_fat_percentage, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [user_id, log_date, weight, neck, waist, hips, body_fat_pct, notes],
    )


def list_body_stats(user_id: int) -> List[Dict[str, Any]]:
    """Return all body stats logs sorted by date."""
    return fetch_all(
        """
        SELECT log_id, date, weight, neck, waist, hips, body_fat_percentage, notes
        FROM user_stats_log
        WHERE user_id = %s
        ORDER BY date DESC, log_id DESC
        """,
        [user_id],
    )


def bodyweight_trend(user_id: int) -> List[Dict[str, Any]]:
    """Weight trend for charting."""
    return fetch_all(
        """
        SELECT date, weight
        FROM user_stats_log
        WHERE user_id = %s AND weight IS NOT NULL
        ORDER BY date ASC
        """,
        [user_id],
    )


def recent_prs(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """Latest PRs for dashboard."""
    return fetch_all(
        """
        SELECT
            e.name AS exercise_name,
            pb.pb_weight,
            pb.pb_reps,
            pb.pb_date,
            pb.previous_pr
        FROM user_pb pb
        JOIN exercise e ON e.exercise_id = pb.exercise_id
        WHERE pb.user_id = %s
        ORDER BY pb.pb_date DESC, pb.pb_weight DESC
        LIMIT %s
        """,
        [user_id, limit],
    )


def validation_events(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Recent validation rows for the progress page."""
    return fetch_all(
        """
        SELECT
            v.timestamp,
            e.name AS exercise_name,
            v.input_weight,
            v.expected_max,
            v.flagged_as
        FROM data_validation v
        LEFT JOIN exercise e ON e.exercise_id = v.exercise_id
        WHERE v.user_id = %s
        ORDER BY v.timestamp DESC
        LIMIT %s
        """,
        [user_id, limit],
    )


def volume_by_workout(user_id: int) -> List[Dict[str, Any]]:
    """Total volume per completed workout."""
    return fetch_all(
        """
        SELECT
            ws.session_name,
            ws.session_date,
            COALESCE(SUM(CASE WHEN s.weight IS NOT NULL AND s.reps IS NOT NULL THEN s.weight * s.reps ELSE 0 END), 0) AS volume
        FROM workout_sessions ws
        LEFT JOIN session_exercises se ON se.session_id = ws.session_id
        LEFT JOIN sets s ON s.session_exercise_id = se.session_exercise_id
        WHERE ws.user_id = %s AND ws.is_template = 0 AND ws.completed = 1
        GROUP BY ws.session_id, ws.session_name, ws.session_date
        ORDER BY ws.session_date ASC
        """,
        [user_id],
    )


def weekly_metrics(user_id: int) -> List[Dict[str, Any]]:
    """Weekly metrics table using session-level aggregates."""
    return fetch_all(
        """
        SELECT
            ws.session_name,
            ws.session_date,
            ws.duration_minutes,
            COUNT(DISTINCT se.session_exercise_id) AS exercises,
            COUNT(s.set_id) AS total_sets,
            COALESCE(SUM(s.reps), 0) AS total_reps,
            COALESCE(AVG(s.rpe), 0) AS avg_rpe,
            COALESCE(SUM(CASE WHEN s.weight IS NOT NULL AND s.reps IS NOT NULL THEN s.weight * s.reps ELSE 0 END), 0) AS total_volume,
            MAX(v.flagged_as) AS validation_flag
        FROM workout_sessions ws
        LEFT JOIN session_exercises se ON se.session_id = ws.session_id
        LEFT JOIN sets s ON s.session_exercise_id = se.session_exercise_id
        LEFT JOIN data_validation v ON v.set_id = s.set_id
        WHERE ws.user_id = %s AND ws.is_template = 0 AND ws.completed = 1
        GROUP BY ws.session_id, ws.session_name, ws.session_date, ws.duration_minutes
        ORDER BY ws.session_date DESC
        """,
        [user_id],
    )


def dashboard_kpis(user_id: int) -> Dict[str, Any]:
    """Return streak, weekly count, total workouts."""
    totals = fetch_one(
        """
        SELECT
            SUM(CASE WHEN ws.completed = 1 THEN 1 ELSE 0 END) AS total_completed,
            SUM(CASE WHEN ws.completed = 1 AND YEARWEEK(ws.session_date, 1) = YEARWEEK(CURDATE(), 1) THEN 1 ELSE 0 END) AS week_completed
        FROM workout_sessions ws
        WHERE ws.user_id = %s AND ws.is_template = 0
        """,
        [user_id],
    ) or {}

    dates = fetch_all(
        """
        SELECT DISTINCT ws.session_date
        FROM workout_sessions ws
        WHERE ws.user_id = %s AND ws.is_template = 0 AND ws.completed = 1
        ORDER BY ws.session_date DESC
        """,
        [user_id],
    )
    streak = 0
    today = date.today()
    for idx, row in enumerate(dates):
        session_date = row["session_date"]
        expected = today - timedelta(days=idx)
        if session_date == expected:
            streak += 1
        else:
            break

    return {
        "streak": streak,
        "week_completed": int(totals.get("week_completed") or 0),
        "total_completed": int(totals.get("total_completed") or 0),
    }

