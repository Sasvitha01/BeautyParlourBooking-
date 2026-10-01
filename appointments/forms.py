"""
Forms for the Appointments app.
Handles appointment booking validation and customer data collection.
"""
import re
from datetime import date, timedelta
from django import forms
from django.core.exceptions import ValidationError
from services.models import Service
from .models import Appointment, Customer


class AppointmentBookingForm(forms.Form):
    """Public booking form for customers."""
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your full name',
            'id': 'id_full_name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your.email@example.com',
            'id': 'id_email',
        })
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+91 98765 43210',
            'id': 'id_phone',
        })
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-input',
            'id': 'id_service',
        }),
        empty_label='Select a service...',
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'id': 'id_appointment_date',
        })
    )
    appointment_time = forms.ChoiceField(
        choices=[('', 'Select a time slot...')] + Appointment.TIME_SLOTS,
        widget=forms.Select(attrs={
            'class': 'form-input',
            'id': 'id_appointment_time',
        })
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Any special requests or notes... (optional)',
            'rows': 3,
            'id': 'id_message',
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        if not re.match(r'^\+?\d{10,14}$', cleaned):
            raise ValidationError(
                'Please enter a valid phone number (10-14 digits, optional + prefix).'
            )
        return cleaned

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if len(name) < 2:
            raise ValidationError('Please enter your full name (at least 2 characters).')
        return name

    def clean_appointment_date(self):
        appt_date = self.cleaned_data.get('appointment_date')
        if not appt_date:
            raise ValidationError('Please select a date.')
        today = date.today()
        if appt_date < today:
            raise ValidationError('You cannot book an appointment in the past.')
        if appt_date > today + timedelta(days=90):
            raise ValidationError('You can only book up to 90 days in advance.')
        return appt_date

    def clean(self):
        cleaned_data = super().clean()
        appt_date = cleaned_data.get('appointment_date')
        appt_time = cleaned_data.get('appointment_time')

        if appt_date and appt_time:
            # Check for double booking
            existing = Appointment.objects.filter(
                appointment_date=appt_date,
                appointment_time=appt_time,
                status__in=['pending', 'confirmed'],
            ).exists()
            if existing:
                raise ValidationError(
                    'Sorry, this time slot has just been booked. Please choose another available time.'
                )
        return cleaned_data


class BookingLookupForm(forms.Form):
    """Form for customers to look up their booking status."""
    booking_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g. GNS-2026-A1B2C',
            'id': 'id_booking_id',
        })
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Phone number used during booking',
            'id': 'id_lookup_phone',
        })
    )


class ContactForm(forms.Form):
    """Contact form for visitors."""
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your.email@example.com',
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Subject',
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Your message...',
            'rows': 5,
        })
    )
