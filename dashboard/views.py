"""
Views for the Admin Dashboard app.
Handles authenticated admin pages for managing appointments and services.
"""
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from appointments.models import Appointment, Customer
from services.models import Service, ServiceCategory
from services.forms import ServiceForm, ServiceCategoryForm


def admin_login(request):
    """Admin login page."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')

    return render(request, 'dashboard/login.html', {
        'page_title': 'Admin Login',
    })


def admin_logout(request):
    """Admin logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('appointments:home')


@login_required
def dashboard_index(request):
    """Main dashboard with statistics."""
    today = date.today()
    tomorrow = today + timedelta(days=1)

    stats = {
        'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
        'pending': Appointment.objects.filter(status='pending').count(),
        'confirmed': Appointment.objects.filter(status='confirmed').count(),
        'completed': Appointment.objects.filter(status='completed').count(),
        'cancelled': Appointment.objects.filter(status='cancelled').count(),
        'total_customers': Customer.objects.count(),
        'total_services': Service.objects.filter(is_active=True).count(),
        'total_appointments': Appointment.objects.count(),
    }

    upcoming = Appointment.objects.filter(
        appointment_date__gte=today,
        status__in=['pending', 'confirmed'],
    ).select_related('customer', 'service').order_by('appointment_date', 'appointment_time')[:10]

    today_appointments = Appointment.objects.filter(
        appointment_date=today,
    ).select_related('customer', 'service').order_by('appointment_time')

    return render(request, 'dashboard/index.html', {
        'stats': stats,
        'upcoming': upcoming,
        'today_appointments': today_appointments,
        'page_title': 'Dashboard',
    })


@login_required
def appointment_list(request):
    """List and filter all appointments."""
    appointments = Appointment.objects.select_related('customer', 'service').all()

    # Search
    search = request.GET.get('search', '').strip()
    if search:
        appointments = appointments.filter(
            Q(booking_id__icontains=search) |
            Q(customer__full_name__icontains=search) |
            Q(customer__phone__icontains=search) |
            Q(customer__email__icontains=search)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)

    # Filter by service
    service_filter = request.GET.get('service', '')
    if service_filter:
        appointments = appointments.filter(service__id=service_filter)

    services = Service.objects.filter(is_active=True)

    return render(request, 'dashboard/appointments.html', {
        'appointments': appointments,
        'services': services,
        'search': search,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'service_filter': service_filter,
        'page_title': 'Appointments',
    })


@login_required
def appointment_detail(request, booking_id):
    """View single appointment details."""
    appointment = get_object_or_404(
        Appointment.objects.select_related('customer', 'service', 'service__category'),
        booking_id=booking_id,
    )
    return render(request, 'dashboard/appointment_detail.html', {
        'appointment': appointment,
        'page_title': f'Appointment {booking_id}',
    })


@login_required
def appointment_action(request, booking_id, action):
    """Change appointment status: confirm, cancel, complete, delete."""
    appointment = get_object_or_404(Appointment, booking_id=booking_id)

    if request.method == 'POST':
        if action == 'confirm' and appointment.can_confirm:
            appointment.status = 'confirmed'
            appointment.save()
            messages.success(request, f'Appointment {booking_id} confirmed.')
        elif action == 'cancel' and appointment.can_cancel:
            appointment.status = 'cancelled'
            appointment.save()
            messages.success(request, f'Appointment {booking_id} cancelled.')
        elif action == 'complete' and appointment.can_complete:
            appointment.status = 'completed'
            appointment.save()
            messages.success(request, f'Appointment {booking_id} marked as completed.')
        elif action == 'delete':
            appointment.delete()
            messages.success(request, f'Appointment {booking_id} deleted.')
            return redirect('dashboard:appointments')
        else:
            messages.error(request, 'Invalid action for current appointment status.')

    return redirect('dashboard:appointment_detail', booking_id=booking_id)


@login_required
def service_list_admin(request):
    """Admin view for managing services."""
    services = Service.objects.select_related('category').all()
    categories = ServiceCategory.objects.all()

    return render(request, 'dashboard/services.html', {
        'services': services,
        'categories': categories,
        'page_title': 'Manage Services',
    })


@login_required
def service_add(request):
    """Add a new service."""
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service added successfully.')
            return redirect('dashboard:services')
    else:
        form = ServiceForm()

    return render(request, 'dashboard/service_form.html', {
        'form': form,
        'page_title': 'Add Service',
        'is_edit': False,
    })


@login_required
def service_edit(request, pk):
    """Edit an existing service."""
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully.')
            return redirect('dashboard:services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'dashboard/service_form.html', {
        'form': form,
        'service': service,
        'page_title': f'Edit: {service.name}',
        'is_edit': True,
    })


@login_required
def service_delete(request, pk):
    """Delete/deactivate a service."""
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        # Check if service has appointments — deactivate instead of delete
        if service.appointments.exists():
            service.is_active = False
            service.save()
            messages.success(request, f'"{service.name}" has been deactivated (has existing bookings).')
        else:
            service.delete()
            messages.success(request, f'"{service.name}" has been deleted.')
    return redirect('dashboard:services')


@login_required
def customer_list(request):
    """View all customers."""
    customers = Customer.objects.annotate(
        appt_count=Count('appointments')
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    if search:
        customers = customers.filter(
            Q(full_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )

    return render(request, 'dashboard/customers.html', {
        'customers': customers,
        'search': search,
        'page_title': 'Customers',
    })


@login_required
def category_add(request):
    """Add a new service category."""
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('dashboard:services')
    else:
        form = ServiceCategoryForm()

    return render(request, 'dashboard/category_form.html', {
        'form': form,
        'page_title': 'Add Category',
        'is_edit': False,
    })


@login_required
def category_edit(request, pk):
    """Edit an existing service category."""
    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('dashboard:services')
    else:
        form = ServiceCategoryForm(instance=category)

    return render(request, 'dashboard/category_form.html', {
        'form': form,
        'category': category,
        'page_title': f'Edit: {category.name}',
        'is_edit': True,
    })
