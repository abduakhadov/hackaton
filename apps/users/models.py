from django.contrib.auth.models import AbstractUser
from django.db import models

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
