"""
ASGI config for the WorkoutWare project.

This module exposes the ASGI callable used for asynchronous server interfaces,
enabling support for async features such as WebSockets or long-lived connections.

It configures the Django environment and returns the ASGI application object
that servers like Daphne or Uvicorn use to run the project.

Referenced by: asgi.py is used in production deployments where ASGI is supported.

================================================================================
SETUP INSTRUCTIONS - ASYNC SERVER DEPLOYMENT
================================================================================

DEVELOPMENT:
    For development, use Django's built-in server:
    python manage.py runserver

PRODUCTION DEPLOYMENT (ASGI):
    This file enables async features. To deploy with ASGI server:

    1. Install ASGI server (e.g., Uvicorn or Daphne):
       pip install uvicorn
       # or
       pip install daphne

    2. Run with Uvicorn:
       uvicorn workoutware.asgi:application --host 0.0.0.0 --port 8000

    3. Run with Daphne:
       daphne -b 0.0.0.0 -p 8000 workoutware.asgi:application

WHEN TO USE ASGI:
    - If you need WebSocket support
    - If you need async/await features
    - For modern async Django applications

NOTE:
    Currently, Workoutware uses standard Django views (synchronous).
    ASGI is included for future async feature support.
"""
"""
ASGI config for workoutware project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workoutware.settings')

application = get_asgi_application()
