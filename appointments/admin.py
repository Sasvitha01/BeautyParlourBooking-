"""Admin configuration for Appointments app."""
from django.contrib import admin
from .models import Customer, Appointment


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'total_appointments', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer', 'service', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date', 'service')
    search_fields = ('booking_id', 'customer__full_name', 'customer__phone', 'customer__email')
    readonly_fields = ('booking_id', 'created_at', 'updated_at')
    date_hierarchy = 'appointment_date'
