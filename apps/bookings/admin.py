from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'barber', 'service', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'barber')
    search_fields = ('client__full_name', 'barber__user__full_name')
    date_hierarchy = 'date'
