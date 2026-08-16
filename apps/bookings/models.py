import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from apps.barbers.models import BarberProfile
from apps.services.models import Service


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        CONFIRMED = 'confirmed', 'Tasdiqlangan'
        COMPLETED = 'completed', 'Bajarilgan'
        CANCELLED = 'cancelled', 'Bekor qilingan'

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='appointments', verbose_name="Mijoz"
    )
    barber = models.ForeignKey(
        BarberProfile, on_delete=models.CASCADE,
        related_name='appointments', verbose_name="Usta"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE,
        related_name='appointments', verbose_name="Xizmat"
    )
    date = models.DateField(verbose_name="Sana")
    start_time = models.TimeField(verbose_name="Boshlanish vaqti")
    end_time = models.TimeField(verbose_name="Tugash vaqti", blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, verbose_name="Holati"
    )
    notes = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.client} → {self.barber} ({self.date} {self.start_time})"

    def get_absolute_url(self):
        return reverse('bookings:my_bookings')

    def _calculate_end_time(self):
        start_dt = datetime.datetime.combine(self.date, self.start_time)
        duration = self.service.duration_minutes if getattr(self, 'service_id', None) and self.service else 30
        end_dt = start_dt + datetime.timedelta(minutes=duration)
        return end_dt.time()

    def clean(self):
        """
        Biznes mantiq: bitta usta bir vaqtning o'zida ikkita mijozni
        qabul qila olmaydi — vaqt oralig'i ustma-ust tushmasligini tekshiramiz.
        """
        if not (self.date and self.start_time and self.barber_id and self.service_id):
            return

        if not self.end_time:
            self.end_time = self._calculate_end_time()

        if self.end_time <= self.start_time:
            raise ValidationError("Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak.")

        # Ustaning ish vaqti oralig'ida ekanligini tekshirish
        barber = self.barber
        if self.start_time < barber.work_start_time or self.end_time > barber.work_end_time:
            raise ValidationError(
                f"Usta ish vaqti: {barber.work_start_time.strftime('%H:%M')} - "
                f"{barber.work_end_time.strftime('%H:%M')}. Tanlangan vaqt bu oraliqdan tashqarida."
            )

        overlapping = Appointment.objects.filter(
            barber=self.barber,
            date=self.date,
            status__in=[self.Status.PENDING, self.Status.CONFIRMED],
        ).exclude(pk=self.pk)

        for appt in overlapping:
            if self.start_time < appt.end_time and appt.start_time < self.end_time:
                raise ValidationError(
                    f"Bu usta {appt.start_time.strftime('%H:%M')} - "
                    f"{appt.end_time.strftime('%H:%M')} oralig'ida band. Boshqa vaqt tanlang."
                )

    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = self._calculate_end_time()
        self.full_clean()
        super().save(*args, **kwargs)
