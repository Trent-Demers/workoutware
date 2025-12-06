"""
Django management utility script for the WorkoutWare project.

This script provides command-line support for administrative Django tasks,
including running the development server, applying migrations, creating apps,
and executing custom management commands.

It serves as the entry point for Django's command-line interface by setting the
appropriate settings module and delegating to `django.core.management`.

Typical usage:
    python manage.py runserver
    python manage.py makemigrations
    python manage.py migrate
"""
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workoutware.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
