"""
Workout Recommendations for WorkoutWare.

This module analyzes a user's historical training data to generate
personalized exercise recommendations in two major categories:

1. Weight Increase Recommendations
   - Identifies exercises where the user has hit target reps consistently.
   - Suggests percentage-based weight increases to promote progressive overload.

2. Neglected Muscle Group Detection
   - Analyzes training volume distribution across muscle groups.
   - Identifies muscles with zero or low volume relative to the user's main focus.

These recommendations are displayed in the Progress Dashboard.
The logic here is lightweight and rule-based but structured such that
future versions can integrate ML or deep-learning models.

Dependencies:
    - Django ORM
    - `sets` model (individual set logs)
    - `exercise` model (muscle group classification)
    - `exercise_target_association` + `target` (muscle group mappings)

All functions in this module are pure functions:
They take a `user_id` and return structured dictionaries with
recommendations that can be directly rendered in templates.
"""

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


# ------------------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------------------

# Weight increase recommendation parameters
WEIGHT_INCREASE_PERCENT = 2.5  # Percentage to add when user hits targets
MIN_CONSECUTIVE_SETS = 3       # Must hit target reps on this many recent sets

# Neglected muscle group parameters
LOOKBACK_DAYS = 30  # Time window for muscle group analysis


# ------------------------------------------------------------------------------
# PUBLIC RECOMMENDATION FUNCTIONS
# ------------------------------------------------------------------------------

def get_weight_increase_recommendations(user_id):
    """
    Analyze recent set performance to identify exercises where the user might
    increase weight based on consistent achievement of target reps.

    Logic:
        - For each session_exercise, examine the last N working sets
        - If user hit target_reps on all N consecutive sets → suggest weight increase
        - Increase is percentage-based (promotes progressive overload)
        - Only considers completed, non-warmup sets

    Args:
        user_id (int): User identifier.

    Returns:
        list of dict:
            Each item contains:
                - exercise_name: Name of the exercise
                - current_weight: Current working weight
                - suggested_weight: Recommended next weight
                - target_reps: Rep target being used
                - num_sets: Number of consecutive sets analyzed
                - message: Detailed recommendation text
    """
    # Look at recent working sets for this user (not templates)
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

    # Group sets by session_exercise
    by_session_exercise = defaultdict(list)
    for s in recent_sets:
        by_session_exercise[s.session_exercise_id_id].append(s)

    recommendations = []

    for se_id, se_sets in by_session_exercise.items():
        # Take latest N sets
        last_sets = se_sets[:MIN_CONSECUTIVE_SETS]
        if len(last_sets) < MIN_CONSECUTIVE_SETS:
            continue

        se = last_sets[0].session_exercise_id  # session_exercises instance
        ex = se.exercise_id                    # exercise instance
        target_reps = se.target_reps

        if target_reps is None:
            continue

        # Check if user hit target reps on all these sets
        if not all((s.reps or 0) >= target_reps for s in last_sets):
            continue

        current_weight = float(last_sets[0].weight or 0.0)
        if current_weight <= 0:
            continue

        # Calculate percentage-based weight increase
        suggested_weight = round(
            current_weight * (1 + WEIGHT_INCREASE_PERCENT / 100.0), 2
        )

        if not any(rec['exercise_name'] == ex.name for rec in recommendations):

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


def get_neglected_muscle_group_recommendations(user_id, lookback_days=LOOKBACK_DAYS):
    """
    Identify muscle groups that the user has not trained enough recently
    based on training volume distribution.

    Logic:
        - Calculate total volume per muscle group over lookback period
        - Volume is distributed across target muscles using exercise_target_association
        - Identify groups with zero training (never trained)
        - Identify groups with low volume (<30% of highest volume group)
        - Return unique list of neglected groups with explanatory messages

    Args:
        user_id (int): User identifier.
        lookback_days (int, optional): Time window for analysis. Defaults to 30.

    Returns:
        dict:
            {
                "groups": List of neglected muscle group names,
                "messages": Corresponding messages for each group,
                "lookback_days": The lookback period used
            }
    """
    start_date = timezone.now().date() - timedelta(days=lookback_days)

    # All working sets for this user in the lookback window
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

    # Accumulate volume by muscle group
    volume_by_group = defaultdict(float)

    for s in sets_qs:
        ex = s.session_exercise_id.exercise_id

        # Get all target muscle groups for this exercise
        targets = (
            exercise_target_association.objects
            .filter(exercise_id=ex)
            .select_related("target_id")
        )

        if not targets:
            continue

        # Calculate set volume (weight × reps)
        set_volume = float(s.weight or 0.0) * (s.reps or 0)
        if set_volume <= 0:
            continue

        # Distribute volume equally among all target muscles
        share = set_volume / len(targets)

        for assoc in targets:
            group = assoc.target_id.target_group
            volume_by_group[group] += share

    # Get all muscle groups that exist in database
    from .models import target  # Imported here to avoid circular imports
    all_groups = set(target.objects.values_list("target_group", flat=True))

    neglected_groups = []
    messages = []

    # ----------------------------------------------------------------------
    # Detection 1: Groups never trained in this window
    # ----------------------------------------------------------------------
    never_trained = sorted(all_groups - set(volume_by_group.keys()))
    for g in never_trained:
        neglected_groups.append(g)
        messages.append(
            f"You haven't trained {g} in the last {lookback_days} days."
        )

    # ----------------------------------------------------------------------
    # Detection 2: Groups with significantly low volume
    # ----------------------------------------------------------------------
    if volume_by_group:
        max_vol = max(volume_by_group.values())
        threshold = max_vol * 0.3  # Less than 30% of top group

        low_vol_groups = sorted(
            [g for g, v in volume_by_group.items() if v < threshold]
        )
        for g in low_vol_groups:
            neglected_groups.append(g)
            messages.append(
                f"Your total volume for {g} is much lower than your main muscle groups."
            )

    # ----------------------------------------------------------------------
    # Deduplicate while preserving order
    # ----------------------------------------------------------------------
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


def get_workout_recommendations(user_id):
    """
    Produce a combined recommendation package for the user's dashboard.

    Args:
        user_id (int): User identifier.

    Returns:
        dict:
            {
                "weight_increase": List of weight increase recommendations,
                "neglected_muscle_groups": Dict with neglected muscle group info
            }
    """
    weight_recs = get_weight_increase_recommendations(user_id)
    neglected_recs = get_neglected_muscle_group_recommendations(user_id)

    return {
        "weight_increase": weight_recs,
        "neglected_muscle_groups": neglected_recs,
    }