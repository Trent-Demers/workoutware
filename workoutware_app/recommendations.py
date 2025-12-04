from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from .models import (
    sets,
    session_exercises,
    workout_sessions,
    exercise,
    exercise_target_association,
    target,
)


# 1) Increase weight suggestions (when user completes goal reps 3x (in 3 sets))
WEIGHT_INCREASE_PERCENT = 2.5  
MIN_CONSECUTIVE_SETS = 3       # must hit target on this many sets


def get_weight_increase_recommendations(user_id):
    """
    For each session_exercise, if the user hit target_reps on the last
    MIN_CONSECUTIVE_SETS working sets, suggest a small weight increase.
    """

    # look at recent working sets for this user (not templates)
    recent_sets = (
        sets.objects
        .filter(
            session_exercise_id__session_id__user_id=user_id,
            session_exercise_id__session_id__is_template=False,
            completed=True,
            is_warmup=False,
        )
        .select_related(
            "session_exercise_id",
            "session_exercise_id__exercise_id",
            "session_exercise_id__session_id",
        )
        .order_by("-completion_time")
    )

    # group sets by session_exercise
    by_session_exercise = defaultdict(list)
    for s in recent_sets:
        by_session_exercise[s.session_exercise_id_id].append(s)

    recommendations = []

    for se_id, se_sets in by_session_exercise.items():
        # take latest N sets
        last_sets = se_sets[:MIN_CONSECUTIVE_SETS]
        if len(last_sets) < MIN_CONSECUTIVE_SETS:
            continue

        se = last_sets[0].session_exercise_id          # session_exercises instance
        ex = se.exercise_id                            # exercise instance
        target_reps = se.target_reps

        if target_reps is None:
            continue

        # check if user hit target reps on all these sets
        if not all((s.reps or 0) >= target_reps for s in last_sets):
            continue

        current_weight = float(last_sets[0].weight or 0.0)
        if current_weight <= 0:
            continue

        suggested_weight = round(
            current_weight * (1 + WEIGHT_INCREASE_PERCENT / 100.0), 2
        )

        recommendations.append({
            "exercise_name": ex.name,
            "current_weight": current_weight,
            "suggested_weight": suggested_weight,
            "target_reps": target_reps,
            "num_sets": MIN_CONSECUTIVE_SETS,
            "message": (
                f"For {ex.name}, you hit at least {target_reps} reps on your last "
                f"{MIN_CONSECUTIVE_SETS} working sets at {current_weight} lbs. "
                f"Consider increasing to ~{suggested_weight} lbs next time."
            ),
        })

    return recommendations




# 2) Neglected muscle group recommendations
LOOKBACK_DAYS = 30


def get_neglected_muscle_group_recommendations(user_id, lookback_days=LOOKBACK_DAYS):
    """
    Use exercise_target_association + target tables to find muscle groups with
    low or zero training volume in the last `lookback_days` days.
    """

    start_date = timezone.now().date() - timedelta(days=lookback_days)

    # all working sets for this user in the lookback window
    sets_qs = (
        sets.objects
        .filter(
            session_exercise_id__session_id__user_id=user_id,
            session_exercise_id__session_id__session_date__gte=start_date,
            session_exercise_id__session_id__is_template=False,
            completed=True,
            is_warmup=False,
        )
        .select_related(
            "session_exercise_id",
            "session_exercise_id__exercise_id",
        )
    )

    volume_by_group = defaultdict(float)

    for s in sets_qs:
        ex = s.session_exercise_id.exercise_id

        # all target rows for this exercise
        targets = (
            exercise_target_association.objects
            .filter(exercise_id=ex)
            .select_related("target_id")
        )

        if not targets:
            continue

        set_volume = float(s.weight or 0.0) * (s.reps or 0)
        if set_volume <= 0:
            continue

        share = set_volume / len(targets)

        for assoc in targets:
            group = assoc.target_id.target_group  # <- your model
            volume_by_group[group] += share

    # all groups that exist in DB
    from .models import target  # imported here to avoid circular imports
    all_groups = set(target.objects.values_list("target_group", flat=True))

    neglected_groups = []
    messages = []

    # groups never trained in this window
    never_trained = sorted(all_groups - set(volume_by_group.keys()))
    for g in never_trained:
        neglected_groups.append(g)
        messages.append(
            f"You haven't trained **{g}** in the last {lookback_days} days."
        )

    # among trained groups, mark significantly low volume
    if volume_by_group:
        max_vol = max(volume_by_group.values())
        threshold = max_vol * 0.3  # < 30% of top group

        low_vol_groups = sorted(
            [g for g, v in volume_by_group.items() if v < threshold]
        )
        for g in low_vol_groups:
            neglected_groups.append(g)
            messages.append(
                f"Your total volume for **{g}** is much lower than your main muscle groups."
            )

    # dedupe while keeping order
    seen = set()
    unique_groups = []
    for g in neglected_groups:
        if g not in seen:
            unique_groups.append(g)
            seen.add(g)

    return {
        "groups": unique_groups,
        "messages": messages,
        "lookback_days": lookback_days,
    }




# HELPER FUNCTION
def get_workout_recommendations(user_id):
    weight_recs = get_weight_increase_recommendations(user_id)
    neglected_recs = get_neglected_muscle_group_recommendations(user_id)

    return {
        "weight_increase": weight_recs,
        "neglected_muscle_groups": neglected_recs,
    }
