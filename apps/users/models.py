from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Telefon raqami orqali tizimga kiriladigan maxsus foydalanuvchi modeli.
    username maydoni Django Admin bilan moslik uchun saqlab qolinadi,
    lekin login uchun ishlatilmaydi — buning o'rniga phone_number ishlatiladi.
    """

    class Role(models.TextChoices):
        CLIENT = 'client', 'Mijoz'
        BARBER = 'barber', 'Usta'
        ADMIN = 'admin', 'Administrator'

    username = None  # o'chirilgan, o'rniga phone_number ishlatiladi
    phone_number = models.CharField(
        max_length=20, unique=True, verbose_name="Telefon raqami"
    )
    full_name = models.CharField(max_length=150, verbose_name="F.I.Sh")
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.CLIENT, verbose_name="Roli"
    )
    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True, verbose_name="Profil rasmi"
    )
    email = models.EmailField(blank=True, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_barber(self):
        return self.role == self.Role.BARBER


class TelegramOTP(models.Model):
    """
    Ro'yxatdan o'tishda Telegram orqali yuborilgan OTP kodlarini saqlaydi.
    """
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqami")
    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=10, blank=True)
    password_hash = models.CharField(max_length=256, blank=True)
    code = models.CharField(max_length=10, verbose_name="OTP kod")
    telegram_chat_id = models.BigIntegerField(null=True, blank=True, verbose_name="Telegram Chat ID")
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Telegram OTP"
        verbose_name_plural = "Telegram OTP lar"

    def is_valid(self):
        """Kod 5 daqiqa davomida amal qiladi."""
        expiry = self.created_at + datetime.timedelta(minutes=5)
        return not self.is_used and timezone.now() <= expiry

    def __str__(self):
        return f"{self.phone_number} — {self.code}"
