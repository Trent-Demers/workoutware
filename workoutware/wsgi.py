"""
WSGI config for the WorkoutWare project.

This module exposes the WSGI callable used by traditional web servers
(Gunicorn, uWSGI, Apache mod_wsgi) to serve the Django application.

It sets up the Django environment and returns the WSGI application
so the project can be deployed in production environments that rely on WSGI.
"""
"""
WSGI config for workoutware project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workoutware.settings')

application = get_wsgi_application()
