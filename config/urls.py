from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.main.urls', namespace='main')),
    path('accounts/', include('apps.users.urls', namespace='users')),
    path('services/', include('apps.services.urls', namespace='services')),
    path('barbers/', include('apps.barbers.urls', namespace='barbers')),
    path('bookings/', include('apps.bookings.urls', namespace='bookings')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
