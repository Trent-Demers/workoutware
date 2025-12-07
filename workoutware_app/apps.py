from django.apps import AppConfig
"""
    Django application configuration for the workoutware_app.

    Responsibility:
    - Registers the app with Django under the label 'workoutware_app'.
    - Controls default settings for this app (e.g., the default primary key field type).

    Notes:
    - `default_auto_field` is set to BigAutoField so new models in this app will
      automatically use BigAutoField as their primary key type unless overridden.
    - This class is referenced in INSTALLED_APPS as 'workoutware_app.apps.WorkoutwareAppConfig'.
    """

class WorkoutwareAppConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workoutware_app'
