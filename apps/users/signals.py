from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_barber_profile(sender, instance, created, **kwargs):
    if instance.role == CustomUser.Role.BARBER:
        from apps.barbers.models import BarberProfile
        BarberProfile.objects.get_or_create(user=instance)
