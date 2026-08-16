from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Service, Category
from .forms import ServiceForm


class StaffRequiredMixin(UserPassesTestMixin):
    """Faqat admin/xodim xizmatlarni qo'shishi va tahrirlashi mumkin."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_staff or getattr(user, 'role', None) == 'admin')

    def handle_no_permission(self):
        messages.error(self.request, "Bu amal uchun ruxsatingiz yo'q.")
        return super().handle_no_permission()


class ServiceListView(ListView):
    """Barcha faol xizmatlar ro'yxati, kategoriya bo'yicha filtrlash imkoniyati bilan."""
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        qs = Service.objects.filter(is_active=True).select_related('category')
        category_slug = self.request.GET.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'


class ServiceCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('services:service_list')

    def form_valid(self, form):
        messages.success(self.request, "Xizmat muvaffaqiyatli qo'shildi.")
        return super().form_valid(form)


class ServiceUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('services:service_list')

    def form_valid(self, form):
        messages.success(self.request, "Xizmat yangilandi.")
        return super().form_valid(form)


class ServiceDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Service
    template_name = 'services/service_confirm_delete.html'
    success_url = reverse_lazy('services:service_list')
