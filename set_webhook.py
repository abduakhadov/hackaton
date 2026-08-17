"""
Telegram bot webhook ni Render serveriga o'rnatuvchi script.
entrypoint.sh tomonidan chaqiriladi.
"""
import os
import requests

token = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()

print('Token present:', bool(token))
print('Render host:', render_host)

if token and render_host:
    webhook_url = 'https://' + render_host + '/accounts/tg-webhook/'
    print('Setting webhook to:', webhook_url)
    try:
        resp = requests.post(
            'https://api.telegram.org/bot' + token + '/setWebhook',
            json={'url': webhook_url, 'drop_pending_updates': True},
            timeout=15,
        )
        data = resp.json()
        print('Webhook result:', data)
    except Exception as e:
        print('Webhook error:', e)
elif not token:
    print('WARNING: TELEGRAM_BOT_TOKEN is not set!')
elif not render_host:
    print('WARNING: RENDER_EXTERNAL_HOSTNAME is not set!')
