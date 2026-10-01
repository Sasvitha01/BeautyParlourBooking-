from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from services.models import ServiceCategory, Service
from appointments.models import Appointment, Customer


class ApiEndpointsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Nail Bar',
            slug='nail-bar',
            icon='💅',
            is_active=True
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Gel Manicure',
            slug='gel-manicure',
            description='Long lasting gel polish manicure.',
            short_description='Gel nails',
            price=999.00,
            duration_minutes=45,
            is_active=True
        )
        self.appt_date = date.today() + timedelta(days=3)

    def test_services_and_categories_api(self):
        svc_res = self.client.get(reverse('api:service_list'))
        self.assertEqual(svc_res.status_code, 200)
        svc_data = svc_res.json().get('results', svc_res.json())
        self.assertTrue(any(s['slug'] == 'gel-manicure' for s in svc_data))

        cat_res = self.client.get(reverse('api:category_list'))
        self.assertEqual(cat_res.status_code, 200)
        cat_data = cat_res.json().get('results', cat_res.json())
        self.assertTrue(any(c['slug'] == 'nail-bar' for c in cat_data))

    def test_available_slots_api(self):
        date_str = self.appt_date.strftime('%Y-%m-%d')
        res = self.client.get(reverse('api:available_slots'), {'date': date_str})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('slots', data)
        self.assertTrue(len(data['slots']) > 0)

    def test_create_appointment_api(self):
        date_str = self.appt_date.strftime('%Y-%m-%d')
        payload = {
            'full_name': 'Divya Sundaram',
            'email': 'divya@example.com',
            'phone': '+919123456780',
            'service_id': self.service.pk,
            'appointment_date': date_str,
            'appointment_time': '14:00',
            'message': 'API booking test'
        }
        res = self.client.post(reverse('api:create_appointment'), payload, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data['booking_id'].startswith('GNS-'))
        self.assertEqual(data['customer_name'], 'Divya Sundaram')

        # Lookup API
        lookup_res = self.client.get(reverse('api:appointment_lookup'), {'booking_id': data['booking_id']})
        self.assertEqual(lookup_res.status_code, 200)
        self.assertEqual(lookup_res.json()['booking_id'], data['booking_id'])
