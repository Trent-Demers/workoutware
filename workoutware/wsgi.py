"""
WSGI config for the WorkoutWare project.

This module exposes the WSGI callable used by traditional web servers
(Gunicorn, uWSGI, Apache mod_wsgi) to serve the Django application.

It sets up the Django environment and returns the WSGI application
so the project can be deployed in production environments that rely on WSGI.

================================================================================
SETUP INSTRUCTIONS - PRODUCTION DEPLOYMENT
================================================================================

DEVELOPMENT:
    For development, use Django's built-in server:
    python manage.py runserver

PRODUCTION DEPLOYMENT:
    This file is used for production deployments. To deploy:

    1. Install production WSGI server (e.g., Gunicorn):
       pip install gunicorn

    2. Run with Gunicorn:
       gunicorn workoutware.wsgi:application --bind 0.0.0.0:8000

    3. Or configure with your web server (Apache/Nginx):
       - Apache: Use mod_wsgi
       - Nginx: Use as reverse proxy to Gunicorn

IMPORTANT:
    - Set DEBUG=False in settings.py for production
    - Configure ALLOWED_HOSTS in settings.py
    - Use environment variables for SECRET_KEY and database credentials
    - Set up proper static file serving
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
