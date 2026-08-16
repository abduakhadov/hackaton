from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.services.models import Service


class BarberProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='barber_profile', verbose_name="Foydalanuvchi"
    )
    bio = models.TextField(blank=True, verbose_name="Bio")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="Tajriba (yil)")
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=5.0, verbose_name="Reyting"
    )
    work_start_time = models.TimeField(default='09:00', verbose_name="Ish boshlanish vaqti")
    work_end_time = models.TimeField(default='18:00', verbose_name="Ish tugash vaqti")
    services = models.ManyToManyField(
        Service, blank=True, related_name='barbers', verbose_name="Ko'rsatadigan xizmatlar"
    )
    is_available = models.BooleanField(default=True, verbose_name="Hozir band emas")

    class Meta:
        verbose_name = "Usta profili"
        verbose_name_plural = "Ustalar profillari"
        ordering = ['-rating']

    def __str__(self):
        return f"Usta: {self.user.full_name}"

    def get_absolute_url(self):
        return reverse('barbers:barber_detail', kwargs={'pk': self.pk})
