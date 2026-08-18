import json
import logging
import urllib.parse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, DetailView

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import CustomUser, TelegramOTP
from .telegram_utils import generate_otp, send_otp, process_telegram_update

logger = logging.getLogger('django')


class RegisterView(View):
    """
    Ro'yxatdan o'tish — 2 bosqich:
      1) Ma'lumotlarni to'ldirish va Telegram botga yo'naltirish
      2) OTP kodni kiritib tasdiqlash
    """
    template_name = 'users/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('main:home')
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('main:home')
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            full_name = form.cleaned_data['full_name']
            role = form.cleaned_data['role']
            raw_password = form.cleaned_data['password1']

            # Avvalgi ishlatilmagan OTP larni o'chirish
            TelegramOTP.objects.filter(phone_number=phone, is_used=False).delete()

            # OTP yaratish va saqlash
            code = generate_otp()
            otp = TelegramOTP.objects.create(
                phone_number=phone,
                full_name=full_name,
                role=role,
                password_hash=make_password(raw_password),
                code=code,
            )

            # Session da saqlash
            request.session['pending_otp_id'] = otp.pk
            request.session['pending_phone'] = phone

            # Agar avvalgi chat_id ma'lum bo'lsa, zudlik bilan botdan yuboramiz
            prev_otp = TelegramOTP.objects.filter(phone_number=phone, telegram_chat_id__isnull=False).last()
            if prev_otp and prev_otp.telegram_chat_id:
                otp.telegram_chat_id = prev_otp.telegram_chat_id
                otp.save(update_fields=['telegram_chat_id'])
                send_otp(otp.telegram_chat_id, otp.code)

            bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'royalbarber_bot')
            clean_digits = ''.join(c for c in phone if c.isdigit())
            start_param = clean_digits[-9:] if len(clean_digits) >= 9 else clean_digits
            bot_link = f"https://t.me/{bot_username}?start={start_param}"

            context = {
                'bot_link': bot_link,
                'phone': phone,
                'otp_id': otp.pk,
            }
            return render(request, 'users/verify_otp.html', context)

        return render(request, self.template_name, {'form': form})


class VerifyOTPView(View):
    """OTP kodni tasdiqlash va hisob yaratish."""
    template_name = 'users/verify_otp.html'

    def get(self, request):
        otp_id = request.session.get('pending_otp_id')
        phone = request.session.get('pending_phone')
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'royalbarber_bot')
        clean_digits = ''.join(c for c in (phone or '') if c.isdigit())
        start_param = clean_digits[-9:] if len(clean_digits) >= 9 else clean_digits
        bot_link = f"https://t.me/{bot_username}?start={start_param}"

        otp = None
        if otp_id:
            otp = TelegramOTP.objects.filter(pk=otp_id, is_used=False).first()

        return render(request, self.template_name, {
            'bot_link': bot_link,
            'phone': phone or (otp.phone_number if otp else ''),
            'otp_id': otp_id or (otp.pk if otp else ''),
        })

    def post(self, request):
        code = request.POST.get('code', '').strip()
        otp_id = request.POST.get('otp_id') or request.session.get('pending_otp_id')
        phone = request.POST.get('phone') or request.session.get('pending_phone')

        if not code:
            messages.error(request, "Iltimos, tasdiqlash kodini kiriting.")
            return redirect('users:verify_otp')

        otp = None
        # 1. ID va telefon orqali qidirish
        if otp_id and phone:
            otp = TelegramOTP.objects.filter(pk=otp_id, phone_number=phone, is_used=False).first()

        # 2. Agar topilmasa, ID bo'yicha
        if not otp and otp_id:
            otp = TelegramOTP.objects.filter(pk=otp_id, is_used=False).first()

        # 3. Agar topilmasa, kiritilgan kod bo'yicha qidirish
        if not otp:
            otp = TelegramOTP.objects.filter(code=code, is_used=False).order_by('-created_at').first()

        # 4. Agar topilmasa, telefon bo'yicha oxirgi OTP
        if not otp and phone:
            otp = TelegramOTP.objects.filter(phone_number=phone, is_used=False).order_by('-created_at').first()

        if not otp:
            messages.error(request, "Noto'g'ri yoki eskirgan kod. Qaytadan urinib ko'ring.")
            return redirect('users:register')

        if not otp.is_valid():
            messages.error(request, "Kod muddati tugagan (15 daqiqa). Qaytadan ro'yxatdan o'ting.")
            TelegramOTP.objects.filter(pk=otp.pk).delete()
            return redirect('users:register')

        if otp.code != code:
            messages.error(request, "Noto'g'ri tasdiqlash kodi kiritildi. Qayta urinib ko'ring.")
            bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'royalbarber_bot')
            clean_digits = ''.join(c for c in otp.phone_number if c.isdigit())
            start_param = clean_digits[-9:] if len(clean_digits) >= 9 else clean_digits
            bot_link = f"https://t.me/{bot_username}?start={start_param}"
            return render(request, self.template_name, {
                'bot_link': bot_link,
                'phone': otp.phone_number,
                'otp_id': otp.pk,
                'error': "Noto'g'ri kod. Iltimos, Telegram bot yuborgan kodni to'g'ri kiriting.",
            })

        # OTP to'g'ri — foydalanuvchi yaratish
        if CustomUser.objects.filter(phone_number=otp.phone_number).exists():
            messages.error(request, "Bu telefon raqami allaqachon ro'yxatdan o'tgan.")
            return redirect('users:login')

        user = CustomUser(
            phone_number=otp.phone_number,
            full_name=otp.full_name,
            role=otp.role,
            password=otp.password_hash,
        )
        user.save()

        otp.is_used = True
        otp.save(update_fields=['is_used'])

        # Session tozalash
        request.session.pop('pending_otp_id', None)
        request.session.pop('pending_phone', None)

        login(request, user)
        messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz! Xush kelibsiz!")
        return redirect('main:home')


def check_otp_status(request):
    """AJAX orqali Telegram botdan kod yuborilganligini tekshirish."""
    otp_id = request.GET.get('otp_id') or request.session.get('pending_otp_id')
    phone = request.GET.get('phone') or request.session.get('pending_phone')
    otp = None
    if otp_id:
        otp = TelegramOTP.objects.filter(pk=otp_id, is_used=False).first()
    elif phone:
        otp = TelegramOTP.objects.filter(phone_number=phone, is_used=False).order_by('-created_at').first()

    if otp and otp.telegram_chat_id:
        return JsonResponse({'sent': True, 'chat_id': otp.telegram_chat_id})
    return JsonResponse({'sent': False})


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """
    Telegram bot webhook — Render/Production serverda ishlaydi.
    """
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            process_telegram_update(data)
        except Exception as e:
            logger.error(f"[TG Webhook] Exception: {e}", exc_info=True)
        return JsonResponse({'ok': True})


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
    """Foydalanuvchi profilini ko'rish."""
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
    """Profilni tahrirlash."""
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil yangilandi.")
        return super().form_valid(form)
