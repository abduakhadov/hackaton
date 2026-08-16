from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('robots.txt', views.RobotsTxtView.as_view(), name='robots_txt'),
    path('sitemap.xml', views.SitemapXmlView.as_view(), name='sitemap_xml'),
    path('google7902dc69f8b402cd.html', views.GoogleVerificationView.as_view(), name='google_verify'),
]
