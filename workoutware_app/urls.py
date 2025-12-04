from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    
    # Admin - Exercise Management
    path('add_exercise/', views.add_exercise, name="add_exercise"),
    path('exercise/<int:exercise_id>/edit/', views.edit_exercise, name="edit_exercise"),
    path('exercise/<int:exercise_id>/delete/', views.delete_exercise, name="delete_exercise"),
    
    # Authentication
    path('signup/', views.signup, name="signup"),
    
    # Workout logging
    path('log_workout/', views.log_workout, name="log_workout"),
    path('create_session/', views.create_workout_session, name="create_session"),
    path('session/<int:session_id>/add_exercises/', views.add_exercises_to_session, name="add_exercises_to_session"),
    path('session/<int:session_id>/add_exercise/', views.add_exercise_to_session, name="add_exercise_to_session"),
    path('log_set/<int:session_exercise_id>/', views.log_set, name="log_set"),
    
    # Templates
    path('session/<int:session_id>/save_template/', views.save_as_template, name="save_as_template"),
    path('template/<int:template_id>/use/', views.use_template, name="use_template"),
    path('template/<int:template_id>/delete/', views.delete_template, name="delete_template"),
    
    # Workout Management
    path('workout/<int:session_id>/delete/', views.delete_workout, name="delete_workout"),
    path('workout/<int:session_id>/rename/', views.rename_workout, name="rename_workout"),  
    path('workout/<int:session_id>/complete/', views.complete_workout, name="complete_workout"),
    path('workouts/completed/', views.completed_workouts, name="completed_workouts"),

    
    # Progress & Analytics
    path('progress/', views.view_progress, name="progress"),
    path('progress/exercise/<int:exercise_id>/', views.get_exercise_data, name="get_exercise_data"),
    
    # Goals
    path('goals/', views.manage_goals, name="manage_goals"),
    path('goals/<int:goal_id>/update/', views.update_goal_status, name="update_goal_status"),
    
    # Body Stats
    path('log_stats/', views.log_body_stats, name="log_body_stats"),
]