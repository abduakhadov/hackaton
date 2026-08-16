from django import forms

from .models import BarberProfile

TAILWIND_INPUT = (
    "w-full px-4 py-3 rounded-lg bg-black/40 border border-yellow-600/40 "
    "text-white placeholder-gray-400 focus:outline-none focus:border-yellow-500 "
    "focus:ring-1 focus:ring-yellow-500 transition"
)


class BarberProfileForm(forms.ModelForm):
    class Meta:
        model = BarberProfile
        fields = ['bio', 'experience_years', 'work_start_time', 'work_end_time', 'services', 'is_available']
        widgets = {
            'bio': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 4}),
            'experience_years': forms.NumberInput(attrs={'class': TAILWIND_INPUT}),
            'work_start_time': forms.TimeInput(attrs={'class': TAILWIND_INPUT, 'type': 'time'}),
            'work_end_time': forms.TimeInput(attrs={'class': TAILWIND_INPUT, 'type': 'time'}),
            'services': forms.SelectMultiple(attrs={'class': TAILWIND_INPUT}),
            'is_available': forms.CheckboxInput(attrs={'class': 'h-5 w-5 accent-yellow-500'}),
        }
