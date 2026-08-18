#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python create_superuser.py || true

echo "Seeding demo data if empty..."
python manage.py seed_demo || true

echo "Setting Telegram Webhook..."
python set_webhook.py || true

echo "Build completed successfully!"
