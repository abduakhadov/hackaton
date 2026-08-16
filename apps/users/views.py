from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView
from django.shortcuts import redirect, get_object_or_404

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import CustomUser


class RegisterView(CreateView):
    """Ro'yxatdan o'tish sahifasi (mijoz yoki usta sifatida)."""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
        return response


class CustomLoginView(LoginView):
    """Telefon raqami va parol orqali tizimga kirish."""
    template_name = 'users/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Xush kelibsiz!")
        return super().form_valid(form)


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Tizimdan chiqdingiz.")
        return redirect('main:home')

    def post(self, request):
        return self.get(request)


class ProfileView(LoginRequiredMixin, DetailView):
    """Foydalanuvchi profilini ko'rish (o'zining yoki boshqa foydalanuvchi)."""
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(CustomUser, pk=pk)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = context['profile_user']
        if profile_user.is_barber:
            context['barber_profile'] = getattr(profile_user, 'barber_profile', None)
        if profile_user == self.request.user:
            context['appointments'] = profile_user.appointments.all().order_by('-date', '-start_time')[:10] \
                if hasattr(profile_user, 'appointments') else None
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Profilni tahrirlash — faqat o'zining profilini tahrirlay oladi."""
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil yangilandi.")
        return super().form_valid(form)
