"""
Superuser yaratish/yangilash scripti.
entrypoint.sh tomonidan chaqiriladi.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import CustomUser

phone = os.environ.get('DJANGO_SUPERUSER_PHONE', '+998000000000')
name = os.environ.get('DJANGO_SUPERUSER_NAME', 'Admin')
pwd = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'RoyalAdmin2024!')

u, created = CustomUser.objects.get_or_create(phone_number=phone, defaults={'full_name': name})
u.full_name = name
u.role = 'admin'
u.is_staff = True
u.is_superuser = True
u.is_active = True
u.set_password(pwd)
u.save()
print('Superuser verified and updated:', phone, '(created:', created, ')')
