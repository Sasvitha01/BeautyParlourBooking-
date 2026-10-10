"""
Views for the Appointments app.
Handles public booking, confirmation, and booking lookup pages.
Also handles public pages: home, about, contact, privacy, terms.
"""
import re
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from services.models import Service, ServiceCategory
from .models import Appointment, Customer
from .forms import AppointmentBookingForm, BookingLookupForm, ContactForm


def home(request):
    """Homepage with hero, featured services, testimonials."""
    featured_services = Service.objects.filter(
        is_active=True, is_featured=True
    ).select_related('category')[:6]

    # If fewer than 6 featured, fill with active services
    if featured_services.count() < 6:
        featured_services = Service.objects.filter(
            is_active=True
        ).select_related('category')[:6]

    categories = ServiceCategory.objects.filter(is_active=True)[:6]

    testimonials = [
        {
            'name': 'Priya Sharma',
            'service': 'Bridal Makeup',
            'text': 'GlowNest made my wedding day absolutely magical! The bridal makeup was flawless and lasted all day. The team understood exactly what I wanted.',
            'rating': 5,
            'initials': 'PS',
        },
        {
            'name': 'Ananya Reddy',
            'service': 'Hair Spa Treatment',
            'text': 'I\'ve been coming to GlowNest for over a year now. Their hair spa treatments are incredibly relaxing and my hair has never looked healthier.',
            'rating': 5,
            'initials': 'AR',
        },
        {
            'name': 'Meera Patel',
            'service': 'Facial & Cleanup',
            'text': 'The facial treatment here is worth every penny. My skin was glowing for weeks! The staff is professional, warm, and the ambiance is so calming.',
            'rating': 5,
            'initials': 'MP',
        },
        {
            'name': 'Kavitha Nair',
            'service': 'Party Makeup',
            'text': 'Got my party makeup done here for my anniversary and received so many compliments! The attention to detail is remarkable.',
            'rating': 4,
            'initials': 'KN',
        },
    ]

    return render(request, 'public/home.html', {
        'featured_services': featured_services,
        'categories': categories,
        'testimonials': testimonials,
        'page_title': 'Home',
    })


def book_appointment(request):
    """Handle appointment booking form."""
    # Pre-select service if passed via query param
    initial = {}
    service_slug = request.GET.get('service')
    if service_slug:
        try:
            service = Service.objects.get(slug=service_slug, is_active=True)
            initial['service'] = service.pk
        except Service.DoesNotExist:
            pass

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                phone=cd['phone'],
                defaults={
                    'full_name': cd['full_name'],
                    'email': cd['email'],
                }
            )
            if not created:
                customer.full_name = cd['full_name']
                customer.email = cd['email']
                customer.save()

            try:
                appointment = Appointment.objects.create(
                    customer=customer,
                    service=cd['service'],
                    appointment_date=cd['appointment_date'],
                    appointment_time=cd['appointment_time'],
                    message=cd.get('message', ''),
                )
                return redirect('appointments:booking_confirmation', booking_id=appointment.booking_id)
            except Exception:
                messages.error(
                    request,
                    'Sorry, this time slot has just been booked by someone else. Please choose another time.'
                )
    else:
        form = AppointmentBookingForm(initial=initial)

    return render(request, 'public/book_appointment.html', {
        'form': form,
        'page_title': 'Book Appointment',
    })


def booking_confirmation(request, booking_id):
    """Display booking confirmation after successful booking."""
    try:
        appointment = Appointment.objects.select_related(
            'customer', 'service', 'service__category'
        ).get(booking_id=booking_id)
    except Appointment.DoesNotExist:
        messages.error(request, 'Booking not found.')
        return redirect('appointments:home')

    return render(request, 'public/booking_confirmation.html', {
        'appointment': appointment,
        'page_title': 'Booking Confirmed',
    })


def check_booking(request):
    """Allow customers to look up their booking status."""
    appointment = None
    not_found = False

    if request.method == 'POST':
        form = BookingLookupForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            phone_clean = re.sub(r'[\s\-\(\)]', '', cd['phone'])
            clean_digits = re.sub(r'\D', '', cd['phone'])
            phone_filter = Q(customer__phone=phone_clean)
            if clean_digits:
                phone_filter |= Q(customer__phone=clean_digits)
                if len(clean_digits) >= 10:
                    phone_filter |= Q(customer__phone__endswith=clean_digits[-10:])
            try:
                appointment = Appointment.objects.select_related(
                    'customer', 'service', 'service__category'
                ).get(
                    Q(booking_id=cd['booking_id'].strip().upper()) & phone_filter
                )
            except Appointment.DoesNotExist:
                not_found = True
            except Appointment.MultipleObjectsReturned:
                # Defensive: booking_id is unique, but guard against any DB anomaly
                not_found = True
            except Exception:
                # Catch any unexpected DB/query error so the page never shows a 500
                not_found = True
    else:
        form = BookingLookupForm()

    return render(request, 'public/check_booking.html', {
        'form': form,
        'appointment': appointment,
        'not_found': not_found,
        'page_title': 'Check Booking',
    })


def available_slots(request):
    """API-like view to get available time slots for a given date."""
    date_str = request.GET.get('date', '').strip()
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)

    from django.utils import timezone
    from datetime import datetime
    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    now = timezone.localtime(timezone.now())
    today = now.date()

    if query_date < today:
        return JsonResponse({'slots': [], 'booked_count': 0, 'error': 'Past dates cannot be booked.'})

    current_time_str = now.strftime('%H:%M')

    # Get booked slots for that date (only active bookings)
    try:
        booked = set(Appointment.objects.filter(
            appointment_date=query_date,
            status__in=['pending', 'confirmed'],
        ).values_list('appointment_time', flat=True))
    except Exception:
        # Catch unexpected DB/query anomalies to prevent 500 error on production
        booked = set()

    all_slots = Appointment.TIME_SLOTS
    available = []
    for slot in all_slots:
        slot_time = slot[0]
        # Exclude past slots if the requested date is today
        if query_date == today and slot_time <= current_time_str:
            continue
        if slot_time not in booked:
            available.append({'value': slot[0], 'label': slot[1]})

    return JsonResponse({'slots': available, 'booked_count': len(booked)})


def about(request):
    """About page."""
    return render(request, 'public/about.html', {
        'page_title': 'About Us',
    })


def contact(request):
    """Contact page with form."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('appointments:contact')
    else:
        form = ContactForm()

    return render(request, 'public/contact.html', {
        'form': form,
        'page_title': 'Contact Us',
    })


def privacy_policy(request):
    """Privacy policy page."""
    return render(request, 'public/privacy.html', {
        'page_title': 'Privacy Policy',
    })


def terms(request):
    """Terms and booking policy page."""
    return render(request, 'public/terms.html', {
        'page_title': 'Terms & Booking Policy',
    })
