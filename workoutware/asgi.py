"""
ASGI config for the WorkoutWare project.

This module exposes the ASGI callable used for asynchronous server interfaces,
enabling support for async features such as WebSockets or long-lived connections.

It configures the Django environment and returns the ASGI application object
that servers like Daphne or Uvicorn use to run the project.

Referenced by: asgi.py is used in production deployments where ASGI is supported.
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
