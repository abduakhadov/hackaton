from django import forms

TAILWIND_INPUT = (
    "w-full px-4 py-3 rounded-lg bg-black/40 border border-yellow-600/40 "
    "text-white placeholder-gray-400 focus:outline-none focus:border-yellow-500 "
    "focus:ring-1 focus:ring-yellow-500 transition"
)


class ContactForm(forms.Form):
    full_name = forms.CharField(
        label="Ismingiz", max_length=150,
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Ismingiz'})
    )
    phone_number = forms.CharField(
        label="Telefon raqami", max_length=20,
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': '+998 90 123 45 67'})
    )
    message = forms.CharField(
        label="Xabar",
        widget=forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 5, 'placeholder': 'Xabaringiz...'})
    )
