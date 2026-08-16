from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView

from .models import BarberProfile


class BarberListView(ListView):
    """Barcha ustalar ro'yxati — reyting bo'yicha tartiblangan."""
    model = BarberProfile
    template_name = 'barbers/barber_list.html'
    context_object_name = 'barbers'

    def get_queryset(self):
        return BarberProfile.objects.select_related('user').prefetch_related('services')


class BarberDetailView(DetailView):
    """Usta profili — ish vaqti va ko'rsatadigan xizmatlari bilan."""
    model = BarberProfile
    template_name = 'barbers/barber_detail.html'
    context_object_name = 'barber'


class BarberProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Usta o'z profilini tahrirlaydi (ish vaqti, xizmatlar, bio)."""
    model = BarberProfile
    fields = ['bio', 'experience_years', 'work_start_time', 'work_end_time', 'services', 'is_available']
    template_name = 'barbers/barber_profile_edit.html'
    success_url = reverse_lazy('barbers:barber_list')

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user

    def form_valid(self, form):
        messages.success(self.request, "Usta profili yangilandi.")
        return super().form_valid(form)
