"""
REST API views for GlowNest Beauty Studio.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from services.models import Service, ServiceCategory
from appointments.models import Appointment, Customer
from .serializers import (
    ServiceSerializer, ServiceCategorySerializer,
    AppointmentSerializer, AppointmentCreateSerializer,
)


class ServiceListAPIView(generics.ListAPIView):
    """List all active services."""
    queryset = Service.objects.filter(is_active=True).select_related('category')
    serializer_class = ServiceSerializer


class ServiceDetailAPIView(generics.RetrieveAPIView):
    """Retrieve a single service by slug."""
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    lookup_field = 'slug'


class CategoryListAPIView(generics.ListAPIView):
    """List all active service categories."""
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer


@api_view(['POST'])
def create_appointment(request):
    """Create a new appointment via API."""
    serializer = AppointmentCreateSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        customer, _ = Customer.objects.get_or_create(
            phone=data['phone'],
            defaults={
                'full_name': data['full_name'],
                'email': data['email'],
            }
        )
        service = Service.objects.get(id=data['service_id'])

        try:
            appointment = Appointment.objects.create(
                customer=customer,
                service=service,
                appointment_date=data['appointment_date'],
                appointment_time=data['appointment_time'],
                message=data.get('message', ''),
            )
            return Response(
                AppointmentSerializer(appointment).data,
                status=status.HTTP_201_CREATED,
            )
        except Exception:
            return Response(
                {'error': 'This time slot was just booked. Please choose another.'},
                status=status.HTTP_409_CONFLICT,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def available_slots_api(request):
    """Get available time slots for a given date."""
    date_str = request.query_params.get('date', '')
    if not date_str:
        return Response({'error': 'date parameter is required'}, status=400)

    from django.utils import timezone
    from datetime import datetime
    try:
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format (expected YYYY-MM-DD)'}, status=400)

    now = timezone.localtime(timezone.now())
    today = now.date()
    current_time_str = now.strftime('%H:%M')

    booked = set(Appointment.objects.filter(
        appointment_date=query_date,
        status__in=['pending', 'confirmed'],
    ).values_list('appointment_time', flat=True))

    slots = []
    for slot in Appointment.TIME_SLOTS:
        is_past = (query_date < today) or (query_date == today and slot[0] <= current_time_str)
        slots.append({
            'value': slot[0],
            'label': slot[1],
            'available': (not is_past) and (slot[0] not in booked)
        })

    return Response({'date': date_str, 'slots': slots})


@api_view(['GET'])
def appointment_lookup_api(request):
    """Look up an appointment by booking ID."""
    booking_id = request.query_params.get('booking_id', '').strip().upper()
    if not booking_id:
        return Response({'error': 'booking_id parameter is required'}, status=400)

    try:
        appointment = Appointment.objects.select_related(
            'customer', 'service'
        ).get(booking_id=booking_id)
        return Response(AppointmentSerializer(appointment).data)
    except Appointment.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)
