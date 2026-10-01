"""URL configuration for REST API."""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('services/', views.ServiceListAPIView.as_view(), name='service_list'),
    path('services/<slug:slug>/', views.ServiceDetailAPIView.as_view(), name='service_detail'),
    path('categories/', views.CategoryListAPIView.as_view(), name='category_list'),
    path('appointments/', views.create_appointment, name='create_appointment'),
    path('appointments/available-slots/', views.available_slots_api, name='available_slots'),
    path('appointments/lookup/', views.appointment_lookup_api, name='appointment_lookup'),
]
