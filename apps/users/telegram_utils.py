"""
Telegram Bot API yordamchi funksiyalari.
OTP kodlarini foydalanuvchilarga yuborish va Telegram bot yangilanishlarini qayta ishlash uchun ishlatiladi.
"""
import datetime
import logging
import random
import string
import threading
import time
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('django')

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


def _api_url(method: str) -> str:
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '').strip()
    return TELEGRAM_API_BASE.format(token=token, method=method)


def send_message(chat_id, text, reply_markup=None):
    """
    Berilgan chat_id ga Telegram orqali xabar yuboradi.
    Muvaffaqiyatli bo'lsa True, aks holda False qaytaradi.
    """
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup

        resp = requests.post(_api_url("sendMessage"), json=payload, timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            return True
        else:
            logger.warning(f"[Telegram Bot] sendMessage failed: status={resp.status_code}, resp={data}")
            return False
    except Exception as e:
        logger.error(f"[Telegram Bot] sendMessage exception: {e}")
        return False


def send_contact_request(chat_id, text=None):
    """Foydalanuvchiga raqamini yuborish tugmasi bilan xabar yuboradi."""
    if not text:
        text = (
            "👋 <b>Royal Barber</b> tasdiqlash botiga xush kelibsiz!\n\n"
            "Tasdiqlash kodini olish uchun quyidagi tugmani bosib telefon raqamingizni yuboring 👇"
        )
    reply_markup = {
        "keyboard": [
            [{"text": "📱 Telefon raqamni yuborish", "request_contact": True}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }
    return send_message(chat_id, text, reply_markup=reply_markup)


def generate_otp(length=6):
    """6 raqamli tasodifiy OTP kod yaratadi."""
    return "".join(random.choices(string.digits, k=length))


def send_otp(chat_id, code):
    """
    Foydalanuvchiga OTP kodni Telegram orqali chiroyli formatda yuboradi.
    """
    text = (
        "✂️ <b>Royal Barber — Tasdiqlash kodi</b>\n\n"
        "Sizning bir martalik kodingiz:\n\n"
        f"👉 <code>{code}</code> 👈\n\n"
        "⏱ Kod <b>15 daqiqa</b> davomida amal qiladi.\n"
        "Kodni saytdagi maydonga kiriting yoki nusxalang."
    )
    reply_markup = {"remove_keyboard": True}
    return send_message(chat_id, text, reply_markup=reply_markup)


def set_webhook(webhook_url):
    """Bot webhook URL ni o'rnatadi (Render/Production deploy vaqtida chaqiriladi)."""
    try:
        resp = requests.post(
            _api_url("setWebhook"),
            json={"url": webhook_url},
            timeout=10,
        )
        return resp.status_code == 200 and resp.json().get("ok", False)
    except Exception as e:
        logger.error(f"[Telegram Bot] set_webhook error: {e}")
        return False


def delete_webhook():
    """Bot webhook ni o'chiradi (Long polling rejimiga o'tish uchun)."""
    try:
        resp = requests.post(
            _api_url("deleteWebhook"),
            json={"drop_pending_updates": False},
            timeout=10,
        )
        return resp.status_code == 200 and resp.json().get("ok", False)
    except Exception as e:
        logger.error(f"[Telegram Bot] delete_webhook error: {e}")
        return False


def process_telegram_update(data):
    """
    Telegram dan kelgan har qanday update (Webhook yoki Long-polling) ni qayta ishlaydi.
    OTP kodini topib, foydalanuvchiga yuboradi.
    """
    from .models import TelegramOTP

    message = data.get('message') or data.get('edited_message')
    if not message:
        return False

    chat = message.get('chat', {})
    chat_id = chat.get('id')
    if not chat_id:
        return False

    text = (message.get('text') or '').strip()
    contact = message.get('contact')
    logger.info(f"[Telegram Bot] Process update: chat_id={chat_id}, text={repr(text)}, contact={bool(contact)}")

    # Telefon raqamni aniqlash
    phone_target = ''
    if contact and contact.get('phone_number'):
        phone_target = str(contact['phone_number']).strip()
    elif text.startswith('/start'):
        parts = text.split(maxsplit=1)
        if len(parts) > 1 and parts[1].strip():
            phone_target = parts[1].strip()
    elif any(c.isdigit() for c in text):
        phone_target = text

    digits_only = ''.join(c for c in phone_target if c.isdigit())

    otp = None
    # 1. Telefon raqam bo'yicha qidirish (oxirgi 9 ta raqam yoki to'liq)
    if digits_only:
        last9 = digits_only[-9:] if len(digits_only) >= 9 else digits_only
        otp = TelegramOTP.objects.filter(
            phone_number__icontains=last9,
            is_used=False,
        ).order_by('-created_at').first()

    # 2. Agar avval shu chat_id ga yuborilgan OTP mavjud bo'lsa
    if not otp:
        otp = TelegramOTP.objects.filter(
            telegram_chat_id=chat_id,
            is_used=False,
        ).order_by('-created_at').first()

    # 3. Agar foydalanuvchi /start yoki har qanday xabar yuborsa va oxirgi 15 daqiqada kutayotgan OTP bo'lsa
    if not otp:
        fifteen_mins_ago = timezone.now() - datetime.timedelta(minutes=15)
        otp = TelegramOTP.objects.filter(
            is_used=False,
            created_at__gte=fifteen_mins_ago,
        ).order_by('-created_at').first()

    if otp:
        otp.telegram_chat_id = chat_id
        otp.save(update_fields=['telegram_chat_id'])
        logger.info(f"[Telegram Bot] Sending OTP {otp.code} to chat_id {chat_id}")
        return send_otp(chat_id, otp.code)
    else:
        logger.warning(f"[Telegram Bot] No pending OTP found for chat_id={chat_id}")
        send_contact_request(chat_id)
        return False


_polling_thread = None
_stop_polling_event = threading.Event()


def run_polling_loop():
    """Telegram bot long-polling orqali yangilanishlarni qabul qilish sikli."""
    delete_webhook()
    offset = 0
    logger.info("[Telegram Poller] Starting Telegram Bot long-polling loop...")

    while not _stop_polling_event.is_set():
        try:
            token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '').strip()
            if not token:
                time.sleep(5)
                continue

            url = TELEGRAM_API_BASE.format(token=token, method="getUpdates")
            resp = requests.get(url, params={"offset": offset, "timeout": 15}, timeout=20)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("ok"):
                    for update in result.get("result", []):
                        offset = update["update_id"] + 1
                        try:
                            process_telegram_update(update)
                        except Exception as e:
                            logger.error(f"[Telegram Poller] Error in process_telegram_update: {e}")
            elif resp.status_code == 409:
                # Webhook o'rnatilgan bo'lsa, polling to'xtatiladi
                logger.info("[Telegram Poller] Webhook is active (HTTP 409), waiting before retry...")
                time.sleep(10)
            else:
                time.sleep(3)
        except requests.exceptions.RequestException:
            time.sleep(3)
        except Exception as e:
            logger.error(f"[Telegram Poller] Unexpected error: {e}")
            time.sleep(3)


def start_polling_in_background():
    """Background da polling thread ni ishga tushirish (Local development uchun)."""
    global _polling_thread
    if _polling_thread is not None and _polling_thread.is_alive():
        return

    _stop_polling_event.clear()
    _polling_thread = threading.Thread(target=run_polling_loop, daemon=True, name="TelegramBotPollerThread")
    _polling_thread.start()
    logger.info("[Telegram Poller] Background polling thread started.")
