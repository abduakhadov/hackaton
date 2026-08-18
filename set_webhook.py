"""
Telegram bot webhook ni Render serveriga o'rnatuvchi script.
build.sh va entrypoint.sh tomonidan chaqiriladi.
"""
import os
import requests

token = os.environ.get('TELEGRAM_BOT_TOKEN', '8937609200:AAFBw4nfLHSJetvKyqZSKa6NPoTsh3Iww4k').strip()
render_url = os.environ.get('RENDER_EXTERNAL_URL', '').strip()
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()

if render_url:
    base_url = render_url.rstrip('/')
elif render_host:
    base_url = 'https://' + render_host.rstrip('/')
else:
    base_url = ''

print('[Webhook Setup] Token present:', bool(token))
print('[Webhook Setup] Base URL:', base_url)

if token and base_url:
    webhook_url = f"{base_url}/accounts/tg-webhook/"
    print(f'[Webhook Setup] Setting webhook to: {webhook_url}')
    try:
        resp = requests.post(
            f'https://api.telegram.org/bot{token}/setWebhook',
            json={'url': webhook_url, 'drop_pending_updates': True},
            timeout=15,
        )
        print('[Webhook Setup] Webhook response:', resp.json())
    except Exception as e:
        print('[Webhook Setup] Webhook error:', e)
elif not token:
    print('[Webhook Setup] WARNING: TELEGRAM_BOT_TOKEN is not set!')
else:
    print('[Webhook Setup] NOTE: Base URL not found (local or initial build), skipping webhook setup.')
