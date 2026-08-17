#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating/Updating superuser..."
python manage.py shell -c "
from apps.users.models import CustomUser
phone = '${DJANGO_SUPERUSER_PHONE:-+998000000000}'
name = '${DJANGO_SUPERUSER_NAME:-Admin}'
pwd = '${DJANGO_SUPERUSER_PASSWORD:-RoyalAdmin2024!}'
u, _ = CustomUser.objects.get_or_create(phone_number=phone, defaults={'full_name': name})
u.full_name = name
u.role = 'admin'
u.is_staff = True
u.is_superuser = True
u.is_active = True
u.set_password(pwd)
u.save()
print(f'Superuser verified and updated: {phone}')
"

echo "Seeding demo data..."
python manage.py seed_demo || echo "Seed skipped (already seeded or error)"

echo "Setting Telegram webhook..."
python manage.py shell -c "
import os
token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
hosts = os.environ.get('ALLOWED_HOSTS', '')
if token and hosts:
    host = [h.strip() for h in hosts.split(',') if h.strip() and h.strip() != '.onrender.com']
    if not host:
        # Use render host
        render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
        if render_host:
            webhook_url = f'https://{render_host}/accounts/tg-webhook/'
            from apps.users.telegram_utils import set_webhook
            result = set_webhook(webhook_url)
            print(f'Webhook set: {webhook_url} -> {result}')
" 2>/dev/null || echo "Webhook setup skipped"

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
