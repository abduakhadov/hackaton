import datetime

from django import forms

from .models import Appointment

TAILWIND_INPUT = (
    "w-full px-4 py-3 rounded-lg bg-black/40 border border-yellow-600/40 "
    "text-white placeholder-gray-400 focus:outline-none focus:border-yellow-500 "
    "focus:ring-1 focus:ring-yellow-500 transition"
)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['barber', 'service', 'date', 'start_time', 'notes']
        widgets = {
            'barber': forms.Select(attrs={'class': TAILWIND_INPUT}),
            'service': forms.Select(attrs={'class': TAILWIND_INPUT}),
            'date': forms.DateInput(attrs={'class': TAILWIND_INPUT, 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': TAILWIND_INPUT, 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 3,
                                            'placeholder': "Qo'shimcha izoh (ixtiyoriy)"}),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise forms.ValidationError("O'tmish sanaga bron qilib bo'lmaydi.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        # Model.clean() to'liq ustma-ust tushish tekshiruvini save() vaqtida bajaradi,
        # forma darajasida esa asosiy maydonlar to'ldirilganini tekshiramiz.
        return cleaned_data
