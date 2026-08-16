from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='service_list'),
    path('add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
]
