from django.db import transaction, models
from django.db.models import F, Max, Avg, Sum, Count, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncWeek

from .models import (
    sets,
    progress,
    workout_sessions,
    session_exercises,
    exercise,
    user_info,
)


WEEKLY = "weekly"


def _weekly_set_queryset_for_user(user_id):
    """
    Base queryset of sets for a given user, joined to session + exercise,
    excluding templates, warmups, and missing weights.
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


@transaction.atomic
def rebuild_progress_for_user(user_id):
    """
    Recompute WEEKLY progress rows for a single user from raw sets.

    - Groups by (user, exercise, week)
    - Calculates:
        * max_weight
        * avg_weight
        * total_volume (weight * reps)
        * workout_count (distinct sessions)
    - Writes into `progress` table (deletes existing weekly rows first)
    """

    # 1) Remove old weekly progress rows for this user
    progress.objects.filter(user_id=user_id, period_type=WEEKLY).delete()

    qs = _weekly_set_queryset_for_user(user_id)

    if not qs.exists():
        return 0  # no data to aggregate

    # Expression for volume: weight * reps
    volume_expr = ExpressionWrapper(
        F("weight") * F("reps"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    # 2) Aggregate by week + exercise
    weekly_stats = (
        qs.annotate(
            week_start=TruncWeek("session_exercise_id__session_id__session_date"),
            ex_id=F("session_exercise_id__exercise_id"),
        )
        .values("week_start", "ex_id")
        .annotate(
            max_weight=Max("weight"),
            avg_weight=Avg("weight"),
            total_volume=Sum(volume_expr),
            workout_count=Count("session_exercise_id__session_id", distinct=True),
        )
        .order_by("week_start", "ex_id")
    )

    # 3) Bulk create progress rows
    user_obj = user_info.objects.get(user_id=user_id)

    progress_rows = []
    for row in weekly_stats:
        progress_rows.append(
            progress(
                user_id=user_obj,                     # FK to user_info
                exercise_id=exercise.objects.get(pk=row["ex_id"]),
                date=row["week_start"],              # week start date
                period_type=WEEKLY,
                max_weight=row["max_weight"],
                avg_weight=row["avg_weight"],
                total_volume=row["total_volume"],
                workout_count=row["workout_count"],
            )
        )

    progress.objects.bulk_create(progress_rows)

    return len(progress_rows)
