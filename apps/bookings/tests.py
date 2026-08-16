import datetime
from django.test import TestCase
from django.urls import reverse

from apps.users.models import CustomUser
from apps.services.models import Category, Service
from apps.barbers.models import BarberProfile
from apps.bookings.models import Appointment


class BarberBookingTests(TestCase):
    def setUp(self):
        self.client_user = CustomUser.objects.create_user(
            phone_number='+998901234567', full_name='Mijoz Test', password='password123', role='client'
        )
        self.barber_user = CustomUser.objects.create_user(
            phone_number='+998907654321', full_name='Usta Test', password='password123', role='barber'
        )
        self.barber_profile = BarberProfile.objects.create(
            user=self.barber_user, work_start_time=datetime.time(9, 0), work_end_time=datetime.time(18, 0)
        )
        self.category = Category.objects.create(name='Test Category')
        self.service = Service.objects.create(
            category=self.category, name='Test Service', price=50000, duration_minutes=30
        )
        self.appointment = Appointment.objects.create(
            client=self.client_user,
            barber=self.barber_profile,
            service=self.service,
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
        )

    def test_profile_view_nonexistent_user(self):
        self.client.login(phone_number='+998901234567', password='password123')
        response = self.client.get(reverse('users:profile_detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)

    def test_booking_cancel_status_update(self):
        self.client.login(phone_number='+998901234567', password='password123')
        response = self.client.post(reverse('bookings:booking_cancel', kwargs={'pk': self.appointment.pk}))
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CANCELLED)

    def test_barber_profile_auto_created(self):
        new_barber = CustomUser.objects.create_user(
            phone_number='+998998887766', full_name='Yangi Usta', password='password123', role=CustomUser.Role.BARBER
        )
        self.assertTrue(hasattr(new_barber, 'barber_profile'))
