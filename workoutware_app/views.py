"""
Views for the WorkoutWare application.

This module contains helper functions and Django views responsible for:
- User dashboard and admin dashboard display
- Exercise creation, editing, deletion
- Workout session creation, modification, and logging
- PR (personal record) tracking
- Smart weight validation
- Progress visualization
- Goals and body stat management
- Template workout management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.utils import timezone
from django.db import connection
from django.db.models import Sum, Avg, Max, Count, Q
from django.http import JsonResponse
from datetime import datetime, date, timedelta
from decimal import Decimal
from collections import defaultdict
import json

from .models import (
    user_info, exercise, workout_sessions, session_exercises,
    sets, data_validation, progress, user_pb, goals,
    user_stats_log, target, exercise_target_association,
    workout_goal_link
)
from .recommendations import get_workout_recommendations
from .progress_utils import rebuild_progress_for_user


# ----------------------------------------------------------------------------
# Helper: Get or create corresponding user_info record
# ----------------------------------------------------------------------------
def get_or_create_user_record(request_user):
    try:
        return user_info.objects.get(email=request_user.email)
    except user_info.DoesNotExist:
        return user_info.objects.create(
            first_name=request_user.first_name or request_user.username,
            last_name=request_user.last_name or '',
            email=request_user.email,
            password_hash='django_auth',
            registered=True,
            date_registered=date.today()
        )


# ----------------------------------------------------------------------------
# Helper: Workout streak
# ----------------------------------------------------------------------------
def calculate_workout_streak(user_id):
    sessions = workout_sessions.objects.filter(
        user_id=user_id,
        completed=True,
        is_template=False
    ).order_by('-session_date').values_list('session_date', flat=True)

    if not sessions:
        return 0

    sessions_list = list(sessions)
    streak = 1

    for i in range(len(sessions_list) - 1):
        diff = (sessions_list[i] - sessions_list[i + 1]).days
        if diff == 1:
            streak += 1
        else:
            break

    return streak


# ----------------------------------------------------------------------------
# Helper: Suggest exercises not done in 7 days
# ----------------------------------------------------------------------------
def get_exercise_suggestions(user_id):
    recent = session_exercises.objects.filter(
        session_id__user_id=user_id,
        session_id__session_date__gte=date.today() - timedelta(days=7),
        session_id__is_template=False
    ).values_list('exercise_id', flat=True)

    return exercise.objects.exclude(exercise_id__in=recent).order_by('?')[:5]


# ----------------------------------------------------------------------------
# Helper: PR detection
# ----------------------------------------------------------------------------
def check_and_record_pr(user_id, exercise_id, weight, reps, set_obj, session):
    """Check if this is a PR and record it."""
    existing_pr = user_pb.objects.filter(
        user_id=user_id,
        exercise_id=exercise_id,
        pr_type='max_weight'
    ).first()

    if existing_pr:
        if weight > existing_pr.pb_weight:
            user_pb.objects.create(
                user_id=user_info.objects.get(user_id=user_id),
                exercise_id=exercise.objects.get(exercise_id=exercise_id),
                session=session,
                pr_type='max_weight',
                pb_weight=weight,
                pb_reps=reps,
                pb_date=date.today(),
                previous_pr=existing_pr.pb_weight,
                notes=f"Set ID: {set_obj.set_id}"
            )
            return True, existing_pr.pb_weight
    else:
        user_pb.objects.create(
            user_id=user_info.objects.get(user_id=user_id),
            exercise_id=exercise.objects.get(exercise_id=exercise_id),
            session=session,
            pr_type='max_weight',
            pb_weight=weight,
            pb_reps=reps,
            pb_date=date.today(),
            notes=f"Set ID: {set_obj.set_id}"
        )
        return True, None

    return False, None


# ----------------------------------------------------------------------------
# Helper: Weight validation
# ----------------------------------------------------------------------------
def validate_weight_input(user_id, exercise_id, input_weight):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MAX(s.weight), AVG(s.weight)
            FROM sets s
            JOIN session_exercises se ON s.session_exercise_id = se.session_exercise_id
            JOIN workout_sessions ws ON se.session_id = ws.session_id
            WHERE ws.user_id = %s
              AND se.exercise_id = %s
              AND s.weight IS NOT NULL
              AND ws.is_template = 0
        """, [user_id, exercise_id])

        result = cursor.fetchone()

        if result[0] is None:
            return {
                "flag": "first_time",
                "message": "🌟 First time logging this exercise!",
                "expected_max": None,
            }

        max_w = Decimal(str(result[0]))
        avg_w = Decimal(str(result[1]))

        if input_weight > max_w * Decimal("1.15"):
            return {
                "flag": "outlier",
                "message": f"⚠️ {input_weight}lbs is unusually high (prev max {max_w}).",
                "expected_max": max_w,
            }
        elif input_weight > max_w:
            return {
                "flag": "new_pr",
                "message": f"🎉 NEW PR! {input_weight}lbs beats your previous {max_w}lbs!",
                "expected_max": max_w,
            }
        elif input_weight < avg_w * Decimal("0.7"):
            return {
                "flag": "suspicious_low",
                "message": f"⚠️ {input_weight}lbs is low (avg {avg_w}).",
                "expected_max": max_w,
            }

        return {"flag": "normal", "message": "✓ Looks good!", "expected_max": max_w}


# ----------------------------------------------------------------------------
# HOME / DASHBOARD
# ----------------------------------------------------------------------------
@login_required
def home(request):
    if request.user.is_superuser:
        # ------------------ ADMIN DASHBOARD ------------------
        total_users = user_info.objects.count()
        total_exercises = exercise.objects.count()
        total_workouts = workout_sessions.objects.filter(
            completed=True, is_template=False
        ).count()

        # Active today
        active_today = workout_sessions.objects.filter(
            session_date=date.today(),
            completed=True,
            is_template=False
        ).values_list("user_id", flat=True)
        active_today = len(set(active_today))

        recent_users = user_info.objects.order_by("-date_registered")[:6]

        popular_exercises = exercise.objects.annotate(
            usage_count=Count("session_exercises",
                              filter=Q(session_exercises__session_id__is_template=False))
        ).order_by("-usage_count")[:5]

        return render(request, "admin_dashboard.html", {
            "total_users": total_users,
            "total_exercises": total_exercises,
            "total_workouts": total_workouts,
            "active_today": active_today,
            "recent_users": recent_users,
            "popular_exercises": popular_exercises,
        })

    # ------------------ USER DASHBOARD ------------------
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id

    streak_days = calculate_workout_streak(user_id)

    # Recent PRs
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.name, pb.pb_weight, pb.pb_date, pb.previous_pr
            FROM user_pb pb
            JOIN exercise e ON pb.exercise_id = e.exercise_id
            WHERE pb.user_id = %s
              AND pb.pr_id IN (
                SELECT MAX(pr_id)
                FROM user_pb
                WHERE user_id = %s
                GROUP BY exercise_id
              )
            ORDER BY pb.pb_date DESC LIMIT 5
        """, [user_id, user_id])

        rows = cursor.fetchall()

    recent_prs = [{
        "exercise_name": r[0],
        "pb_weight": r[1],
        "pb_date": r[2],
        "previous_pr": r[3],
        "improvement": (r[1] - r[3]) if r[3] else 0,
    } for r in rows]

    # Goals (with linked workout count)
    active_goals = goals.objects.filter(user_id=user_id, status="active")

    linked_counts = workout_goal_link.objects.filter(
        user_id=user_record,
        session__completed=True,
        session__is_template=False
    ).values("goal_id").annotate(num_sessions=Count("session_id"))

    counts_by_goal = {x["goal_id"]: x["num_sessions"] for x in linked_counts}

    for g in active_goals:
        if g.exercise_id:
            latest_pr = user_pb.objects.filter(
                user_id=user_id,
                exercise_id=g.exercise_id,
                pr_type="max_weight"
            ).order_by("-pb_date").first()
            g.current_value = latest_pr.pb_weight if latest_pr else 0
        else:
            g.current_value = counts_by_goal.get(g.goal_id, 0)

    # Weekly workouts
    week_start = date.today() - timedelta(days=date.today().weekday())
    workouts_this_week = workout_sessions.objects.filter(
        user_id=user_id,
        session_date__gte=week_start,
        completed=True,
        is_template=False
    ).count()

    total_workouts = workout_sessions.objects.filter(
        user_id=user_id, completed=True, is_template=False
    ).count()

    return render(request, "user_dashboard.html", {
        "streak_days": streak_days,
        "recent_prs": recent_prs,
        "active_goals": active_goals,
        "workouts_this_week": workouts_this_week,
        "total_workouts": total_workouts,
    })


# ----------------------------------------------------------------------------
# ADD EXERCISE (GLOBAL)
# ----------------------------------------------------------------------------
@login_required
def add_exercise(request):
    if request.method == "POST":
        ex = exercise(
            name=request.POST.get("exercise_name"),
            exercise_type=request.POST.get("exercise_type"),
            subtype=request.POST.get("exercise_subtype"),
            equipment=request.POST.get("exercise_equipment"),
            difficulty=request.POST.get("exercise_difficulty"),
            description=request.POST.get("exercise_description"),
            demo_link=request.POST.get("exercise_demo"),
            image=request.FILES.get("exercise_image"),
        )
        ex.save()

        messages.success(request, "Exercise added successfully!")
        return redirect("add_exercise")

    return render(request, "add_exercise_form.html")


# ----------------------------------------------------------------------------
# EDIT / DELETE EXERCISE
# ----------------------------------------------------------------------------
@login_required
def edit_exercise(request, exercise_id):
    if not request.user.is_superuser:
        return redirect("/")

    ex = get_object_or_404(exercise, exercise_id=exercise_id)

    ex.name = request.POST.get("exercise_name")
    ex.exercise_type = request.POST.get("exercise_type")
    ex.subtype = request.POST.get("exercise_subtype")
    ex.equipment = request.POST.get("exercise_equipment")
    ex.difficulty = request.POST.get("exercise_difficulty")
    ex.description = request.POST.get("exercise_description")
    ex.demo_link = request.POST.get("exercise_demo")
    ex.save()

    return redirect("/")


@login_required
def delete_exercise(request, exercise_id):
    if not request.user.is_superuser:
        return redirect("/")

    ex = get_object_or_404(exercise, exercise_id=exercise_id)
    ex.delete()
    return redirect("/")


# ----------------------------------------------------------------------------
# LOG WORKOUT
# ----------------------------------------------------------------------------
@login_required
def log_workout(request):
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id

    exercises_list = exercise.objects.all()

    recent_sessions = workout_sessions.objects.filter(
        user_id=user_id,
        completed=False,
        is_template=False
    ).order_by("-session_date", "-session_id")[:5]

    templates = workout_sessions.objects.filter(
        user_id=user_id, is_template=True
    ).order_by("-session_id")

    active_goals = goals.objects.filter(user_id=user_id, status="active")

    suggestions = get_exercise_suggestions(user_id)

    return render(request, "log_workout.html", {
        "exercises": exercises_list,
        "recent_sessions": recent_sessions,
        "templates": templates,
        "active_goals": active_goals,
        "suggestions": suggestions,
        "today": date.today(),
    })


# ----------------------------------------------------------------------------
# CREATE WORKOUT SESSION
# ----------------------------------------------------------------------------
@login_required
def create_workout_session(request):
    if request.method == "POST":
        user_record = get_or_create_user_record(request.user)

        selected_goal_id = request.POST.get("goal_id")

        new_session = workout_sessions.objects.create(
            user_id=user_record,
            session_name=request.POST.get("session_name"),
            session_date=request.POST.get("session_date", date.today()),
            start_time=request.POST.get("start_time") or None,
            bodyweight=request.POST.get("bodyweight") or None,
            is_template=False,
            completed=False,
        )

        # Link workout to goal (optional)
        if selected_goal_id:
            try:
                g = goals.objects.get(goal_id=selected_goal_id, user_id=user_record)
                workout_goal_link.objects.create(
                    user_id=user_record, goal=g, session=new_session
                )
            except goals.DoesNotExist:
                pass

        return redirect("add_exercises_to_session", session_id=new_session.session_id)

    return redirect("log_workout")


# ----------------------------------------------------------------------------
# COMPLETE WORKOUT
# ----------------------------------------------------------------------------
@login_required
def complete_workout(request, session_id):
    if request.method == "POST":
        s = get_object_or_404(workout_sessions, session_id=session_id)
        s.completed = True
        s.save()
    return redirect("log_workout")


# ----------------------------------------------------------------------------
# Completed workout pages
# ----------------------------------------------------------------------------
@login_required
def completed_workouts(request):
    user_record = get_or_create_user_record(request.user)

    sessions = workout_sessions.objects.filter(
        user_id=user_record,
        is_template=False,
        completed=True
    ).order_by("-session_date", "-start_time")

    return render(request, "completed_workouts.html", {"sessions": sessions})


@login_required
def completed_workouts_week(request):
    user_record = get_or_create_user_record(request.user)

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())

    sessions = workout_sessions.objects.filter(
        user_id=user_record,
        is_template=False,
        completed=True,
        session_date__gte=week_start,
        session_date__lte=today,
    ).order_by("-session_date")

    return render(request, "completed_workouts_week.html", {"sessions": sessions})


# ----------------------------------------------------------------------------
# USE TEMPLATE
# ----------------------------------------------------------------------------
@login_required
def use_template(request, template_id):
    template = get_object_or_404(workout_sessions, session_id=template_id, is_template=True)
    user_record = get_or_create_user_record(request.user)

    if request.method == "POST":
        name = request.POST.get("session_name", template.session_name.replace(" (Template)", ""))

        new_s = workout_sessions.objects.create(
            user_id=user_record,
            session_name=name,
            session_date=date.today(),
            is_template=False,
        )

        for te in session_exercises.objects.filter(session_id=template):
            session_exercises.objects.create(
                session_id=new_s,
                exercise_id=te.exercise_id,
                exercise_order=te.exercise_order,
                target_sets=te.target_sets,
                target_reps=te.target_reps,
            )

        return redirect("add_exercises_to_session", session_id=new_s.session_id)

    return redirect("log_workout")


# ----------------------------------------------------------------------------
# SAVE AS TEMPLATE
# ----------------------------------------------------------------------------
@login_required
def save_as_template(request, session_id):
    if request.method == "POST":
        session = get_object_or_404(workout_sessions, session_id=session_id)

        template = workout_sessions.objects.create(
            user_id=session.user_id,
            session_name=f"{session.session_name} (Template)",
            session_date=date.today(),
            is_template=True,
        )

        for se in session_exercises.objects.filter(session_id=session):
            session_exercises.objects.create(
                session_id=template,
                exercise_id=se.exercise_id,
                exercise_order=se.exercise_order,
                target_sets=se.target_sets,
                target_reps=se.target_reps,
            )

        return redirect("log_workout")


# ----------------------------------------------------------------------------
# DELETE TEMPLATE / WORKOUT
# ----------------------------------------------------------------------------
@login_required
def delete_template(request, template_id):
    if request.method == "POST":
        get_object_or_404(workout_sessions, session_id=template_id, is_template=True).delete()
    return redirect("log_workout")


@login_required
def delete_workout(request, session_id):
    if request.method == "POST":
        get_object_or_404(workout_sessions, session_id=session_id, is_template=False).delete()
    return redirect("log_workout")


# ----------------------------------------------------------------------------
# RENAME WORKOUT
# ----------------------------------------------------------------------------
@login_required
def rename_workout(request, session_id):
    if request.method == "POST":
        session = get_object_or_404(workout_sessions, session_id=session_id)
        new_name = request.POST.get("session_name", "").strip()

        if new_name:
            session.session_name = new_name
            session.save()
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "Name cannot be empty"})

    return JsonResponse({"success": False, "error": "Invalid request"})


# ----------------------------------------------------------------------------
# ADD EXERCISES TO SESSION
# ----------------------------------------------------------------------------
@login_required
def add_exercises_to_session(request, session_id):
    session = workout_sessions.objects.get(session_id=session_id)
    exercises_list = exercise.objects.all()

    session_ex_set = session_exercises.objects.filter(
        session_id=session_id
    ).select_related("exercise_id").order_by("exercise_order")

    session_data = []
    for se in session_ex_set:
        set_list = sets.objects.filter(session_exercise_id=se.session_exercise_id).order_by("set_number")
        session_data.append({"session_exercise": se, "sets": set_list})

    return render(request, "add_exercises.html", {
        "session": session,
        "exercises": exercises_list,
        "session_data": session_data
    })


# ----------------------------------------------------------------------------
# ADD EXERCISE TO SESSION
# ----------------------------------------------------------------------------
@login_required
def add_exercise_to_session(request, session_id):
    if request.method == "POST":
        exercise_id = request.POST.get("exercise_id")
        target_sets = request.POST.get("target_sets", 3)
        target_reps = request.POST.get("target_reps", 10)

        order = session_exercises.objects.filter(session_id=session_id).count()

        session_exercises.objects.create(
            session_id=workout_sessions.objects.get(session_id=session_id),
            exercise_id=exercise.objects.get(exercise_id=exercise_id),
            exercise_order=order + 1,
            target_sets=target_sets,
            target_reps=target_reps,
        )

    return redirect("add_exercises_to_session", session_id=session_id)


# ----------------------------------------------------------------------------
# LOG SET (PR + VALIDATION)
# ----------------------------------------------------------------------------
@login_required
def log_set(request, session_exercise_id):
    if request.method == "POST":
        weight = Decimal(request.POST.get("weight") or "0")
        reps = int(request.POST.get("reps", 0))
        rpe = int(request.POST.get("rpe", 5))
        set_number = int(request.POST.get("set_number", 1))

        se = session_exercises.objects.get(session_exercise_id=session_exercise_id)
        ex = se.exercise_id
        session = se.session_id
        user_record = session.user_id

        # Validation logic
        validation_result = validate_weight_input(
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

        # PR detection
        is_pr = False
        previous_pr = None
        if weight > 0:
            is_pr, previous_pr = check_and_record_pr(
                user_record.user_id, ex.exercise_id, weight, reps, new_set, session
            )

        # Save validation record
        data_validation.objects.create(
            user_id=user_record,
            set_id=new_set,
            exercise_id=ex,
            input_weight=weight,
            expected_max=validation_result["expected_max"],
            flagged_as=validation_result["flag"],
        )

        return render(request, "set_logged.html", {
            "validation": validation_result,
            "set": new_set,
            "is_pr": is_pr,
            "previous_pr": previous_pr,
            "exercise_name": ex.name,
            "session_exercise_id": session_exercise_id,
            "session_id": session.session_id,
        })

    return redirect("log_workout")


# ----------------------------------------------------------------------------
# PROGRESS DASHBOARD
# ----------------------------------------------------------------------------
@login_required
def view_progress(request):
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id

    rebuild_progress_for_user(user_id)

    progress_data = progress.objects.filter(
        user_id=user_id
    ).select_related("exercise_id").order_by("-date")[:20]

    validations = data_validation.objects.filter(
        user_id=user_id
    ).select_related("exercise_id").order_by("-timestamp")[:10]

    # Top exercises by volume
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.exercise_id, e.name, SUM(s.weight * s.reps) AS vol
            FROM exercise e
            JOIN session_exercises se ON e.exercise_id = se.exercise_id
            JOIN sets s ON se.session_exercise_id = s.session_exercise_id
            JOIN workout_sessions ws ON se.session_id = ws.session_id
            WHERE ws.user_id = %s
              AND ws.is_template = 0
              AND s.weight IS NOT NULL
            GROUP BY e.exercise_id, e.name
            ORDER BY vol DESC
            LIMIT 5
        """, [user_id])

        top_exercises = cursor.fetchall()

    trends = {}
    for ex_id, ex_name, _ in top_exercises:
        weekly = progress.objects.filter(
            user_id=user_id, exercise_id=ex_id, period_type="weekly"
        ).order_by("date")[:8]

        if weekly:
            trends[ex_name] = {
                "dates": [p.date.strftime("%m/%d") for p in weekly],
                "max_weights": [float(p.max_weight or 0) for p in weekly],
                "volumes": [float(p.total_volume or 0) for p in weekly],
            }

    body_logs = user_stats_log.objects.filter(
        user_id=user_id
    ).order_by("date")[:30]

    bodyweight_trend = {
        "dates": [x.date.strftime("%m/%d") for x in body_logs],
        "weights": [float(x.weight) for x in body_logs],
    }

    recommendations = get_workout_recommendations(user_id)

    return render(request, "progress.html", {
        "progress_data": progress_data,
        "validations": validations,
        "exercise_trends": json.dumps(trends),
        "bodyweight_trend": json.dumps(bodyweight_trend),
        "user_exercises": exercise.objects.filter(
            session_exercises__session_id__user_id=user_id,
            session_exercises__session_id__is_template=False
        ).distinct().values_list("exercise_id", "name"),
        "weight_increase_recs": recommendations["weight_increase"],
        "neglected_muscle_group_recs": recommendations["neglected_muscle_groups"],
    })


# ----------------------------------------------------------------------------
# API – Fetch exercise data (charts)
# ----------------------------------------------------------------------------
@login_required
def get_exercise_data(request, exercise_id):
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ws.session_date,
                   MAX(s.weight),
                   AVG(s.reps),
                   SUM(s.weight * s.reps)
            FROM workout_sessions ws
            JOIN session_exercises se ON ws.session_id = se.session_id
            JOIN sets s ON se.session_exercise_id = s.session_exercise_id
            WHERE ws.user_id = %s
              AND se.exercise_id = %s
              AND ws.is_template = 0
            GROUP BY ws.session_date
            ORDER BY ws.session_date
            LIMIT 20
        """, [user_id, exercise_id])

        rows = cursor.fetchall()

    return JsonResponse({
        "dates": [r[0].strftime("%m/%d") for r in rows],
        "max_weights": [float(r[1] or 0) for r in rows],
        "avg_reps": [float(r[2] or 0) for r in rows],
        "total_volume": [float(r[3] or 0) for r in rows],
    })


# ----------------------------------------------------------------------------
# GOALS
# ----------------------------------------------------------------------------
@login_required
def manage_goals(request):
    user_record = get_or_create_user_record(request.user)
    user_id = user_record.user_id

    if request.method == "POST":
        goals.objects.create(
            user_id=user_record,
            goal_type=request.POST.get("goal_type"),
            goal_description=request.POST.get("goal_description"),
            target_value=Decimal(request.POST.get("target_value")),
            unit=request.POST.get("unit"),
            exercise_id=exercise.objects.get(
                exercise_id=request.POST.get("exercise_id")
            ) if request.POST.get("exercise_id") else None,
            start_date=date.today(),
            target_date=request.POST.get("target_date") or None,
            status="active",
        )
        return redirect("manage_goals")

    exercise_list = exercise.objects.all()
    all_goals = goals.objects.filter(user_id=user_id).select_related("exercise_id").order_by("-start_date")

    return render(request, "goals.html", {
        "goals": all_goals,
        "exercises": exercise_list,
    })


@login_required
def update_goal_status(request, goal_id):
    if request.method == "POST":
        goal = get_object_or_404(goals, goal_id=goal_id)
        new_status = request.POST.get("status")
        goal.status = new_status

        if new_status == "completed":
            goal.completion_date = date.today()

        goal.save()

    return redirect("manage_goals")


# ----------------------------------------------------------------------------
# BODY STATS
# ----------------------------------------------------------------------------
@login_required
def log_body_stats(request):
    user_record = get_or_create_user_record(request.user)

    if request.method == "POST":
        user_stats_log.objects.create(
            user_id=user_record,
            date=request.POST.get("date", date.today()),
            weight=Decimal(request.POST.get("weight")),
            neck=Decimal(request.POST.get("neck")) if request.POST.get("neck") else None,
            waist=Decimal(request.POST.get("waist")) if request.POST.get("waist") else None,
            hips=Decimal(request.POST.get("hips")) if request.POST.get("hips") else None,
            body_fat_percentage=Decimal(request.POST.get("body_fat")) if request.POST.get("body_fat") else None,
            notes=request.POST.get("notes", "")
        )
        return redirect("progress")

    logs = user_stats_log.objects.filter(
        user_id=user_record.user_id
    ).order_by("-date")[:10]

    return render(request, "log_stats.html", {
        "recent_logs": logs,
        "today": date.today(),
    })


# ----------------------------------------------------------------------------
# SIGNUP
# ----------------------------------------------------------------------------
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})

