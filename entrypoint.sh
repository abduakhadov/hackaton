#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating/Updating superuser..."
python create_superuser.py

echo "Seeding demo data..."
python manage.py seed_demo || echo "Seed skipped (already seeded or error)"

echo "Setting Telegram webhook..."
python set_webhook.py || echo "Webhook setup skipped"

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
