"""
Utility functions for generating and maintaining workout progress records.

This module is responsible for computing aggregate training statistics such as:
- Maximum weight lifted per exercise
- Total training volume (weight × reps)
- Weekly and daily performance summaries

These statistics are stored in the `progress` model and displayed throughout
the WorkoutWare application, especially in the Progress Dashboard.

The progress records act as a lightweight analytics engine, allowing fast
queries for trends and recommendations without repeatedly scanning the raw logs.

This module is typically called:
    - When a new set is logged
    - When viewing the progress dashboard
    - When rebuilding the entire progress table (e.g., admin/debug)
"""

from datetime import date, timedelta

from django.db import connection
from workoutware_app.models import progress, workout_sessions, session_exercises, sets


# ------------------------------------------------------------------------------
# HELPER QUERIES
# ------------------------------------------------------------------------------

def _get_user_exercise_sessions(user_id):
    """
    Retrieve all completed workout sessions for a given user that contain
    valid sets with weights.

    Args:
        user_id (int): User identifier.

    Returns:
        list of dict:
            Each dictionary contains:
                - session_date
                - exercise_id
                - weight
                - reps
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT ws.session_date,
                   se.exercise_id,
                   s.weight,
                   s.reps
            FROM workout_sessions ws
            JOIN session_exercises se ON ws.session_id = se.session_id
            JOIN sets s ON s.session_exercise_id = se.session_exercise_id
            WHERE ws.user_id = %s
              AND ws.completed = 1
              AND ws.is_template = 0
              AND s.weight IS NOT NULL
            ORDER BY ws.session_date ASC
            """,
            [user_id],
        )
        rows = cursor.fetchall()

    return [
        {
            "session_date": row[0],
            "exercise_id": row[1],
            "weight": float(row[2]),
            "reps": row[3],
        }
        for row in rows
    ]


def _aggregate_by_period(records, period="weekly"):
    """
    Aggregate raw exercise-set records into periods.

    Supported periods:
        - "daily"
        - "weekly"

    Args:
        records (list[dict]): Output of _get_user_exercise_sessions().
        period (str): Aggregation type.

    Returns:
        dict:
            Keys: (exercise_id, period_date)
            Values: {
                "max_weight": float,
                "total_volume": float
            }
    """
    aggregated = {}

    for r in records:
        date_key = r["session_date"]

        if period == "weekly":
            # Align to the start of the week (Monday)
            date_key = date_key - timedelta(days=date_key.weekday())

        key = (r["exercise_id"], date_key)
        weight = r["weight"]
        volume = r["weight"] * r["reps"]

        if key not in aggregated:
            aggregated[key] = {
                "max_weight": weight,
                "total_volume": volume,
            }
        else:
            aggregated[key]["max_weight"] = max(aggregated[key]["max_weight"], weight)
            aggregated[key]["total_volume"] += volume

    return aggregated


# ------------------------------------------------------------------------------
# PUBLIC FUNCTIONS
# ------------------------------------------------------------------------------

def rebuild_progress_for_user(user_id):
    """
    Completely rebuild the progress table for one user.

    This is used when:
        - Data is migrated from SQLite → MySQL
        - Debugging incorrect progress values
        - Admin wants a recalculation
        - User deletes many sessions and progress must be recomputed

    Steps:
        1. Delete all progress rows for the user.
        2. Retrieve all historical workout data.
        3. Compute daily & weekly aggregates.
        4. Insert new progress entries into the database.

    Args:
        user_id (int)

    Returns:
        int: Number of progress records recreated.
    """
    # Step 1 — Delete old records
    progress.objects.filter(user_id=user_id).delete()

    # Step 2 — Fetch raw historical training data
    records = _get_user_exercise_sessions(user_id)
    if not records:
        return 0

    # Step 3 — Aggregate daily & weekly stats
    daily_data = _aggregate_by_period(records, period="daily")
    weekly_data = _aggregate_by_period(records, period="weekly")

    # Step 4 — Insert records into progress table
    new_progress_entries = []

    # Daily entries
    for (exercise_id, day), stats in daily_data.items():
        new_progress_entries.append(
            progress(
                user_id=user_id,
                exercise_id=exercise_id,
                date=day,
                period_type="daily",
                max_weight=stats["max_weight"],
                total_volume=stats["total_volume"],
            )
        )

    # Weekly entries
    for (exercise_id, week_start), stats in weekly_data.items():
        new_progress_entries.append(
            progress(
                user_id=user_id,
                exercise_id=exercise_id,
                date=week_start,
                period_type="weekly",
                max_weight=stats["max_weight"],
                total_volume=stats["total_volume"],
            )
        )

    progress.objects.bulk_create(new_progress_entries)
    return len(new_progress_entries)


def update_progress_after_set(user_id, exercise_id, session_date):
    """
    Incrementally update progress metrics after a new set is logged.

    This is a more lightweight alternative to full rebuilding.

    Args:
        user_id (int)
        exercise_id (int)
        session_date (date): Date of the workout session.

    Behavior:
        - Recomputes only the affected *daily* and *weekly* rows.
        - Useful for real-time updates after logging a set.
    """
    # Re-fetch all sets for that exercise and user on this date
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT s.weight, s.reps
            FROM sets s
            JOIN session_exercises se ON s.session_exercise_id = se.session_exercise_id
            JOIN workout_sessions ws ON se.session_id = ws.session_id
            WHERE ws.user_id = %s
              AND se.exercise_id = %s
              AND ws.session_date = %s
              AND ws.completed = 1
            """,
            [user_id, exercise_id, session_date],
        )
        rows = cursor.fetchall()

    if not rows:
        return

    # Compute daily stats
    max_weight = max(float(r[0]) for r in rows if r[0] is not None)
    total_volume = sum(float(r[0]) * r[1] for r in rows if r[0] is not None)

    # Update or create daily progress
    progress.objects.update_or_create(
        user_id=user_id,
        exercise_id=exercise_id,
        date=session_date,
        period_type="daily",
        defaults={
            "max_weight": max_weight,
            "total_volume": total_volume,
        },
    )

    # Compute weekly date key
    week_start = session_date - timedelta(days=session_date.weekday())

    # Recompute weekly stats by aggregating all sessions in the week
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT s.weight, s.reps
            FROM sets s
            JOIN session_exercises se ON s.session_exercise_id = se.session_exercise_id
            JOIN workout_sessions ws ON ws.session_id = se.session_id
            WHERE ws.user_id = %s
              AND se.exercise_id = %s
              AND ws.completed = 1
              AND ws.session_date >= %s
              AND ws.session_date < %s
            """,
            [user_id, exercise_id, week_start, week_start + timedelta(days=7)],
        )
        week_rows = cursor.fetchall()

    if not week_rows:
        return

    weekly_max = max(float(r[0]) for r in week_rows if r[0] is not None)
    weekly_volume = sum(float(r[0]) * r[1] for r in week_rows if r[0] is not None)

    # Update or create weekly progress
    progress.objects.update_or_create(
        user_id=user_id,
        exercise_id=exercise_id,
        date=week_start,
        period_type="weekly",
        defaults={
            "max_weight": weekly_max,
            "total_volume": weekly_volume,
        },
    )

