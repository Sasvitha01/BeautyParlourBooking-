"""URL configuration for admin dashboard app."""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('', views.dashboard_index, name='index'),
    path('appointments/', views.appointment_list, name='appointments'),
    path('appointments/<str:booking_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<str:booking_id>/<str:action>/', views.appointment_action, name='appointment_action'),
    path('services/', views.service_list_admin, name='services'),
    path('services/add/', views.service_add, name='service_add'),
    path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('customers/', views.customer_list, name='customers'),
]
