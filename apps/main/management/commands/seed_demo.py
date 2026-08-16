"""
Demo ma'lumotlarni yaratish uchun boshqaruv buyrug'i.
Ishlatish: python manage.py seed_demo
"""
import datetime

from django.core.management.base import BaseCommand

from apps.users.models import CustomUser
from apps.services.models import Category, Service
from apps.barbers.models import BarberProfile


class Command(BaseCommand):
    help = "Demo uchun kategoriya, xizmat, usta va mijoz ma'lumotlarini yaratadi"

    def handle(self, *args, **options):
        # Superuser
        if not CustomUser.objects.filter(phone_number='+998900000000').exists():
            CustomUser.objects.create_superuser(
                phone_number='+998900000000', full_name='Admin', password='admin12345'
            )
            self.stdout.write(self.style.SUCCESS("Superuser yaratildi: +998900000000 / admin12345"))

        # Categories & Services
        haircut, _ = Category.objects.get_or_create(name='Soch olish')
        beard, _ = Category.objects.get_or_create(name='Soqol')
        combo, _ = Category.objects.get_or_create(name='Kompleks')

        s1, _ = Service.objects.get_or_create(
            category=haircut, name='Klassik soch olish',
            defaults={'price': 50000, 'duration_minutes': 30, 'description': 'An\'anaviy uslubda soch olish'}
        )
        s2, _ = Service.objects.get_or_create(
            category=beard, name='Soqol dizayni',
            defaults={'price': 40000, 'duration_minutes': 25, 'description': 'Soqolni tekislash va dizayn qilish'}
        )
        s3, _ = Service.objects.get_or_create(
            category=combo, name='Soch + Soqol (VIP)',
            defaults={'price': 80000, 'duration_minutes': 60, 'description': 'To\'liq VIP xizmat'}
        )

        # Barber user + profile
        if not CustomUser.objects.filter(phone_number='+998911111111').exists():
            barber_user = CustomUser.objects.create_user(
                phone_number='+998911111111', full_name='Aziz Usta',
                password='barber12345', role=CustomUser.Role.BARBER
            )
            profile, _ = BarberProfile.objects.get_or_create(user=barber_user)
            profile.bio = '10 yillik tajribaga ega usta.'
            profile.experience_years = 10
            profile.rating = 4.9
            profile.work_start_time = datetime.time(9, 0)
            profile.work_end_time = datetime.time(19, 0)
            profile.save()
            profile.services.set([s1, s2, s3])
            self.stdout.write(self.style.SUCCESS("Namunaviy usta yaratildi: +998911111111 / barber12345"))

        # Client user
        if not CustomUser.objects.filter(phone_number='+998922222222').exists():
            CustomUser.objects.create_user(
                phone_number='+998922222222', full_name='Test Mijoz',
                password='client12345', role=CustomUser.Role.CLIENT
            )
            self.stdout.write(self.style.SUCCESS("Namunaviy mijoz yaratildi: +998922222222 / client12345"))

        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar muvaffaqiyatli yaratildi!"))
