from django.urls import path

from . import views

app_name = 'barbers'

urlpatterns = [
    path('', views.BarberListView.as_view(), name='barber_list'),
    path('<int:pk>/', views.BarberDetailView.as_view(), name='barber_detail'),
    path('<int:pk>/edit/', views.BarberProfileUpdateView.as_view(), name='barber_profile_edit'),
]
