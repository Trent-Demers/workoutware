"""
Django management utility script for the WorkoutWare project.

This script provides command-line support for administrative Django tasks,
including running the development server, applying migrations, creating apps,
and executing custom management commands.

It serves as the entry point for Django's command-line interface by setting the
appropriate settings module and delegating to `django.core.management`.

================================================================================
SETUP INSTRUCTIONS - READ BEFORE RUNNING
================================================================================

PREREQUISITES:
    1. Python 3.10+ installed
    2. pip version 25.2+ installed
    3. MySQL 8.0 installed (or Docker for containerized MySQL)
    4. Git installed

STEP-BY-STEP SETUP:

    1. CLONE THE REPOSITORY:
       git clone https://github.com/Trent-Demers/workoutware
       cd workoutware

    2. SETUP MYSQL DATABASE (using Docker):
       docker pull mysql:8.0
       docker run --name workoutware -e MYSQL_ROOT_PASSWORD=Rutgers123 -p 3306:3306 -d mysql:8.0

    3. SETUP DATABASE SCHEMA:
       - Run SQL scripts from the 'sql' folder using MySQL Workbench, DBeaver, or VSCode
       - Execute: sql/workoutware_db_setup.sql (creates database and tables)
       - Optional: Execute: sql/sample_data.sql (adds sample data)

    4. CREATE PYTHON VIRTUAL ENVIRONMENT:
       python -m venv .venv

    5. ACTIVATE VIRTUAL ENVIRONMENT:
       Windows:
           cd .venv/Scripts
           activate
           cd ../..
       Mac/Linux:
           cd .venv/bin
           source activate
           cd ../..

    6. INSTALL DEPENDENCIES:
       pip install -r requirements.txt

    7. CONFIGURE DATABASE CONNECTION:
       - Edit workoutware/settings.py if needed
       - Default settings:
         * Database: workoutware
         * User: root
         * Password: Rutgers123
         * Host: 127.0.0.1
         * Port: 3306

    8. RUN DJANGO MIGRATIONS:
       python manage.py makemigrations
       python manage.py migrate

    9. CREATE ADMIN USER (OPTIONAL):
       python manage.py createsuperuser
       Follow prompts to create admin account

    10. START DJANGO DEVELOPMENT SERVER:
        python manage.py runserver
        Server will run at http://127.0.0.1:8000/

    11. START STREAMLIT CLIENT (in a separate terminal):
        streamlit run streamlit_client/app.py
        Client will run at http://localhost:8501/

ENVIRONMENT VARIABLES (for Streamlit client):
    DB_HOST=127.0.0.1 (default)
    DB_PORT=3306 (default)
    DB_NAME=workoutware (default)
    DB_USER=root (default)
    DB_PASSWORD=Rutgers123 (default)

TROUBLESHOOTING:
    - If MySQL connection fails, ensure Docker container is running:
      docker ps (should show workoutware container)
    - If port 3306 is in use, change MySQL port in docker run command
    - If Django migrations fail, ensure database schema is created first
    - If Streamlit can't connect, verify database credentials match Django settings

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
