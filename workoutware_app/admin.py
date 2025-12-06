"""
Django Admin Configuration for WorkoutWare
==========================================

This module registers all WorkoutWare database models with Django’s admin panel.
It provides a centralized interface for developers, instructors, and superusers
to inspect, modify, and debug application data.

Only light customization is included, because the admin panel is primarily used
internally rather than as a production-facing tool.

Models registered:
    • exercise
    • target
    • user_info
    • session_exercises
    • sets
    • exercise_target_association
    • progress
    • goals
    • data_validation
    • user_stats_log
    • workout_plan
    • workout_sessions
    • workout_goal_link
    • user_pb
"""

from django.contrib import admin
from .models import (
    exercise,
    target,
    user_info,
    session_exercises,
    sets,
    exercise_target_association,
    progress,
    goals,
    data_validation,
    user_stats_log,
    workout_plan,
    workout_sessions,
    workout_goal_link,
    user_pb
)


# ------------------------------------------------------------------------------
# OPTIONAL ADMIN CUSTOMIZATION CLASSES
# ------------------------------------------------------------------------------

@admin.register(exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """
    Admin view configuration for the Exercise model.

    Displays key identifying fields and allows filtering/searching to make
    exercise management easier for instructors or developers.
    """
    list_display = ("exercise_id", "name", "exercise_type", "equipment", "difficulty")
    search_fields = ("name", "exercise_type", "equipment")
    list_filter = ("exercise_type", "equipment")


@admin.register(user_info)
class UserInfoAdmin(admin.ModelAdmin):
    """
    Admin configuration for user_info model.

    Shows basic identity fields and registration status.
    """
    list_display = ("user_id", "first_name", "last_name", "email", "registered")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("registered",)


@admin.register(workout_sessions)
class WorkoutSessionsAdmin(admin.ModelAdmin):
    """
    Admin configuration for workout_sessions.

    Useful for coordinators to inspect sessions, templates, and completion patterns.
    """
    list_display = ("session_id", "user_id", "session_name", "session_date", "completed", "is_template")
    search_fields = ("session_name",)
    list_filter = ("completed", "is_template", "session_date")


@admin.register(session_exercises)
class SessionExercisesAdmin(admin.ModelAdmin):
    """
    Admin configuration for session_exercises, which represent exercises inside a workout session.
    """
    list_display = ("session_exercise_id", "session_id", "exercise_id", "exercise_order")
    list_filter = ("session_id", "exercise_id")


@admin.register(sets)
class SetsAdmin(admin.ModelAdmin):
    """
    Admin configuration for logged sets.
    """
    list_display = ("set_id", "session_exercise_id", "set_number", "weight", "reps", "rpe", "completion_time")
    list_filter = ("session_exercise_id",)


@admin.register(progress)
class ProgressAdmin(admin.ModelAdmin):
    """
    Admin configuration for progress metrics (daily/weekly).
    """
    list_display = ("progress_id", "user_id", "exercise_id", "period_type", "max_weight", "total_volume", "date")
    list_filter = ("period_type", "exercise_id")


@admin.register(goals)
class GoalsAdmin(admin.ModelAdmin):
    """
    Admin configuration for user fitness goals.
    """
    list_display = ("goal_id", "user_id", "goal_type", "target_value", "unit", "status", "start_date", "target_date")
    list_filter = ("status", "start_date")


@admin.register(data_validation)
class DataValidationAdmin(admin.ModelAdmin):
    """
    Admin configuration for weight validation and anomaly flags.
    Useful for debugging the smart weight detection system.
    """
    list_display = ("validation_id", "user_id", "exercise_id", "input_weight", "expected_max", "flagged_as", "timestamp")
    list_filter = ("flagged_as", "timestamp")


@admin.register(user_stats_log)
class UserStatsLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for bodyweight and body measurements logs.
    """
    list_display = ("log_id", "user_id", "date", "weight", "body_fat_percentage")
    list_filter = ("date",)


@admin.register(user_pb)
class UserPBAdmin(admin.ModelAdmin):
    """
    Admin configuration for personal records (PRs).
    """
    list_display = ("pr_id", "user_id", "exercise_id", "pb_weight", "pb_reps", "pb_date", "previous_pr")
    list_filter = ("exercise_id", "pb_date")


@admin.register(workout_goal_link)
class WorkoutGoalLinkAdmin(admin.ModelAdmin):
    """
    Admin configuration linking goals to specific workout sessions.
    """
    list_display = ("id", "user_id", "goal_id", "session_id", "created_at")
    list_filter = ("goal_id",)


# Register remaining models with basic admin behavior
admin.site.register(target)
admin.site.register(exercise_target_association)
admin.site.register(workout_plan)

