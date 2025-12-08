"""
Workout, template, and set logging helpers.
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from ..db import execute, fetch_all, fetch_one, execute_many
from .validation import evaluate_set, record_validation


def list_exercise_catalog() -> List[Dict[str, Any]]:
    """Return all exercises for dropdowns."""
    return fetch_all(
        """
        SELECT exercise_id, name, exercise_type, subtype, equipment, difficulty
        FROM exercise
        ORDER BY name ASC
        """
    )


def list_recent_sessions(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """Recent workouts (non-templates) with volume summary."""
    return fetch_all(
        """
        SELECT
            ws.session_id,
            ws.session_name,
            ws.session_date,
            ws.completed,
            ws.duration_minutes,
            COUNT(DISTINCT se.session_exercise_id) AS exercise_count,
            COALESCE(SUM(CASE WHEN s.weight IS NOT NULL AND s.reps IS NOT NULL THEN s.weight * s.reps ELSE 0 END), 0) AS total_volume
        FROM workout_sessions ws
        LEFT JOIN session_exercises se ON se.session_id = ws.session_id
        LEFT JOIN sets s ON s.session_exercise_id = se.session_exercise_id
        WHERE ws.user_id = %s AND ws.is_template = 0
        GROUP BY ws.session_id, ws.session_name, ws.session_date, ws.completed, ws.duration_minutes
        ORDER BY ws.session_date DESC, ws.session_id DESC
        LIMIT %s
        """,
        [user_id, limit],
    )


def list_completed_sessions(user_id: int, this_week_only: bool = False) -> List[Dict[str, Any]]:
    """Return completed workouts, optionally limited to current week."""
    params: List[Any] = [user_id]
    week_filter = ""
    if this_week_only:
        week_filter = "AND YEARWEEK(ws.session_date, 1) = YEARWEEK(CURDATE(), 1)"
    return fetch_all(
        f"""
        SELECT
            ws.session_id,
            ws.session_name,
            ws.session_date,
            ws.duration_minutes,
            ws.completed,
            COUNT(DISTINCT se.session_exercise_id) AS exercise_count,
            COALESCE(SUM(CASE WHEN s.weight IS NOT NULL AND s.reps IS NOT NULL THEN s.weight * s.reps ELSE 0 END), 0) AS total_volume
        FROM workout_sessions ws
        LEFT JOIN session_exercises se ON se.session_id = ws.session_id
        LEFT JOIN sets s ON s.session_exercise_id = se.session_exercise_id
        WHERE ws.user_id = %s AND ws.is_template = 0 AND ws.completed = 1
        {week_filter}
        GROUP BY ws.session_id, ws.session_name, ws.session_date, ws.duration_minutes, ws.completed
        ORDER BY ws.session_date DESC, ws.session_id DESC
        """,
        params,
    )


def list_templates(user_id: int) -> List[Dict[str, Any]]:
    """Return templates owned by the user."""
    return fetch_all(
        """
        SELECT session_id, session_name, session_date, duration_minutes
        FROM workout_sessions
        WHERE user_id = %s AND is_template = 1
        ORDER BY session_date DESC, session_id DESC
        """,
        [user_id],
    )


def recommended_exercises(user_id: int, limit: int = 6) -> List[Dict[str, Any]]:
    """Top exercises by frequency over the last 30 days."""
    return fetch_all(
        """
        SELECT
            e.exercise_id,
            e.name,
            COUNT(*) AS freq
        FROM sets s
        JOIN session_exercises se ON se.session_exercise_id = s.session_exercise_id
        JOIN workout_sessions ws ON ws.session_id = se.session_id
        JOIN exercise e ON e.exercise_id = se.exercise_id
        WHERE
            ws.user_id = %s
            AND ws.is_template = 0
            AND ws.session_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY e.exercise_id, e.name
        ORDER BY freq DESC
        LIMIT %s
        """,
        [user_id, limit],
    )


def create_session(
    user_id: int,
    name: str,
    session_date: date,
    start_time: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    is_template: bool = False,
) -> int:
    """Insert a workout session and return its id."""
    return execute(
        """
        INSERT INTO workout_sessions (
            user_id, session_name, session_date, start_time, duration_minutes, completed, is_template
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        [
            user_id,
            name,
            session_date,
            start_time,
            duration_minutes,
            0 if not is_template else 1,
            1 if is_template else 0,
        ],
    )


def add_exercise_to_session(
    session_id: int,
    exercise_id: int,
    exercise_order: int,
    target_sets: Optional[int],
    target_reps: Optional[int],
) -> int:
    """Add an exercise to a session and return session_exercise_id."""
    return execute(
        """
        INSERT INTO session_exercises (
            session_id, exercise_id, exercise_order, target_sets, target_reps, completed
        )
        VALUES (%s, %s, %s, %s, %s, 0)
        """,
        [session_id, exercise_id, exercise_order, target_sets, target_reps],
    )


def _sets_for_session_exercise(session_exercise_id: int) -> List[Dict[str, Any]]:
    """List sets for a single session_exercise."""
    return fetch_all(
        """
        SELECT
            set_id, set_number, weight, reps, rpe, completed, is_warmup, completion_time
        FROM sets
        WHERE session_exercise_id = %s
        ORDER BY set_number ASC
        """,
        [session_exercise_id],
    )


def get_session_detail(session_id: int) -> Dict[str, Any]:
    """Return session metadata, exercises, and sets."""
    session = fetch_one(
        """
        SELECT
            ws.session_id,
            ws.session_name,
            ws.session_date,
            ws.start_time,
            ws.duration_minutes,
            ws.completed,
            ws.is_template
        FROM workout_sessions ws
        WHERE ws.session_id = %s
        """,
        [session_id],
    )
    exercises = fetch_all(
        """
        SELECT
            se.session_exercise_id,
            se.exercise_order,
            se.target_sets,
            se.target_reps,
            se.completed,
            e.exercise_id,
            e.name
        FROM session_exercises se
        JOIN exercise e ON e.exercise_id = se.exercise_id
        WHERE se.session_id = %s
        ORDER BY se.exercise_order ASC
        """,
        [session_id],
    )
    for ex in exercises:
        ex["sets"] = _sets_for_session_exercise(ex["session_exercise_id"])
    return {"session": session, "exercises": exercises}


def _next_set_number(session_exercise_id: int) -> int:
    row = fetch_one(
        """
        SELECT COALESCE(MAX(set_number), 0) AS current
        FROM sets
        WHERE session_exercise_id = %s
        """,
        [session_exercise_id],
    )
    return int(row["current"]) + 1 if row else 1


def _record_pr(user_id: int, exercise_id: int, weight: float, reps: Optional[int]) -> None:
    """Update or insert a PR entry."""
    existing = fetch_one(
        """
        SELECT pr_id, pb_weight, pb_reps
        FROM user_pb
        WHERE user_id = %s AND exercise_id = %s AND pr_type = 'max_weight'
        ORDER BY pb_weight DESC
        LIMIT 1
        """,
        [user_id, exercise_id],
    )
    if existing and existing.get("pb_weight") and weight <= float(existing["pb_weight"]):
        return
    if existing:
        execute(
            """
            UPDATE user_pb
            SET pb_weight = %s, pb_reps = %s, pb_date = CURDATE(), previous_pr = %s
            WHERE pr_id = %s
            """,
            [weight, reps, existing.get("pb_weight"), existing["pr_id"]],
        )
    else:
        execute(
            """
            INSERT INTO user_pb (user_id, exercise_id, pr_type, pb_weight, pb_reps, pb_date)
            VALUES (%s, %s, 'max_weight', %s, %s, CURDATE())
            """,
            [user_id, exercise_id, weight, reps],
        )


def log_set(
    session_exercise_id: int,
    user_id: int,
    exercise_id: int,
    weight: float,
    reps: int,
    rpe: Optional[int],
    is_warmup: bool = False,
) -> Dict[str, Any]:
    """Insert a set and return status metadata."""
    set_number = _next_set_number(session_exercise_id)
    set_id = execute(
        """
        INSERT INTO sets (
            session_exercise_id, set_number, weight, reps, rpe, completed, is_warmup, completion_time
        )
        VALUES (%s, %s, %s, %s, %s, 1, %s, NOW())
        """,
        [session_exercise_id, set_number, weight, reps, rpe, 1 if is_warmup else 0],
    )

    validation = evaluate_set(user_id, exercise_id, weight)
    record_validation(
        user_id=user_id,
        set_id=set_id,
        exercise_id=exercise_id,
        input_weight=weight,
        expected_max=validation.get("expected_max"),
        flagged_as=validation["status"],
    )

    if validation.get("is_pr"):
        _record_pr(user_id, exercise_id, weight, reps)

    return {
        "set_id": set_id,
        "set_number": set_number,
        "validation": validation,
    }


def complete_session(session_id: int, duration_minutes: Optional[int] = None) -> None:
    """Mark a session as complete."""
    execute(
        """
        UPDATE workout_sessions
        SET completed = 1, duration_minutes = COALESCE(%s, duration_minutes)
        WHERE session_id = %s
        """,
        [duration_minutes, session_id],
    )


def delete_session(session_id: int, user_id: int) -> None:
    """Delete a session owned by the user."""
    execute(
        """
        DELETE FROM workout_sessions WHERE session_id = %s AND user_id = %s
        """,
        [session_id, user_id],
    )


def save_as_template(session_id: int, user_id: int, name: str) -> Optional[int]:
    """Clone a session into a template for the user."""
    session = fetch_one(
        """
        SELECT session_date, duration_minutes
        FROM workout_sessions
        WHERE session_id = %s AND user_id = %s
        """,
        [session_id, user_id],
    )
    if not session:
        return None

    new_template_id = create_session(
        user_id=user_id,
        name=name,
        session_date=session["session_date"],
        duration_minutes=session.get("duration_minutes"),
        is_template=True,
    )

    exercises = fetch_all(
        """
        SELECT exercise_id, exercise_order, target_sets, target_reps
        FROM session_exercises
        WHERE session_id = %s
        """,
        [session_id],
    )
    rows: List[Tuple[Any, ...]] = []
    for ex in exercises:
        rows.append(
            (
                new_template_id,
                ex["exercise_id"],
                ex["exercise_order"],
                ex.get("target_sets"),
                ex.get("target_reps"),
                0,
            )
        )
    execute_many(
        """
        INSERT INTO session_exercises (
            session_id, exercise_id, exercise_order, target_sets, target_reps, completed
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        rows,
    )
    return new_template_id


def use_template(template_id: int, user_id: int, new_date: date, name: Optional[str] = None) -> Optional[int]:
    """Create a new workout from an existing template."""
    template = fetch_one(
        """
        SELECT session_name, duration_minutes
        FROM workout_sessions
        WHERE session_id = %s AND user_id = %s AND is_template = 1
        """,
        [template_id, user_id],
    )
    if not template:
        return None

    session_name = name or template["session_name"] or "Template Workout"
    new_session_id = create_session(
        user_id=user_id,
        name=session_name,
        session_date=new_date,
        duration_minutes=template.get("duration_minutes"),
        is_template=False,
    )

    exercises = fetch_all(
        """
        SELECT exercise_id, exercise_order, target_sets, target_reps
        FROM session_exercises
        WHERE session_id = %s
        """,
        [template_id],
    )
    rows: List[Tuple[Any, ...]] = []
    for ex in exercises:
        rows.append(
            (
                new_session_id,
                ex["exercise_id"],
                ex["exercise_order"],
                ex.get("target_sets"),
                ex.get("target_reps"),
                0,
            )
        )
    execute_many(
        """
        INSERT INTO session_exercises (
            session_id, exercise_id, exercise_order, target_sets, target_reps, completed
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        rows,
    )
    return new_session_id
