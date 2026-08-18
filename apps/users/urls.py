from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/verify/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile_detail'),
    # Telegram bot webhook — bot dan xabarlar keladi
    path('tg-webhook/', views.TelegramWebhookView.as_view(), name='telegram_webhook'),
    path('check-otp-status/', views.check_otp_status, name='check_otp_status'),
]
