"""
Models for the Appointments app.
Defines Customer and Appointment models for GlowNest Beauty Studio.
"""
import uuid
from django.db import models
from django.utils import timezone
from services.models import Service


class Customer(models.Model):
    """Customer who books an appointment."""
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    @property
    def total_appointments(self):
        return self.appointments.count()


class Appointment(models.Model):
    """Appointment booking record."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    # Available time slots (salon working hours with lunch break)
    TIME_SLOTS = [
        ('09:00', '09:00 AM'),
        ('09:30', '09:30 AM'),
        ('10:00', '10:00 AM'),
        ('10:30', '10:30 AM'),
        ('11:00', '11:00 AM'),
        ('11:30', '11:30 AM'),
        ('12:00', '12:00 PM'),
        ('12:30', '12:30 PM'),
        # Lunch break: 1:00 PM - 2:00 PM
        ('14:00', '02:00 PM'),
        ('14:30', '02:30 PM'),
        ('15:00', '03:00 PM'),
        ('15:30', '03:30 PM'),
        ('16:00', '04:00 PM'),
        ('16:30', '04:30 PM'),
        ('17:00', '05:00 PM'),
        ('17:30', '05:30 PM'),
        ('18:00', '06:00 PM'),
        ('18:30', '06:30 PM'),
        ('19:00', '07:00 PM'),
    ]

    booking_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.CharField(max_length=5, choices=TIME_SLOTS)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    message = models.TextField(blank=True, help_text="Optional message from customer")
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        # Prevent double booking: same date + same time = unique
        constraints = [
            models.UniqueConstraint(
                fields=['appointment_date', 'appointment_time'],
                condition=models.Q(status__in=['pending', 'confirmed']),
                name='unique_active_appointment_slot'
            )
        ]

    def __str__(self):
        return f"{self.booking_id} - {self.customer.full_name} - {self.get_appointment_time_display()}"

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = self._generate_booking_id()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_booking_id():
        """Generate a unique booking reference like GNS-2026-XXXXX."""
        year = timezone.now().year
        # Get count of appointments this year + random suffix for safety
        short_uuid = uuid.uuid4().hex[:5].upper()
        return f"GNS-{year}-{short_uuid}"

    @property
    def is_upcoming(self):
        today = timezone.now().date()
        return self.appointment_date >= today and self.status in ('pending', 'confirmed')

    @property
    def time_display(self):
        return dict(self.TIME_SLOTS).get(self.appointment_time, self.appointment_time)

    @property
    def can_cancel(self):
        return self.status in ('pending', 'confirmed')

    @property
    def can_confirm(self):
        return self.status == 'pending'

    @property
    def can_complete(self):
        return self.status == 'confirmed'
