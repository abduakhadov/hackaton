from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from .forms import BookingForm
from .models import Appointment


class BookingCreateView(LoginRequiredMixin, CreateView):
    """Mijoz yangi bron yaratadi — usta, xizmat, sana va vaqtni tanlaydi."""
    model = Appointment
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('bookings:my_bookings')

    def get_initial(self):
        initial = super().get_initial()
        barber_id = self.request.GET.get('barber')
        service_id = self.request.GET.get('service')
        if barber_id:
            initial['barber'] = barber_id
        if service_id:
            initial['service'] = service_id
        return initial

    def form_valid(self, form):
        form.instance.client = self.request.user
        try:
            self.object = form.save()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        messages.success(self.request, "Bron muvaffaqiyatli yaratildi! Tasdiqlashni kuting.")
        return super(CreateView, self).form_valid(form)


class MyBookingsListView(LoginRequiredMixin, ListView):
    """Mijozning barcha bronlari ro'yxati."""
    model = Appointment
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(
            client=self.request.user
        ).select_related('barber__user', 'service').order_by('-date', '-start_time')


class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Mijoz o'z bronini tahrirlaydi (hali tasdiqlanmagan bo'lsa)."""
    model = Appointment
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('bookings:my_bookings')

    def test_func(self):
        appt = self.get_object()
        return self.request.user == appt.client

    def form_valid(self, form):
        try:
            self.object = form.save()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        messages.success(self.request, "Bron yangilandi.")
        return super(UpdateView, self).form_valid(form)


class BookingCancelView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Mijoz o'z bronini bekor qiladi."""
    model = Appointment
    template_name = 'bookings/booking_confirm_cancel.html'
    success_url = reverse_lazy('bookings:my_bookings')

    def test_func(self):
        appt = self.get_object()
        return self.request.user == appt.client

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.status = Appointment.Status.CANCELLED
        self.object.save()
        messages.info(self.request, "Bron bekor qilindi.")
        return HttpResponseRedirect(self.get_success_url())


class BarberScheduleView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Usta o'ziga tushgan bronlar jadvalini ko'radi."""
    model = Appointment
    template_name = 'bookings/barber_schedule.html'
    context_object_name = 'appointments'

    def test_func(self):
        return hasattr(self.request.user, 'barber_profile')

    def get_queryset(self):
        return Appointment.objects.filter(
            barber=self.request.user.barber_profile
        ).select_related('client', 'service').order_by('-date', '-start_time')
