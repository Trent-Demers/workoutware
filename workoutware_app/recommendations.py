"""
AI-Based Workout Recommendations for WorkoutWare.

This module analyzes a user's historical training data to generate
personalized exercise recommendations in two major categories:

1. **Weight Increase Recommendations**
   - Identifies exercises where the user's max weight has stalled.
   - Suggests specific next-step weight targets based on progress trends.

2. **Neglected Muscle Group Detection**
   - Analyzes the frequency of training sessions per muscle group.
   - Identifies muscles the user has not trained enough recently.

These recommendations are displayed in the Progress Dashboard.
The logic here is lightweight and rule-based but structured such that
future versions can integrate ML or deep-learning models.

Dependencies:
    - Django ORM
    - `progress` model (aggregated statistics)
    - `exercise` model (muscle group classification)

All functions in this module are pure functions:
They take a `user_id` and return structured dictionaries with
recommendations that can be directly rendered in templates.
"""

from django.db import connection
from datetime import date, timedelta


# ------------------------------------------------------------------------------
# INTERNAL HELPER FUNCTIONS
# ------------------------------------------------------------------------------

def _fetch_recent_progress(user_id):
    """
    Retrieve the user's weekly aggregated progress metrics for all exercises.

    Args:
        user_id (int): user_info primary key.

    Returns:
        list of dict:
            Each item contains:
                - exercise_id
                - exercise_name
                - max_weight
                - previous_max_weight
                - date
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.exercise_id,
                   e.name,
                   p.max_weight,
                   LAG(p.max_weight) OVER (PARTITION BY p.exercise_id ORDER BY p.date) AS prev_weight,
                   p.date
            FROM progress p
            JOIN exercise e ON p.exercise_id = e.exercise_id
            WHERE p.user_id = %s AND p.period_type = 'weekly'
            ORDER BY p.exercise_id, p.date DESC
            """,
            [user_id],
        )
        rows = cursor.fetchall()

    return [
        {
            "exercise_id": r[0],
            "exercise_name": r[1],
            "max_weight": float(r[2]) if r[2] else None,
            "previous_max_weight": float(r[3]) if r[3] else None,
            "date": r[4],
        }
        for r in rows
    ]


def _fetch_muscle_group_usage(user_id, weeks=4):
    """
    Compute how often the user has trained each muscle group in the past X weeks.

    Args:
        user_id (int)
        weeks (int): Time window for analysis.

    Returns:
        dict: {muscle_group_name: session_count}
    """
    start_date = date.today() - timedelta(weeks=weeks)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT e.subtype AS muscle_group,
                   COUNT(*) AS frequency
            FROM workout_sessions ws
            JOIN session_exercises se ON ws.session_id = se.session_id
            JOIN exercise e ON se.exercise_id = e.exercise_id
            WHERE ws.user_id = %s
              AND ws.completed = 1
              AND ws.session_date >= %s
            GROUP BY e.subtype
            """,
            [user_id, start_date],
        )
        rows = cursor.fetchall()

    return {row[0]: row[1] for row in rows}


# ------------------------------------------------------------------------------
# PUBLIC RECOMMENDATION FUNCTIONS
# ------------------------------------------------------------------------------

def recommend_weight_increases(user_id):
    """
    Analyze progress history to identify exercises where the user might
    increase weight based on stalled or slow progress.

    Logic:
        - If max weight has not increased for 2+ weeks → suggest adding 2.5–5 lbs.
        - If recent max_weight > previous → no suggestion needed.
        - If user has no data → skip.

    Args:
        user_id (int)

    Returns:
        list of dict:
            Each item has:
                - exercise_name
                - current_weight
                - previous_weight
                - recommended_weight
                - reason
    """
    progress_history = _fetch_recent_progress(user_id)
    recommendations = []

    grouped = {}
    for row in progress_history:
        grouped.setdefault(row["exercise_name"], []).append(row)

    for name, rows in grouped.items():
        if len(rows) < 2:
            continue  # not enough history

        current = rows[0]
        previous = rows[1]

        cur_w = current["max_weight"]
        prev_w = previous["max_weight"]

        if cur_w is None or prev_w is None:
            continue

        # If weight hasn't changed → progressive overload suggestion
        if abs(cur_w - prev_w) < 0.1:
            recommendations.append(
                {
                    "exercise_name": name,
                    "current_weight": cur_w,
                    "previous_weight": prev_w,
                    "recommended_weight": round(cur_w + 2.5, 1),
                    "reason": "No progress in 2 weeks — increase weight slightly.",
                }
            )

    return recommendations


def recommend_neglected_muscle_groups(user_id):
    """
    Identify muscle groups that the user has not trained enough recently.

    Logic:
        - Count sessions per muscle group in last 4 weeks.
        - Compare to expected baseline (e.g., trained at least 3 times).
        - Groups below baseline are considered neglected.

    Args:
        user_id (int)

    Returns:
        list of dict:
            Each item has:
                - muscle_group
                - frequency
                - recommended_action
    """
    usage = _fetch_muscle_group_usage(user_id, weeks=4)
    recommendations = []

    BASELINE = 3  # expected frequency in 4 weeks

    for group, freq in usage.items():
        if freq < BASELINE:
            recommendations.append(
                {
                    "muscle_group": group,
                    "frequency": freq,
                    "recommended_action": f"Add 1–2 more {group} exercises per week.",
                }
            )

    return recommendations


def get_workout_recommendations(user_id):
    """
    Produce a combined recommendation package for the user's dashboard.

    Args:
        user_id (int)

    Returns:
        dict:
            {
                "weight_increase": [...],
                "neglected_muscle_groups": [...]
            }
    """
    return {
        "weight_increase": recommend_weight_increases(user_id),
        "neglected_muscle_groups": recommend_neglected_muscle_groups(user_id),
    }
