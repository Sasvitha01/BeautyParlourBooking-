"""URL configuration for appointments app (public pages)."""
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('booking/<str:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('check-booking/', views.check_booking, name='check_booking'),
    path('available-slots/', views.available_slots, name='available_slots'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('debug-status/', views.debug_status, name='debug_status'),
]
