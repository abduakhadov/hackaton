import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect

from .forms import BookingForm
from .models import Appointment
from apps.barbers.models import BarberProfile


class BookingCreateView(LoginRequiredMixin, CreateView):
    """Mijoz yangi bron yaratadi — usta, xizmat, sana va vaqtni tanlaydi."""
    model = Appointment
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('bookings:my_bookings')

    def dispatch(self, request, *args, **kwargs):
        # Usta bron qila olmaydi
        if request.user.is_authenticated and request.user.is_barber:
            messages.error(request, "Ustalar bron qila olmaydi. Siz o'z jadvalingizni 'Ish jadvalim' bo'limida ko'rishingiz mumkin.")
            return HttpResponseRedirect(reverse_lazy('bookings:my_bookings'))
        return super().dispatch(request, *args, **kwargs)

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
    """
    Mijoz uchun: o'z bronlari ro'yxati.
    Usta uchun: o'ziga tushgan bronlar jadvali.
    """
    model = Appointment
    context_object_name = 'appointments'

    def get_template_names(self):
        if self.request.user.is_barber:
            return ['bookings/barber_schedule.html']
        return ['bookings/my_bookings.html']

    def get_queryset(self):
        user = self.request.user
        if user.is_barber:
            barber_profile = getattr(user, 'barber_profile', None)
            if barber_profile:
                return Appointment.objects.filter(
                    barber=barber_profile
                ).select_related('client', 'service').order_by('-date', '-start_time')
            return Appointment.objects.none()
        # Mijoz uchun
        return Appointment.objects.filter(
            client=user
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
        return hasattr(self.request.user, 'barber_profile') or self.request.user.is_staff or self.request.user.role == 'admin'

    def get_queryset(self):
        if hasattr(self.request.user, 'barber_profile'):
            return Appointment.objects.filter(
                barber=self.request.user.barber_profile
            ).select_related('client', 'service').order_by('-date', '-start_time')
        return Appointment.objects.all().select_related('barber__user', 'client', 'service').order_by('-date', '-start_time')



class UpdateBookingStatusView(LoginRequiredMixin, View):
    """Usta o'ziga tushgan bron holatini o'zgartiradi (kutilmoqda -> tasdiqlandi, bajarildi, bekor qilindi)."""

    def post(self, request, pk):
        if not (request.user.is_barber or request.user.is_staff or request.user.role == 'admin'):
            messages.error(request, "Faqat usta yoki admin bron holatini o'zgartira oladi.")
            return redirect('bookings:my_bookings')

        barber_profile = getattr(request.user, 'barber_profile', None)
        if request.user.is_staff or request.user.role == 'admin':
            appt = get_object_or_404(Appointment, pk=pk)
        else:
            if not barber_profile:
                messages.error(request, "Usta profili topilmadi.")
                return redirect('bookings:my_bookings')
            appt = get_object_or_404(Appointment, pk=pk, barber=barber_profile)

        new_status = request.POST.get('status')
        if new_status in Appointment.Status.values:
            appt.status = new_status
            appt.save()
            messages.success(request, f"Bron holati '{appt.get_status_display()}' ga o'zgartirildi!")
        else:
            messages.error(request, "Noto'g'ri holat tanlandi.")

        return redirect('bookings:my_bookings')


class BarberSlotsApiView(LoginRequiredMixin, View):
    """
    Usta va sana tanlanganda ustaning ish vaqti, band va bo'sh vaqt oralig'ini JSON qaytaradi.
    GET /bookings/api/barber-slots/?barber=1&date=2026-08-18&duration=30
    """

    def get(self, request):
        barber_id = request.GET.get('barber')
        date_str = request.GET.get('date')
        duration_str = request.GET.get('duration', '30')

        if not barber_id or not date_str:
            return JsonResponse({'error': 'Barber and date are required'}, status=400)

        try:
            barber = BarberProfile.objects.get(pk=barber_id)
            appt_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            duration = int(duration_str) if duration_str.isdigit() else 30
        except (BarberProfile.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Invalid barber or date format'}, status=400)

        # Ustaning shu kundagi band bo'lgan bronlari
        booked_appts = Appointment.objects.filter(
            barber=barber,
            date=appt_date,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).order_by('start_time')

        booked_slots = [
            {'start': a.start_time.strftime('%H:%M'), 'end': a.end_time.strftime('%H:%M')}
            for a in booked_appts
        ]

        # Bo'sh vaqt oraliqlarini hisoblash
        free_slots = []
        curr_time = datetime.datetime.combine(appt_date, barber.work_start_time)
        end_work = datetime.datetime.combine(appt_date, barber.work_end_time)

        while curr_time + datetime.timedelta(minutes=duration) <= end_work:
            slot_start = curr_time.time()
            slot_end = (curr_time + datetime.timedelta(minutes=duration)).time()

            is_busy = False
            for a in booked_appts:
                if slot_start < a.end_time and a.start_time < slot_end:
                    is_busy = True
                    break

            if not is_busy:
                free_slots.append(slot_start.strftime('%H:%M'))

            curr_time += datetime.timedelta(minutes=30)

        return JsonResponse({
            'barber_name': barber.user.full_name,
            'work_start': barber.work_start_time.strftime('%H:%M'),
            'work_end': barber.work_end_time.strftime('%H:%M'),
            'booked_slots': booked_slots,
            'free_slots': free_slots,
        })


class RateAppointmentView(LoginRequiredMixin, View):
    """Mijoz bajarilgan bron uchun baho (1-5 yulduz) va fikr qoldiradi."""

    def post(self, request, pk):
        appt = get_object_or_404(Appointment, pk=pk, client=request.user)
        if appt.status != Appointment.Status.COMPLETED:
            messages.error(request, "Faqat bajarilgan xizmatlar uchun baho berish mumkin.")
            return redirect('bookings:my_bookings')

        rating_val = request.POST.get('rating')
        review_text = request.POST.get('review', '').strip()

        try:
            rating_int = int(rating_val)
            if 1 <= rating_int <= 5:
                appt.rating = rating_int
                appt.review = review_text
                appt.save()
                messages.success(request, f"Rahmat! Ustaga {rating_int} ★ baho berildi.")
            else:
                messages.error(request, "Baho 1 dan 5 gacha bo'lishi kerak.")
        except (TypeError, ValueError):
            messages.error(request, "Noto'g'ri baho qiymati.")

        return redirect('bookings:my_bookings')


