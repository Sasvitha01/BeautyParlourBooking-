from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from services.models import ServiceCategory, Service
from appointments.models import Appointment, Customer


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='staffadmin',
            email='admin@glownest.com',
            password='testpassword123',
            is_staff=True
        )
        self.category = ServiceCategory.objects.create(
            name='Bridal Studio',
            slug='bridal',
            icon='👰‍♀️',
            is_active=True
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Bridal Glow',
            slug='bridal-glow',
            description='Exclusive bridal treatment.',
            short_description='Bridal package',
            price=8000.00,
            duration_minutes=120,
            is_active=True
        )
        self.customer = Customer.objects.create(
            full_name='Aarthi Krishnan',
            email='aarthi@example.com',
            phone='+919876543210'
        )
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service=self.service,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time='11:00',
            status='pending'
        )

    def test_unauthenticated_redirect(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:login'), response.url)

    def test_admin_login_and_dashboard_index(self):
        login_response = self.client.post(reverse('dashboard:login'), {
            'username': 'staffadmin',
            'password': 'testpassword123'
        }, follow=True)
        self.assertEqual(login_response.status_code, 200)

        index_response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(index_response.status_code, 200)
        self.assertContains(index_response, 'Dashboard Overview')
        self.assertContains(index_response, 'Aarthi Krishnan')
        self.assertContains(index_response, self.appointment.booking_id)

    def test_appointments_list_and_filter(self):
        self.client.login(username='staffadmin', password='testpassword123')
        response = self.client.get(reverse('dashboard:appointments'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.appointment.booking_id)

        # Search filter
        search_res = self.client.get(reverse('dashboard:appointments'), {'search': 'Aarthi'})
        self.assertContains(search_res, self.appointment.booking_id)

    def test_appointment_actions_flow(self):
        self.client.login(username='staffadmin', password='testpassword123')

        # 1. Confirm appointment
        confirm_res = self.client.post(reverse('dashboard:appointment_action', kwargs={
            'booking_id': self.appointment.booking_id,
            'action': 'confirm'
        }), follow=True)
        self.assertEqual(confirm_res.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'confirmed')

        # 2. Complete appointment
        complete_res = self.client.post(reverse('dashboard:appointment_action', kwargs={
            'booking_id': self.appointment.booking_id,
            'action': 'complete'
        }), follow=True)
        self.assertEqual(complete_res.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'completed')

    def test_appointment_cancel_action(self):
        self.client.login(username='staffadmin', password='testpassword123')
        cancel_res = self.client.post(reverse('dashboard:appointment_action', kwargs={
            'booking_id': self.appointment.booking_id,
            'action': 'cancel'
        }), follow=True)
        self.assertEqual(cancel_res.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'cancelled')

    def test_appointment_delete_action(self):
        self.client.login(username='staffadmin', password='testpassword123')
        delete_res = self.client.post(reverse('dashboard:appointment_action', kwargs={
            'booking_id': self.appointment.booking_id,
            'action': 'delete'
        }), follow=True)
        self.assertEqual(delete_res.status_code, 200)
        self.assertFalse(Appointment.objects.filter(booking_id=self.appointment.booking_id).exists())

    def test_service_add_and_edit(self):
        self.client.login(username='staffadmin', password='testpassword123')

        # Add service
        add_res = self.client.post(reverse('dashboard:service_add'), {
            'category': self.category.pk,
            'name': 'New Facial Therapy',
            'slug': 'new-facial-therapy',
            'short_description': 'New revitalizing facial',
            'description': 'Full facial relaxation treatment description.',
            'price': '1500.00',
            'duration_minutes': '60',
            'display_order': '5',
            'is_active': True,
        }, follow=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertTrue(Service.objects.filter(slug='new-facial-therapy').exists())

        new_svc = Service.objects.get(slug='new-facial-therapy')

        # Edit service
        edit_res = self.client.post(reverse('dashboard:service_edit', kwargs={'pk': new_svc.pk}), {
            'category': self.category.pk,
            'name': 'Updated Facial Therapy',
            'slug': 'new-facial-therapy',
            'short_description': 'Updated short desc',
            'description': 'Updated long description.',
            'price': '1800.00',
            'duration_minutes': '75',
            'display_order': '5',
            'is_active': True,
        }, follow=True)
        self.assertEqual(edit_res.status_code, 200)
        new_svc.refresh_from_db()
        self.assertEqual(new_svc.name, 'Updated Facial Therapy')
        self.assertEqual(new_svc.price, 1800.00)

    def test_customer_list_view(self):
        self.client.login(username='staffadmin', password='testpassword123')
        res = self.client.get(reverse('dashboard:customers'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Aarthi Krishnan')
        self.assertContains(res, '+919876543210')
