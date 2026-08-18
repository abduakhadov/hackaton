import os
import sys
from django.apps import AppConfig
from django.conf import settings


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Foydalanuvchilar'

    def ready(self):
        import apps.users.signals  # noqa

        # Local development (runserver) rejimida Telegram botdan xabarlarni
        # avtomatik qabul qilish uchun background polling ni yoqamiz
        if getattr(settings, 'DEBUG', False) and 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') == 'true' or '--noreload' in sys.argv:
                try:
                    from .telegram_utils import start_polling_in_background
                    start_polling_in_background()
                except Exception:
                    pass
