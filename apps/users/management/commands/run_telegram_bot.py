import logging
from django.core.management.base import BaseCommand
from apps.users.telegram_utils import run_polling_loop

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = "Telegram bot long-polling orqali yangilanishlarni qabul qiluvchi xizmat"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🤖 Telegram Bot Poller ishga tushirildi..."))
        self.stdout.write(self.style.NOTICE("Foydalanuvchilardan kelgan kod so'rovlari qabul qilinmoqda. To'xtatish uchun Ctrl+C bosing."))
        try:
            run_polling_loop()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n🛑 Telegram Bot Poller to'xtatildi."))
