from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from services.models import ServiceCategory, Service
from appointments.models import Appointment, Customer


class AppointmentsCustomerFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Skin Care',
            slug='skin-care',
            icon='🧖‍♀️',
            is_active=True
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Gold Facial',
            slug='gold-facial',
            description='Luxury 24K gold facial.',
            short_description='Gold glow',
            price=2000.00,
            duration_minutes=60,
            is_active=True,
            is_featured=True
        )
        self.booking_date = date.today() + timedelta(days=2)

    def test_home_page(self):
        response = self.client.get(reverse('appointments:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GlowNest')
        self.assertContains(response, 'Gold Facial')

    def test_static_pages(self):
        for route_name in ['about', 'contact', 'privacy', 'terms']:
            response = self.client.get(reverse(f'appointments:{route_name}'))
            self.assertEqual(response.status_code, 200)

    def test_contact_form_submission(self):
        response = self.client.post(reverse('appointments:contact'), {
            'name': 'Pooja Kumar',
            'email': 'pooja@example.com',
            'subject': 'Bridal consultation inquiry',
            'message': 'Hello, I would like to inquire about wedding packages.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thank you for your message")

    def test_booking_appointment_success(self):
        post_data = {
            'full_name': 'Ritu Varma',
            'phone': '+919876543210',
            'email': 'ritu@example.com',
            'service': self.service.pk,
            'appointment_date': self.booking_date.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'message': 'Please use organic products if possible.'
        }
        response = self.client.post(reverse('appointments:book_appointment'), post_data)
        self.assertEqual(response.status_code, 302)

        appointment = Appointment.objects.get(customer__phone='+919876543210')
        self.assertTrue(appointment.booking_id.startswith('GNS-'))
        self.assertEqual(appointment.status, 'pending')
        self.assertEqual(appointment.service, self.service)

        # Check confirmation page
        confirm_url = reverse('appointments:booking_confirmation', kwargs={'booking_id': appointment.booking_id})
        self.assertRedirects(response, confirm_url)

        confirm_response = self.client.get(confirm_url)
        self.assertEqual(confirm_response.status_code, 200)
        self.assertContains(confirm_response, appointment.booking_id)
        self.assertContains(confirm_response, 'Ritu Varma')
        self.assertContains(confirm_response, 'Gold Facial')

    def test_prevent_double_booking(self):
        # Book initial appointment
        customer = Customer.objects.create(
            full_name='First Customer',
            email='first@example.com',
            phone='+919999988888'
        )
        Appointment.objects.create(
            customer=customer,
            service=self.service,
            appointment_date=self.booking_date,
            appointment_time='11:00',
            status='confirmed'
        )

        # Attempt to book the exact same slot on the same date
        post_data = {
            'full_name': 'Second Customer',
            'phone': '+918888877777',
            'email': 'second@example.com',
            'service': self.service.pk,
            'appointment_date': self.booking_date.strftime('%Y-%m-%d'),
            'appointment_time': '11:00',
            'message': ''
        }
        response = self.client.post(reverse('appointments:book_appointment'), post_data)
        # Form should have validation error and re-render without creating
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sorry, this time slot has just been booked')
        self.assertEqual(Appointment.objects.filter(appointment_date=self.booking_date, appointment_time='11:00').count(), 1)

    def test_available_slots_endpoint(self):
        # Book 10:00 slot
        customer = Customer.objects.create(full_name='Slot Tester', email='t@example.com', phone='+919876500000')
        Appointment.objects.create(
            customer=customer,
            service=self.service,
            appointment_date=self.booking_date,
            appointment_time='10:00',
            status='confirmed'
        )

        date_str = self.booking_date.strftime('%Y-%m-%d')
        response = self.client.get(reverse('appointments:available_slots'), {'date': date_str})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        slot_values = [s['value'] for s in data['slots']]
        self.assertNotIn('10:00', slot_values)
        self.assertIn('10:30', slot_values)
        self.assertEqual(data['booked_count'], 1)

    def test_available_slots_missing_date(self):
        response = self.client.get(reverse('appointments:available_slots'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Date is required'})

    def test_available_slots_invalid_format(self):
        for bad_date in ['invalid', '2026-13-45', 'not-a-date']:
            response = self.client.get(reverse('appointments:available_slots'), {'date': bad_date})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {'error': 'Invalid date format'})

    def test_available_slots_past_date(self):
        past_date = (date.today() - timedelta(days=5)).strftime('%Y-%m-%d')
        response = self.client.get(reverse('appointments:available_slots'), {'date': past_date})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['slots'], [])
        self.assertEqual(data['booked_count'], 0)
        self.assertEqual(data['error'], 'Past dates cannot be booked.')

    def test_available_slots_whitespace_handling(self):
        date_str = f"  {self.booking_date.strftime('%Y-%m-%d')}  "
        response = self.client.get(reverse('appointments:available_slots'), {'date': date_str})
        self.assertEqual(response.status_code, 200)
        self.assertIn('slots', response.json())

    def test_available_slots_db_error_resilience(self):
        from unittest.mock import patch
        with patch('appointments.models.Appointment.objects.filter', side_effect=Exception('DB timeout')):
            date_str = self.booking_date.strftime('%Y-%m-%d')
            response = self.client.get(reverse('appointments:available_slots'), {'date': date_str})
            self.assertEqual(response.status_code, 200)
            self.assertIn('slots', response.json())

    def test_check_booking_lookup(self):
        customer = Customer.objects.create(full_name='Maya Sen', email='maya@example.com', phone='+919876543210')
        appointment = Appointment.objects.create(
            customer=customer,
            service=self.service,
            appointment_date=self.booking_date,
            appointment_time='15:00',
            status='confirmed'
        )

        # Lookup with matching phone and ID
        response = self.client.post(reverse('appointments:check_booking'), {
            'booking_id': appointment.booking_id,
            'phone': '9876543210'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, appointment.booking_id)
        self.assertContains(response, 'Maya Sen')
        self.assertContains(response, 'Confirmed')

        # Lookup with incorrect phone
        response_invalid = self.client.post(reverse('appointments:check_booking'), {
            'booking_id': appointment.booking_id,
            'phone': '9000000000'
        })
        self.assertEqual(response_invalid.status_code, 200)
        self.assertContains(response_invalid, 'No Appointment Found')

    def test_past_date_booking_rejected(self):
        past_date = date.today() - timedelta(days=1)
        post_data = {
            'full_name': 'Test Past User',
            'phone': '+919876543210',
            'email': 'past@example.com',
            'service': self.service.pk,
            'appointment_date': past_date.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'message': ''
        }
        response = self.client.post(reverse('appointments:book_appointment'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You cannot book an appointment in the past')

    def test_cancelled_appointment_releases_slot(self):
        customer = Customer.objects.create(full_name='Cancel Tester', email='c@example.com', phone='+919876501234')
        appointment = Appointment.objects.create(
            customer=customer,
            service=self.service,
            appointment_date=self.booking_date,
            appointment_time='12:00',
            status='pending'
        )

        # Cancel the appointment
        appointment.status = 'cancelled'
        appointment.save()

        # Slot should now be available in available_slots
        date_str = self.booking_date.strftime('%Y-%m-%d')
        response = self.client.get(reverse('appointments:available_slots'), {'date': date_str})
        self.assertEqual(response.status_code, 200)
        slots = [s['value'] for s in response.json()['slots']]
        self.assertIn('12:00', slots)

        # Booking the same slot should now succeed
        post_data = {
            'full_name': 'New Booker',
            'phone': '+919876599999',
            'email': 'new@example.com',
            'service': self.service.pk,
            'appointment_date': date_str,
            'appointment_time': '12:00',
            'message': ''
        }
        res = self.client.post(reverse('appointments:book_appointment'), post_data)
        self.assertEqual(res.status_code, 302)


class DjangoAdminAccessTests(TestCase):
    """Tests for Django Admin access control and customer booking visibility."""

    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Nail Art',
            slug='nail-art',
            icon='💅',
            is_active=True
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Gel Manicure',
            slug='gel-manicure',
            description='Long lasting gel polish.',
            short_description='Gel nails',
            price=1200.00,
            duration_minutes=45,
            is_active=True
        )
        self.customer = Customer.objects.create(
            full_name='Priya Sharma',
            email='priya@example.com',
            phone='+919876543210'
        )
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            appointment_date=date.today() + timedelta(days=3),
            appointment_time='14:00',
            status='pending'
        )
        self.staff_user = User.objects.create_superuser(
            username='admin_staff',
            email='admin@test.com',
            password='securepassword123'
        )
        self.non_staff_user = User.objects.create_user(
            username='regular_customer',
            password='customerpass123',
            is_staff=False,
            is_active=True
        )

    def test_anonymous_user_cannot_access_admin_portal(self):
        # /admin/ must redirect unauthenticated visitors to login
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

        # /admin/appointments/appointment/ must also redirect
        detail_response = self.client.get('/admin/appointments/appointment/')
        self.assertEqual(detail_response.status_code, 302)
        self.assertIn('/admin/login/', detail_response.url)

    def test_non_staff_user_cannot_access_admin_portal(self):
        self.client.login(username='regular_customer', password='customerpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

        appts_response = self.client.get('/admin/appointments/appointment/')
        self.assertEqual(appts_response.status_code, 302)

    def test_authenticated_staff_can_access_admin_and_view_booking_details(self):
        self.client.login(username='admin_staff', password='securepassword123')

        # Admin root
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Site administration')
        self.assertContains(response, 'Appointments')

        # Appointment changelist view
        appts_response = self.client.get('/admin/appointments/appointment/')
        self.assertEqual(appts_response.status_code, 200)

        # Verify all required booking fields are visible to admin
        self.assertContains(appts_response, self.appointment.booking_id)
        self.assertContains(appts_response, 'Priya Sharma')      # Customer Name
        self.assertContains(appts_response, '+919876543210')     # Phone Number
        self.assertContains(appts_response, 'Gel Manicure')      # Selected Service
        self.assertContains(appts_response, '02:00 PM')          # Time (display label)
        self.assertContains(appts_response, 'Pending')           # Booking Status

    def test_django_admin_alias_route_works(self):
        self.client.login(username='admin_staff', password='securepassword123')
        response = self.client.get('/django-admin/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Site administration')

