from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import CustomUser

TAILWIND_INPUT = (
    "w-full px-4 py-3 rounded-lg bg-black/40 border border-yellow-600/40 "
    "text-white placeholder-gray-400 focus:outline-none focus:border-yellow-500 "
    "focus:ring-1 focus:ring-yellow-500 transition"
)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('full_name', 'phone_number', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update(
            {'class': TAILWIND_INPUT, 'placeholder': 'Ism Familiya'}
        )
        self.fields['phone_number'].widget.attrs.update(
            {'class': TAILWIND_INPUT, 'placeholder': '+998 90 123 45 67'}
        )
        self.fields['role'].widget.attrs.update({'class': TAILWIND_INPUT})
        # Faqat mijoz va usta ro'yxatdan o'ta oladi (admin emas)
        self.fields['role'].choices = [
            c for c in CustomUser.Role.choices if c[0] != CustomUser.Role.ADMIN
        ]
        self.fields['password1'].widget.attrs.update(
            {'class': TAILWIND_INPUT, 'placeholder': 'Parol'}
        )
        self.fields['password2'].widget.attrs.update(
            {'class': TAILWIND_INPUT, 'placeholder': 'Parolni tasdiqlang'}
        )


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Telefon raqami",
        widget=forms.TextInput(
            attrs={'class': TAILWIND_INPUT, 'placeholder': '+998 90 123 45 67'}
        ),
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(
            attrs={'class': TAILWIND_INPUT, 'placeholder': 'Parol'}
        ),
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('full_name', 'phone_number', 'email', 'avatar')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'phone_number': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT}),
            'avatar': forms.ClearableFileInput(
                attrs={'class': 'text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg '
                                'file:border-0 file:bg-yellow-500 file:text-black file:font-semibold'}
            ),
        }


class OTPVerifyForm(forms.Form):
    """OTP tasdiqlash formasi."""
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label="Tasdiqlash kodi",
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT + ' text-center text-2xl tracking-widest font-mono',
            'placeholder': '______',
            'maxlength': '6',
            'autofocus': True,
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
        }),
    )
