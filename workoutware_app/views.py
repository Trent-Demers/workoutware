"""
Views for the WorkoutWare application.

This module handles all presentation logic and request–response flow
across the WorkoutWare system. It includes:

1. **Dashboard Views**
   - Admin dashboard with platform-wide analytics
   - User dashboard with PRs, streaks, and weekly progress

2. **Exercise Management**
   - Add new exercises to the global catalog
   - Edit or delete existing exercises

3. **Workout Session Management**
   - Create workout sessions
   - Add exercises to a session
   - Log sets with weight validation & PR detection
   - Save sessions as templates or delete them
   - Mark sessions as complete

4. **Goals & Body Stats**
   - Create and update fitness goals
   - Log and visualize body measurements

5. **Progress Tracking**
   - Daily/weekly aggregated metrics
   - Charts for volume, max weight, and reps
   - AI workout recommendations

This file interacts closely with:
- models.py
- recommendations.py
- progress_utils.py
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db import connection
from django.db.models import Count, Avg, Max, Sum, Q
from django.http import JsonResponse
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from .models import (
    user_info,
    exercise,
    workout_sessions,
    session_exercises,
    sets,
    data_validation,
    progress,
    user_pb,
    goals,
    user_stats_log,
    target,
    exercise_target_association,
    workout_goal_link,
)
from .recommendations import get_workout_recommendations
from .progress_utils import rebuild_progress_for_user


# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

def get_or_create_user_record(request_user):
    """
    Ensures the authenticated Django user also exists in user_info table.
    Inserts all required fields to satisfy MySQL constraints.
    """
    try:
        return user_info.objects.get(username=request_user.username)

    except user_info.DoesNotExist:
        return user_info.objects.create(
            first_name=request_user.first_name or "",
            last_name=request_user.last_name or "",
            email=request_user.email,
            username=request_user.username,
            password_hash="django_managed",  # placeholder
            date_registered=timezone.now().date(),
            registered=True,
            user_type="user",
            fitness_goal="",
            town="",
            state="",
            country=""
        )



def calculate_workout_streak(user_id):
    """
    Compute how many consecutive days the user has completed workouts.

    Args:
        user_id (int): Internal user_info ID.

    Returns:
        int: Number of consecutive workout days.
    """
    sessions = workout_sessions.objects.filter(
        user_id=user_id,
        completed=True,
        is_template=False,
    ).order_by("-session_date").values_list("session_date", flat=True)

    if not sessions:
        return 0

    dates = list(sessions)
    streak = 1

    for i in range(len(dates) - 1):
        if (dates[i] - dates[i + 1]).days == 1:
            streak += 1
        else:
            break

    return streak


def get_exercise_suggestions(user_id):
    """
    Suggest up to 5 exercises the user hasn’t performed recently.

    Args:
        user_id (int): user_info ID.

    Returns:
        QuerySet: Random unused exercises.
    """
    recent = session_exercises.objects.filter(
        session_id__user_id=user_id,
        session_id__is_template=False,
        session_id__session_date__gte=date.today() - timedelta(days=7),
    ).values_list("exercise_id", flat=True)

    return exercise.objects.exclude(exercise_id__in=recent).order_by("?")[:5]


def check_and_record_pr(user_id, exercise_id, weight, reps, set_obj):
    """
    Determine whether a logged set creates a new personal record (PR)
    and store it if needed.

    Args:
        user_id (int): user_info ID.
        exercise_id (int)
        weight (Decimal)
        reps (int)
        set_obj (sets): Newly saved set instance.

    Returns:
        (bool, Decimal or None): Whether a PR occurred, and previous PR.
    """
    existing = user_pb.objects.filter(
        user_id=user_id, exercise_id=exercise_id, pr_type="max_weight"
    ).first()

    if existing and weight <= existing.pb_weight:
        return False, None  # No PR

    previous = existing.pb_weight if existing else None

    # Create new PR entry
    user_pb.objects.create(
        user_id=user_info.objects.get(user_id=user_id),
        exercise_id=exercise.objects.get(exercise_id=exercise_id),
        pr_type="max_weight",
        pb_weight=weight,
        pb_reps=reps,
        pb_date=date.today(),
        previous_pr=previous,
        notes=f"Set ID: {set_obj.set_id}",
    )

    return True, previous


def validate_weight_input(user_id, exercise_id, weight):
    """
    Categorize a weight input based on user’s history using:
    - Outlier detection
    - New PR prediction
    - Suspiciously low values
    - First-time exercise

    Args:
        user_id (int)
        exercise_id (int)
        weight (Decimal)

    Returns:
        dict: {flag, message, expected_max}
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT MAX(s.weight), AVG(s.weight)
            FROM sets s
            JOIN session_exercises se ON s.session_exercise_id = se.session_exercise_id
            JOIN workout_sessions ws ON se.session_id = ws.session_id
            WHERE ws.user_id = %s AND se.exercise_id = %s
              AND s.weight IS NOT NULL AND ws.is_template = 0
            """,
            [user_id, exercise_id],
        )
        max_w, avg_w = cursor.fetchone()

    if max_w is None:
        return {
            "flag": "first_time",
            "message": "🌟 First time logging this exercise!",
            "expected_max": None,
        }

    max_w = Decimal(str(max_w))
    avg_w = Decimal(str(avg_w))

    if weight > max_w * Decimal("1.15"):
        return {
            "flag": "outlier",
            "message": f"⚠️ {weight} lbs is unusually high vs max {max_w}.",
            "expected_max": max_w,
        }

    if weight > max_w:
        return {
            "flag": "new_pr",
            "message": f"🎉 NEW PR! {weight} lbs beats previous max {max_w}!",
            "expected_max": max_w,
        }

    if weight < avg_w * Decimal("0.7"):
        return {
            "flag": "suspicious_low",
            "message": f"⚠️ {weight} lbs is very low compared to your average {avg_w}.",
            "expected_max": max_w,
        }

    return {
        "flag": "normal",
        "message": "✓ Looks good!",
        "expected_max": max_w,
    }


# ------------------------------------------------------------------------------
# DASHBOARD VIEWS
# ------------------------------------------------------------------------------

@login_required
def home(request):
    """
    Render either:
    - **Admin dashboard** with platform statistics, OR
    - **User dashboard** showing PRs, goals, streaks, and workout counts.

    Returns:
        HttpResponse
    """
    user = request.user

    # ---------------------------------------------
    # ADMIN DASHBOARD
    # ---------------------------------------------
    if user.is_superuser:
        total_users = user_info.objects.count()
        total_exercises = exercise.objects.count()
        total_workouts = workout_sessions.objects.filter(
            completed=True, is_template=False
        ).count()

        # Active users today
        active_today = (
            workout_sessions.objects.filter(
                session_date=date.today(),
                completed=True,
                is_template=False,
            )
            .values("user_id")
            .distinct()
            .count()
        )

        # Recently registered users
        recent_users = user_info.objects.order_by("-date_registered")[:6]
        exercises = exercise.objects.all()

        # Popular exercises by usage
        popular_exercises = exercise.objects.annotate(
            usage=Count(
                "session_exercises",
                filter=Q(session_exercises__session_id__is_template=False),
            )
        ).order_by("-usage")[:5]

        return render(
            request,
            "admin_dashboard.html",
            {
                "total_users": total_users,
                "total_exercises": total_exercises,
                "total_workouts": total_workouts,
                "active_today": active_today,
                "recent_users": recent_users,
                "exercises": exercises,
                "popular_exercises": popular_exercises,
            },
        )

    # ---------------------------------------------
    # USER DASHBOARD
    # ---------------------------------------------
    user_record = get_or_create_user_record(user)
    uid = user_record.user_id

    streak = calculate_workout_streak(uid)

    # Recent PRs
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT e.name, pb.pb_weight, pb.pb_date, pb.previous_pr
            FROM user_pb pb
            JOIN exercise e ON pb.exercise_id = e.exercise_id
            WHERE pb.user_id = %s
              AND pb.pr_id IN (
                SELECT MAX(pr_id) FROM user_pb
                WHERE user_id = %s GROUP BY exercise_id
              )
            ORDER BY pb.pb_date DESC LIMIT 5
            """,
            [uid, uid],
        )
        pr_rows = cursor.fetchall()

    recent_prs = [
        {
            "exercise_name": r[0],
            "pb_weight": r[1],
            "pb_date": r[2],
            "previous_pr": r[3],
            "improvement": (r[1] - r[3]) if r[3] else 0,
        }
        for r in pr_rows
    ]

    # Active goals
    active_goals = goals.objects.filter(user_id=user_record, status="active").select_related(
        "exercise_id"
    ).order_by("-start_date")

    # Update goal progress
    for g in active_goals:
        if g.exercise_id:
            latest = (
                user_pb.objects.filter(
                    user_id=uid, exercise_id=g.exercise_id, pr_type="max_weight"
                )
                .order_by("-pb_date")
                .first()
            )
            g.current_value = latest.pb_weight if latest else 0
            g.save(update_fields=["current_value"])

    # Weekly workout count
    week_start = date.today() - timedelta(days=date.today().weekday())

    workouts_this_week = workout_sessions.objects.filter(
        user_id=uid,
        session_date__gte=week_start,
        is_template=False,
        completed=True,
    ).count()

    total_workouts = workout_sessions.objects.filter(
        user_id=uid, is_template=False, completed=True
    ).count()

    return render(
        request,
        "user_dashboard.html",
        {
            "streak_days": streak,
            "recent_prs": recent_prs,
            "active_goals": active_goals,
            "workouts_this_week": workouts_this_week,
            "total_workouts": total_workouts,
        },
    )


# ------------------------------------------------------------------------------
# EXERCISE MANAGEMENT
# ------------------------------------------------------------------------------

@login_required
def add_exercise(request):
    """
    Admin-only: Add a new exercise to the global catalog.

    Returns:
        Redirect to homepage.
    """
    if not request.user.is_superuser:
        return redirect("/")

    name = request.POST.get("exercise_name")
    type = request.POST.get("exercise_type")
    subtype = request.POST.get("exercise_subtype")
    equipment = request.POST.get("exercise_equipment")
    difficulty = request.POST.get("exercise_difficulty")
    description = request.POST.get("exercise_description")
    demo = request.POST.get("exercise_demo")

    new_exercise = exercise.objects.create(
        name=name,
        type=type,
        subtype=subtype,
        equipment=equipment,
        difficulty=difficulty,
        description=description,
        demo_link=demo,
    )

    new_exercise.save()
    return redirect("/")


@login_required
def edit_exercise(request, exercise_id):
    """
    Admin-only: Edit an existing exercise.

    Args:
        exercise_id (int): exercise.exercise_id

    Returns:
        Redirect to homepage.
    """
    if not request.user.is_superuser:
        return redirect("/")

    ex = get_object_or_404(exercise, exercise_id=exercise_id)

    ex.name = request.POST.get("exercise_name")
    ex.type = request.POST.get("exercise_type")
    ex.subtype = request.POST.get("exercise_subtype")
    ex.equipment = request.POST.get("exercise_equipment")
    ex.difficulty = request.POST.get("exercise_difficulty")
    ex.description = request.POST.get("exercise_description")
    ex.demo_link = request.POST.get("exercise_demo")
    ex.save()

    return redirect("/")


@login_required
def delete_exercise(request, exercise_id):
    """
    Admin-only: Delete an exercise from global catalog.

    Args:
        exercise_id (int)

    Returns:
        Redirect to dashboard.
    """
    if not request.user.is_superuser:
        return redirect("/")

    get_object_or_404(exercise, exercise_id=exercise_id).delete()
    return redirect("/")


# ------------------------------------------------------------------------------
# WORKOUT SESSION FLOW
# ------------------------------------------------------------------------------

@login_required
def log_workout(request):
    """
    Display main workout logging interface.

    Shows:
        - Exercise dropdown
        - Recent unfinished sessions
        - Saved templates
        - Active goals
        - Suggested exercises

    Returns:
        HttpResponse
    """
    user_record = get_or_create_user_record(request.user)
    uid = user_record.user_id

    exercises_list = exercise.objects.all()

    recent_sessions = workout_sessions.objects.filter(
        user_id=uid, completed=False, is_template=False
    ).order_by("-session_date", "-session_id")[:5]

    templates = workout_sessions.objects.filter(
        user_id=uid, is_template=True
    ).order_by("-session_id")

    suggestions = get_exercise_suggestions(uid)

    active_goals = goals.objects.filter(user_id=uid, status="active")

    return render(
        request,
        "log_workout.html",
        {
            "exercises": exercises_list,
            "recent_sessions": recent_sessions,
            "templates": templates,
            "active_goals": active_goals,
            "suggestions": suggestions,
            "today": date.today(),
        },
    )


@login_required
def create_workout_session(request):
    """
    Create a new workout session for the user.

    If goal_id is provided, link the session to that goal.

    Returns:
        Redirect to add_exercises_to_session page.
    """
    if request.method != "POST":
        return redirect("log_workout")

    user_record = get_or_create_user_record(request.user)
    goal_id = request.POST.get("goal_id")

    new_session = workout_sessions.objects.create(
        user_id=user_record,
        session_name=request.POST.get("session_name"),
        session_date=request.POST.get("session_date", date.today()),
        start_time=request.POST.get("start_time") or None,
        bodyweight=request.POST.get("bodyweight") or None,
        completed=False,
        is_template=False,
    )

    # Link goal if provided
    if goal_id:
        try:
            g = goals.objects.get(goal_id=goal_id, user_id=user_record)

            # Convert session_date to date object
            if isinstance(new_session.session_date, str):
                session_date = datetime.strptime(new_session.session_date, "%Y-%m-%d").date()
            else:
                session_date = new_session.session_date

            # Convert start_time to time object
            if new_session.start_time:
                if isinstance(new_session.start_time, str):
                    start_time = datetime.strptime(new_session.start_time, "%H:%M").time()
                else:
                    start_time = new_session.start_time
            else:
                start_time = None
                        
            if new_session.start_time:
                # Use session_date + start_time
                session_dt = datetime.combine(session_date, start_time)
            else:
                # Default to current full datetime
                now_dt = timezone.now()
                # Convert to naive for MySQL
                session_dt = timezone.make_naive(now_dt, timezone.get_current_timezone())
            
            workout_goal_link.objects.create(
                user_id=user_record, goal=g, session=new_session, created_at=session_dt
            )
        except goals.DoesNotExist:
            pass

    return redirect("add_exercises_to_session", session_id=new_session.session_id)


@login_required
def complete_workout(request, session_id):
    """
    Mark a workout session as complete.

    Args:
        session_id (int)

    Returns:
        Redirect back to workout log.
    """
    if request.method == "POST":
        s = get_object_or_404(workout_sessions, session_id=session_id)
        s.completed = True
        s.save()

    return redirect("log_workout")


@login_required
def completed_workouts(request):
    """
    Display all completed workouts for the user.
    """
    user_record = get_or_create_user_record(request.user)

    sessions = workout_sessions.objects.filter(
        user_id=user_record,
        completed=True,
        is_template=False,
    ).order_by("-session_date", "-start_time")

    return render(request, "completed_workouts.html", {"sessions": sessions})


@login_required
def completed_workouts_week(request):
    """
    Display completed workouts in the current week.

    Returns:
        HttpResponse
    """
    user_record = get_or_create_user_record(request.user)

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())

    sessions = workout_sessions.objects.filter(
        user_id=user_record,
        completed=True,
        is_template=False,
        session_date__gte=week_start,
        session_date__lte=today,
    ).order_by("-session_date")

    return render(
        request, "completed_workouts_week.html", {"sessions": sessions}
    )


@login_required
def use_template(request, template_id):
    """
    Duplicate a template session into a new workout session.

    Steps:
        - Load template
        - Create new session
        - Copy exercises but NOT sets
        - Redirect user to session page

    Returns:
        Redirect to add_exercises_to_session
    """
    template = get_object_or_404(
        workout_sessions, session_id=template_id, is_template=True
    )

    user_record = get_or_create_user_record(request.user)

    if request.method == "POST":
        name = request.POST.get(
            "session_name", template.session_name.replace(" (Template)", "")
        )

        new_session = workout_sessions.objects.create(
            user_id=user_record,
            session_name=name,
            session_date=date.today(),
            is_template=False,
        )

        # Copy exercises
        for te in session_exercises.objects.filter(session_id=template):
            session_exercises.objects.create(
                session_id=new_session,
                exercise_id=te.exercise_id,
                exercise_order=te.exercise_order,
                target_sets=te.target_sets,
                target_reps=te.target_reps,
            )

        return redirect(
            "add_exercises_to_session", session_id=new_session.session_id
        )

    return redirect("log_workout")


@login_required
def save_as_template(request, session_id):
    """
    Convert a completed workout session into a reusable template.

    Returns:
        Redirect to log_workout
    """
    if request.method != "POST":
        return redirect("log_workout")

    session = get_object_or_404(workout_sessions, session_id=session_id)

    tmpl = workout_sessions.objects.create(
        user_id=session.user_id,
        session_name=f"{session.session_name} (Template)",
        session_date=date.today(),
        is_template=True,
    )

    for s in session_exercises.objects.filter(session_id=session):
        session_exercises.objects.create(
            session_id=tmpl,
            exercise_id=s.exercise_id,
            exercise_order=s.exercise_order,
            target_sets=s.target_sets,
            target_reps=s.target_reps,
        )

    return redirect("log_workout")


@login_required
def delete_template(request, template_id):
    """
    Delete a template session.

    Returns:
        Redirect to log_workout
    """
    if request.method == "POST":
        get_object_or_404(
            workout_sessions, session_id=template_id, is_template=True
        ).delete()

    return redirect("log_workout")


@login_required
def delete_workout(request, session_id):
    """
    Delete a non-template workout session.

    Returns:
        Redirect to log_workout
    """
    if request.method == "POST":
        get_object_or_404(
            workout_sessions, session_id=session_id, is_template=False
        ).delete()

    return redirect("log_workout")


@login_required
def rename_workout(request, session_id):
    """
    AJAX endpoint to rename a workout session.

    Returns:
        JsonResponse {success: bool}
    """
    if request.method == "POST":
        session = get_object_or_404(workout_sessions, session_id=session_id)
        new_name = request.POST.get("session_name", "").strip()

        if not new_name:
            return JsonResponse(
                {"success": False, "error": "Name cannot be empty"}, status=400
            )

        session.session_name = new_name
        session.save()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def add_exercises_to_session(request, session_id):
    """
    Display and manage exercises within a workout session.

    Shows:
        - All exercises already added
        - Logged sets per exercise
        - Dropdown to add more exercises

    Returns:
        HttpResponse
    """
    session = get_object_or_404(workout_sessions, session_id=session_id)

    exercises_list = exercise.objects.all()

    all_session_ex = (
        session_exercises.objects.filter(session_id=session_id)
        .select_related("exercise_id")
        .order_by("exercise_order")
    )

    session_data = [
        {
            "session_exercise": se,
            "sets": sets.objects.filter(
                session_exercise_id=se.session_exercise_id
            ).order_by("set_number"),
        }
        for se in all_session_ex
    ]

    return render(
        request,
        "add_exercises.html",
        {
            "session": session,
            "exercises": exercises_list,
            "session_data": session_data,
        },
    )


@login_required
def add_exercise_to_session(request, session_id):
    """
    Insert a new exercise into an existing workout session.

    Returns:
        Redirect to session editing page.
    """
    if request.method == "POST":
        ex_id = request.POST.get("exercise_id")
        target_sets = request.POST.get("target_sets", 3)
        target_reps = request.POST.get("target_reps", 10)

        order = session_exercises.objects.filter(
            session_id=session_id
        ).count() + 1

        session_exercises.objects.create(
            session_id=get_object_or_404(workout_sessions, session_id=session_id),
            exercise_id=get_object_or_404(exercise, exercise_id=ex_id),
            exercise_order=order,
            target_sets=target_sets,
            target_reps=target_reps,
        )

    return redirect("add_exercises_to_session", session_id=session_id)


@login_required
def log_set(request, session_exercise_id):
    """
    Log a set (weight × reps × RPE) for a particular exercise in a session.

    Features:
        - Intelligent weight validation
        - PR detection
        - Data validation logging

    Returns:
        HttpResponse confirmation page
    """
    if request.method != "POST":
        return redirect("log_workout")

    weight = Decimal(request.POST.get("weight", "0"))
    reps = int(request.POST.get("reps", 0))
    rpe = int(request.POST.get("rpe", 5))
    set_number = int(request.POST.get("set_number", 1))

    se = get_object_or_404(session_exercises, session_exercise_id=session_exercise_id)
    ex = se.exercise_id
    session = se.session_id
    user_record = session.user_id

    # Validate weight
    validation = validate_weight_input(
        user_record.user_id, ex.exercise_id, weight
    )

    # Save set
    new_set = sets.objects.create(
        session_exercise_id=se,
        set_number=set_number,
        weight=weight if weight > 0 else None,
        reps=reps,
        rpe=rpe,
        completion_time=datetime.now(),
    )

    # PR check
    is_pr = False
    prev_pr = None
    if weight > 0:
        is_pr, prev_pr = check_and_record_pr(
            user_record.user_id,
            ex.exercise_id,
            weight,
            reps,
            new_set
        )

    # Log validation
    data_validation.objects.create(
        user_id=user_record,
        set_id=new_set,
        exercise_id=ex,
        input_weight=weight,
        expected_max=validation.get("expected_max"),
        flagged_as=validation["flag"],
        timestamp=datetime.now()
    )

    return render(
        request,
        "set_logged.html",
        {
            "validation": validation,
            "set": new_set,
            "is_pr": is_pr,
            "previous_pr": prev_pr,
            "exercise_name": ex.name,
            "session_exercise_id": session_exercise_id,
            "session_id": session.session_id,
        }
    )


# ------------------------------------------------------------------------------
# PROGRESS & ANALYTICS
# ------------------------------------------------------------------------------

@login_required
def view_progress(request):
    """
    Render the user's progress dashboard.
    Includes:
        - Recent PRs
        - Validation warnings
        - Top exercises by volume
        - Weekly charts
        - Bodyweight trends
        - AI-based recommendations

    Returns:
        HttpResponse
    """
    user_record = get_or_create_user_record(request.user)
    uid = user_record.user_id

    # Rebuild progress table (ensures chart accuracy)
    rebuild_progress_for_user(uid)

    # Progress rows
    progress_rows = progress.objects.filter(user_id=uid).select_related(
        "exercise_id"
    ).order_by("-date")[:20]

    # Recent validations
    validations = data_validation.objects.filter(
        user_id=uid
    ).order_by("-timestamp")[:10]

    # Top exercises by training volume
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT e.exercise_id, e.name,
                   SUM(s.weight * s.reps) AS total_volume
            FROM exercise e
            JOIN session_exercises se ON e.exercise_id = se.exercise_id
            JOIN sets s ON se.session_exercise_id = s.session_exercise_id
            JOIN workout_sessions ws ON se.session_id = ws.session_id
            WHERE ws.user_id = %s
              AND s.weight IS NOT NULL
              AND ws.is_template = 0
            GROUP BY e.exercise_id, e.name
            ORDER BY total_volume DESC
            LIMIT 5
            """,
            [uid],
        )
        top_exercises = cursor.fetchall()

    # Weekly trends for each top exercise
    exercise_trends = {}
    for ex_id, name, _ in top_exercises:
        rows = progress.objects.filter(
            user_id=uid, exercise_id=ex_id, period_type="weekly"
        ).order_by("date")[:8]

        exercise_trends[name] = {
            "dates": [p.date.strftime("%m/%d") for p in rows],
            "max_weights": [float(p.max_weight or 0) for p in rows],
            "volumes": [float(p.total_volume or 0) for p in rows],
        }

    # Bodyweight trend
    logs = user_stats_log.objects.filter(user_id=uid).order_by("date")[:30]
    bodyweight_trend = {
        "dates": [l.date.strftime("%m/%d") for l in logs],
        "weights": [float(l.weight) for l in logs],
    }

    recs = get_workout_recommendations(uid)

    return render(
        request,
        "progress.html",
        {
            "progress_data": progress_rows,
            "validations": validations,
            "exercise_trends": json.dumps(exercise_trends),
            "bodyweight_trend": json.dumps(bodyweight_trend),
            "user_exercises": exercise.objects.filter(
                session_exercises__session_id__user_id=uid,
                session_exercises__session_id__is_template=False,
            )
            .distinct()
            .values_list("exercise_id", "name"),
            "weight_increase_recs": recs["weight_increase"],
            "neglected_muscle_group_recs": recs["neglected_muscle_groups"],
        },
    )


@login_required
def get_exercise_data(request, exercise_id):
    """
    API endpoint returning time-series metrics for a specific exercise.

    Includes:
        - Max weight per session
        - Average reps
        - Total volume

    Returns:
        JsonResponse
    """
    user_record = get_or_create_user_record(request.user)
    uid = user_record.user_id

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT ws.session_date,
                   MAX(s.weight),
                   AVG(s.reps),
                   SUM(s.weight * s.reps)
            FROM workout_sessions ws
            JOIN session_exercises se ON ws.session_id = se.session_id
            JOIN sets s ON se.session_exercise_id = s.session_exercise_id
            WHERE ws.user_id = %s
              AND se.exercise_id = %s
              AND s.weight IS NOT NULL
              AND ws.is_template = 0
            GROUP BY ws.session_date
            ORDER BY ws.session_date ASC
            LIMIT 20
            """,
            [uid, exercise_id],
        )
        results = cursor.fetchall()

    data = {
        "dates": [row[0].strftime("%m/%d") for row in results],
        "max_weights": [float(row[1] or 0) for row in results],
        "avg_reps": [float(row[2] or 0) for row in results],
        "total_volume": [float(row[3] or 0) for row in results],
    }

    return JsonResponse(data)


# ------------------------------------------------------------------------------
# GOAL MANAGEMENT
# ------------------------------------------------------------------------------

@login_required
def manage_goals(request):
    """
    Display and create user fitness goals.

    Returns:
        HttpResponse
    """
    user_record = get_or_create_user_record(request.user)
    uid = user_record.user_id

    # Add new goal
    if request.method == "POST":
        goals.objects.create(
            user_id=user_record,
            goal_type=request.POST.get("goal_type"),
            goal_description=request.POST.get("goal_description"),
            target_value=Decimal(request.POST.get("target_value")),
            unit=request.POST.get("unit"),
            exercise_id=exercise.objects.get(
                exercise_id=request.POST.get("exercise_id")
            )
            if request.POST.get("exercise_id")
            else None,
            start_date=date.today(),
            target_date=request.POST.get("target_date") or None,
            status="active",
        )
        return redirect("manage_goals")

    all_goals = goals.objects.filter(
        user_id=uid
    ).select_related("exercise_id").order_by("-start_date")

    for g in all_goals:
        if g.exercise_id:
            latest = (
                user_pb.objects.filter(
                    user_id=uid, exercise_id=g.exercise_id, pr_type="max_weight"
                )
                .order_by("-pb_date")
                .first()
            )
            g.current_value = latest.pb_weight if latest else 0
        else:
            g.current_value = 0
        
        g.save(update_fields=["current_value"])

    exercises_list = exercise.objects.all()

    return render(
        request,
        "goals.html",
        {"goals": all_goals, "exercises": exercises_list},
    )


@login_required
def update_goal_status(request, goal_id):
    """
    Update status of a specific goal:
        - completed
        - abandoned

    Returns:
        Redirect to goal page.
    """
    if request.method == "POST":
        g = get_object_or_404(goals, goal_id=goal_id)
        status = request.POST.get("status")

        g.status = status
        if status == "completed":
            g.completion_date = date.today()

        g.save()

    return redirect("manage_goals")


# ------------------------------------------------------------------------------
# BODY STATS
# ------------------------------------------------------------------------------

@login_required
def log_body_stats(request):
    """
    Log user's body measurements:
        - weight
        - neck/waist/hips
        - body fat %

    Renders last 10 logs.

    Returns:
        HttpResponse or redirect to progress page
    """
    user_record = get_or_create_user_record(request.user)

    if request.method == "POST":
        user_stats_log.objects.create(
            user_id=user_record,
            date=request.POST.get("date", date.today()),
            weight=Decimal(request.POST.get("weight")),
            neck=Decimal(request.POST.get("neck"))
            if request.POST.get("neck")
            else None,
            waist=Decimal(request.POST.get("waist"))
            if request.POST.get("waist")
            else None,
            hips=Decimal(request.POST.get("hips"))
            if request.POST.get("hips")
            else None,
            body_fat_percentage=Decimal(request.POST.get("body_fat"))
            if request.POST.get("body_fat")
            else None,
            notes=request.POST.get("notes", ""),
        )
        return redirect("progress")

    recent_logs = user_stats_log.objects.filter(
        user_id=user_record.user_id
    ).order_by("-date")[:10]

    return render(
        request,
        "log_stats.html",
        {"recent_logs": recent_logs, "today": date.today()},
    )


# ------------------------------------------------------------------------------
# SIGNUP
# ------------------------------------------------------------------------------

def signup(request):
    """
    Register a new account using Django's built-in UserCreationForm.

    Returns:
        HttpResponse
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def progress_view(request):
    """
    Legacy minimal progress view (deprecated).
    Only shows AI recommendations — replaced by `view_progress`.

    Returns:
        HttpResponse
    """
    user_record = get_or_create_user_record(request.user)
    recs = get_workout_recommendations(user_record.user_id)

    return render(
        request,
        "workoutware_app/progress.html",
        {
            "weight_increase_recs": recs["weight_increase"],
            "neglected_muscle_group_recs": recs["neglected_muscle_groups"],
        },
    )