"""
Utility functions for generating and maintaining workout progress records.

This module is responsible for computing aggregate training statistics such as:
- Maximum weight lifted per exercise
- Average weight per exercise
- Total training volume (weight × reps)
- Workout count (distinct sessions)
- Daily, weekly, monthly, quarterly, or yearly performance summaries

These statistics are stored in the `progress` model and displayed throughout
the WorkoutWare application, especially in the Progress Dashboard.

The progress records act as a lightweight analytics engine, allowing fast
queries for trends and recommendations without repeatedly scanning the raw logs.

This module is typically called:
    - When a new set is logged
    - When viewing the progress dashboard
    - When rebuilding the entire progress table (e.g., admin/debug)
"""

from datetime import timedelta

from django.db import transaction
from django.db.models import F, Max, Avg, Sum, Count, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncWeek, TruncDate, TruncMonth, TruncQuarter, TruncYear

from .models import (
    sets,
    progress,
    workout_sessions,
    session_exercises,
    exercise,
    user_info,
)


# ------------------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------------------

DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"
QUARTERLY = "3 monthly"
YEARLY = "yearly"


# ------------------------------------------------------------------------------
# HELPER QUERIES
# ------------------------------------------------------------------------------

def _base_set_queryset_for_user(user_id):
    """
    Base queryset of sets for a given user, joined to session + exercise,
    excluding templates, warmups, and missing weights.

    Args:
        user_id (int): User identifier.

    Returns:
        QuerySet: Filtered sets with select_related optimizations.
    """
    return (
        sets.objects
        .filter(
            session_exercise_id__session_id__user_id=user_id,
            session_exercise_id__session_id__is_template=False,
            session_exercise_id__session_id__completed=True,
            completed=True,
            is_warmup=False,
            weight__isnull=False,
        )
        .select_related(
            "session_exercise_id",
            "session_exercise_id__exercise_id",
            "session_exercise_id__session_id",
        )
    )


def _aggregate_sets_by_period(queryset, period_type):
    """
    Aggregate a queryset of sets by time period (daily, weekly, monthly, quarterly, or yearly).

    Args:
        queryset (QuerySet): Filtered sets queryset.
        period_type (str): "daily", "weekly", "monthly", "quarterly", or "yearly".

    Returns:
        QuerySet: Aggregated data with columns:
            - period_start: Date of period start
            - ex_id: Exercise ID
            - max_weight: Maximum weight in period
            - avg_weight: Average weight in period
            - total_volume: Sum of (weight × reps)
            - workout_count: Count of distinct sessions
    """
    # Expression for volume: weight * reps
    volume_expr = ExpressionWrapper(
        F("weight") * F("reps"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    # Choose truncation function based on period type
    trunc_funcs = {
        DAILY: TruncDate,
        WEEKLY: TruncWeek,
        MONTHLY: TruncMonth,
        QUARTERLY: TruncQuarter,
        YEARLY: TruncYear,
    }

    trunc_func = trunc_funcs[period_type]("session_exercise_id__session_id__session_date")

    return (
        queryset
        .annotate(
            period_start=trunc_func,
            ex_id=F("session_exercise_id__exercise_id"),
        )
        .values("period_start", "ex_id")
        .annotate(
            max_weight=Max("weight"),
            avg_weight=Avg("weight"),
            total_volume=Sum(volume_expr),
            workout_count=Count("session_exercise_id__session_id", distinct=True),
        )
        .order_by("period_start", "ex_id")
    )


# ------------------------------------------------------------------------------
# PUBLIC FUNCTIONS
# ------------------------------------------------------------------------------

@transaction.atomic
def rebuild_progress_for_user(user_id, period_types=None):
    """
    Completely rebuild the progress table for one user.

    This is used when:
        - Data is migrated from SQLite → MySQL
        - Debugging incorrect progress values
        - Admin wants a recalculation
        - User deletes many sessions and progress must be recomputed

    Steps:
        1. Delete specified progress period types for the user.
        2. Retrieve all historical workout data.
        3. Compute daily, weekly, monthly, quarterly, or yearly aggregates.
        4. Bulk insert new progress entries into the database.

    Args:
        user_id (int): User identifier.
        period_types (list[str], optional): List of period types to rebuild.
            Defaults to ["weekly"] if None.

    Returns:
        int: Number of progress records recreated.
    """
    if period_types is None:
        period_types = [WEEKLY]

    # Step 1 — Delete old records for specified period types
    progress.objects.filter(
        user_id=user_id, 
        period_type__in=period_types
    ).delete()

    # Step 2 — Get base queryset
    qs = _base_set_queryset_for_user(user_id)

    if not qs.exists():
        return 0  # No data to aggregate

    # Step 3 — Get user object for FK relationships
    user_obj = user_info.objects.get(user_id=user_id)

    progress_rows = []

    # Step 4 — Aggregate and create progress entries for each period type
    for period_type in period_types:
        aggregated_stats = _aggregate_sets_by_period(qs, period_type)

        for row in aggregated_stats:
            progress_rows.append(
                progress(
                    user_id=user_obj,
                    exercise_id=exercise.objects.get(pk=row["ex_id"]),
                    date=row["period_start"],
                    period_type=period_type,
                    max_weight=row["max_weight"],
                    avg_weight=row["avg_weight"],
                    total_volume=row["total_volume"],
                    workout_count=row["workout_count"],
                )
            )

    # Step 5 — Bulk insert all progress rows
    progress.objects.bulk_create(progress_rows)

    return len(progress_rows)