from django.contrib import admin

from .models import BarberProfile


@admin.register(BarberProfile)
class BarberProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'rating', 'work_start_time', 'work_end_time', 'is_available')
    filter_horizontal = ('services',)
    search_fields = ('user__full_name',)
