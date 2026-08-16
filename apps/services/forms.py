from django import forms

from .models import Service, Category

TAILWIND_INPUT = (
    "w-full px-4 py-3 rounded-lg bg-black/40 border border-yellow-600/40 "
    "text-white placeholder-gray-400 focus:outline-none focus:border-yellow-500 "
    "focus:ring-1 focus:ring-yellow-500 transition"
)


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'name', 'description', 'price', 'duration_minutes', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': TAILWIND_INPUT}),
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Xizmat nomi'}),
            'description': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': TAILWIND_INPUT}),
            'duration_minutes': forms.NumberInput(attrs={'class': TAILWIND_INPUT}),
            'image': forms.ClearableFileInput(
                attrs={'class': 'text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg '
                                'file:border-0 file:bg-yellow-500 file:text-black file:font-semibold'}
            ),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-5 w-5 accent-yellow-500'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'icon': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
        }
