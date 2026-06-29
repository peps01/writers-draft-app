#!/bin/bash
set -e
echo "DATABASE_URL is set: $([ -n \"$DATABASE_URL\" ] && echo YES || echo NO)"
echo "Running migrations..."
python manage.py migrate --noinput 2>&1
echo "Collecting static files..."
python manage.py collectstatic --noinput 2>&1
echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
