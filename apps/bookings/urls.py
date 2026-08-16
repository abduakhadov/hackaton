from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('new/', views.BookingCreateView.as_view(), name='booking_create'),
    path('my/', views.MyBookingsListView.as_view(), name='my_bookings'),
    path('<int:pk>/edit/', views.BookingUpdateView.as_view(), name='booking_edit'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('schedule/', views.BarberScheduleView.as_view(), name='barber_schedule'),
]
