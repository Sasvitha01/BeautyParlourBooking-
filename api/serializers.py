"""
REST API serializers for GlowNest Beauty Studio.
"""
from rest_framework import serializers
from services.models import Service, ServiceCategory
from appointments.models import Appointment, Customer


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active']


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    duration_display = serializers.CharField(read_only=True)
    price_display = serializers.CharField(read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'description', 'short_description', 'price', 'price_display',
            'duration_minutes', 'duration_display', 'is_active', 'is_featured',
        ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'email', 'phone']


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=8, decimal_places=2, read_only=True)
    time_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'booking_id', 'customer_name', 'customer_phone', 'customer_email',
            'service_name', 'service_price', 'appointment_date', 'appointment_time',
            'time_display', 'status', 'status_display', 'message', 'created_at',
        ]


class AppointmentCreateSerializer(serializers.Serializer):
    """Serializer for creating appointments via API."""
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    service_id = serializers.IntegerField()
    appointment_date = serializers.DateField()
    appointment_time = serializers.ChoiceField(choices=Appointment.TIME_SLOTS)
    message = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_service_id(self, value):
        try:
            Service.objects.get(id=value, is_active=True)
        except Service.DoesNotExist:
            raise serializers.ValidationError('Service not found or inactive.')
        return value

    def validate(self, data):
        from django.utils import timezone
        now = timezone.localtime(timezone.now())
        today = now.date()
        current_time_str = now.strftime('%H:%M')

        if data['appointment_date'] < today:
            raise serializers.ValidationError({'appointment_date': 'Cannot book in the past.'})

        if data['appointment_date'] == today and data['appointment_time'] <= current_time_str:
            raise serializers.ValidationError(
                {'appointment_time': 'This time slot has already passed for today.'}
            )

        existing = Appointment.objects.filter(
            appointment_date=data['appointment_date'],
            appointment_time=data['appointment_time'],
            status__in=['pending', 'confirmed'],
        ).exists()
        if existing:
            raise serializers.ValidationError(
                'Sorry, this time slot is no longer available. Please choose another time.'
            )
        return data
