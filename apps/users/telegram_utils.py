"""
Telegram Bot API yordamchi funksiyalari.
OTP kodlarini foydalanuvchilarga yuborish uchun ishlatiladi.
"""
import random
import string
import requests
from django.conf import settings


TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


def _api_url(method: str) -> str:
    return TELEGRAM_API_BASE.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)


def send_message(chat_id, text):
    """
    Berilgan chat_id ga Telegram orqali xabar yuboradi.
    Muvaffaqiyatli bo ssa True, aks holda False qaytaradi.
    """
    try:
        resp = requests.post(
            _api_url("sendMessage"),
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        return resp.status_code == 200 and resp.json().get("ok", False)
    except Exception:
        return False


def generate_otp(length=6):
    """6 raqamli tasodifiy OTP kod yaratadi."""
    return "".join(random.choices(string.digits, k=length))


def send_otp(chat_id, code):
    """
    Foydalanuvchiga OTP kodni Telegram orqali yuboradi.
    """
    text = (
        "🔐 <b>Royal Barber — Tasdiqlash kodi</b>\n\n"
        "Sizning bir martalik kodingiz:\n\n"
        f"<code>{code}</code>\n\n"
        "⏱ Kod 5 daqiqa davomida amal qiladi.\n"
        "Agar siz royxatdan otmagan bolsangiz, ushbu xabarni etiborssiz qoldiring."
    )
    return send_message(chat_id, text)


def set_webhook(webhook_url):
    """Bot webhook URL ni o rnatadi (Render deploy vaqtida chaqiriladi)."""
    try:
        resp = requests.post(
            _api_url("setWebhook"),
            json={"url": webhook_url},
            timeout=10,
        )
        return resp.status_code == 200 and resp.json().get("ok", False)
    except Exception:
        return False
