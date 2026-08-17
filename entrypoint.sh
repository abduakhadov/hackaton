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
import os, requests
token = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()

print(f'Token present: {bool(token)}')
print(f'Render host: {render_host}')

if token and render_host:
    webhook_url = f'https://{render_host}/accounts/tg-webhook/'
    print(f'Setting webhook to: {webhook_url}')
    try:
        resp = requests.post(
            f'https://api.telegram.org/bot{token}/setWebhook',
            json={'url': webhook_url, 'drop_pending_updates': True},
            timeout=15,
        )
        data = resp.json()
        print(f'Webhook result: {data}')
    except Exception as e:
        print(f'Webhook error: {e}')
elif not token:
    print('WARNING: TELEGRAM_BOT_TOKEN is not set!')
elif not render_host:
    print('WARNING: RENDER_EXTERNAL_HOSTNAME is not set!')
"

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
