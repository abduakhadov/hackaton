import json

from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, UpdateView, DetailView
from django.shortcuts import redirect, render, get_object_or_404

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm, OTPVerifyForm
from .models import CustomUser, TelegramOTP
from .telegram_utils import generate_otp, send_otp


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

            # Session ga saqlash (OTP id)
            request.session['pending_otp_id'] = otp.pk
            request.session['pending_phone'] = phone

            from django.conf import settings
            bot_username = settings.TELEGRAM_BOT_USERNAME
            # Botga deep link (start param sifatida telefon raqamni kodlangan holda yuboramiz)
            import urllib.parse
            start_param = urllib.parse.quote(phone.replace('+', '').replace(' ', ''))
            bot_link = f"https://t.me/{bot_username}?start={start_param}"

            return render(request, 'users/verify_otp.html', {
                'bot_link': bot_link,
                'phone': phone,
                'otp_id': otp.pk,
            })
        return render(request, self.template_name, {'form': form})


class VerifyOTPView(View):
    """OTP kodni tasdiqlash va hisob yaratish."""
    template_name = 'users/verify_otp.html'

    def post(self, request):
        code = request.POST.get('code', '').strip()
        otp_id = request.session.get('pending_otp_id')
        phone = request.session.get('pending_phone')

        if not otp_id or not phone:
            messages.error(request, "Sessiya muddati tugagan. Qaytadan ro'yxatdan o'ting.")
            return redirect('users:register')

        try:
            otp = TelegramOTP.objects.get(pk=otp_id, phone_number=phone)
        except TelegramOTP.DoesNotExist:
            messages.error(request, "OTP topilmadi. Qaytadan urinib ko'ring.")
            return redirect('users:register')

        if not otp.is_valid():
            messages.error(request, "Kod muddati tugagan (5 daqiqa). Qaytadan ro'yxatdan o'ting.")
            TelegramOTP.objects.filter(pk=otp_id).delete()
            return redirect('users:register')

        if otp.code != code:
            messages.error(request, "Noto'g'ri kod. Qayta urinib ko'ring.")
            from django.conf import settings
            bot_username = settings.TELEGRAM_BOT_USERNAME
            import urllib.parse
            start_param = urllib.parse.quote(phone.replace('+', '').replace(' ', ''))
            bot_link = f"https://t.me/{bot_username}?start={start_param}"
            return render(request, self.template_name, {
                'bot_link': bot_link,
                'phone': phone,
                'otp_id': otp_id,
                'error': "Noto'g'ri kod. Qayta urinib ko'ring.",
            })

        # OTP to'g'ri — foydalanuvchi yaratish
        if CustomUser.objects.filter(phone_number=phone).exists():
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
        otp.save()

        # Session tozalash
        del request.session['pending_otp_id']
        del request.session['pending_phone']

        login(request, user)
        messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz! Xush kelibsiz!")
        return redirect('main:home')


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """
    Telegram bot webhook — foydalanuvchi /start yozganda chat_id saqlaydi
    va OTP kodni yuboradi.
    """

    def post(self, request):
        import logging
        logger = logging.getLogger('django')

        try:
            data = json.loads(request.body)
            logger.info(f"[TG Webhook] Received data: {data}")

            message = data.get('message') or data.get('edited_message')
            if not message:
                return JsonResponse({'ok': True})

            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            logger.info(f"[TG Webhook] chat_id={chat_id}, text={repr(text)}")

            if text.startswith('/start'):
                parts = text.split(' ', 1)
                start_param = parts[1].strip() if len(parts) > 1 else ''
                logger.info(f"[TG Webhook] start_param={repr(start_param)}")

                if start_param:
                    import urllib.parse
                    phone_digits = urllib.parse.unquote(start_param)
                    # Telefon raqamni formatlash: '+' qo'shamiz
                    if not phone_digits.startswith('+'):
                        phone_digits = '+' + phone_digits

                    logger.info(f"[TG Webhook] Looking for OTP with phone={phone_digits}")

                    # Eng yangi ishlatilmagan OTP ni topamiz
                    try:
                        otp = TelegramOTP.objects.filter(
                            phone_number=phone_digits,
                            is_used=False,
                            telegram_chat_id__isnull=True,
                        ).latest('created_at')

                        logger.info(f"[TG Webhook] Found OTP id={otp.pk}, code={otp.code}")

                        otp.telegram_chat_id = chat_id
                        otp.save()

                        result = send_otp(chat_id, otp.code)
                        logger.info(f"[TG Webhook] send_otp result={result}")
                    except TelegramOTP.DoesNotExist:
                        logger.warning(f"[TG Webhook] No OTP found for phone={phone_digits}")
                        from .telegram_utils import send_message
                        send_message(
                            chat_id,
                            "❌ Tasdiqlash kodi topilmadi. Iltimos, saytga qaytib qaytadan ro'yxatdan o'ting."
                        )
                else:
                    from .telegram_utils import send_message
                    send_message(
                        chat_id,
                        "👋 Salom! Men <b>Royal Barber</b> tasdiqlash botiman.\n\n"
                        "Ro'yxatdan o'tish uchun saytga o'ting va ko'rsatilgan havolani bosing."
                    )
        except Exception as e:
            import logging
            logging.getLogger('django').error(f"[TG Webhook] Exception: {e}", exc_info=True)

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

