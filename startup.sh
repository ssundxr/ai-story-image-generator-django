#!/bin/bash
echo "Starting Django application..."

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate --noinput

# Start Gunicorn server
gunicorn --bind=0.0.0.0 --timeout 600 story_generator.wsgi:application
