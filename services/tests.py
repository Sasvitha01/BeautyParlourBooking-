from django.test import TestCase, Client
from django.urls import reverse
from services.models import ServiceCategory, Service


class ServicesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Hair Care',
            slug='hair-care',
            icon='✂️',
            description='Hair services',
            is_active=True
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Hair Spa',
            slug='hair-spa',
            description='Revitalizing hair spa treatment.',
            short_description='Deep conditioning',
            price=1200.00,
            duration_minutes=60,
            is_active=True,
            is_featured=True
        )

    def test_category_str_and_properties(self):
        self.assertEqual(str(self.category), 'Hair Care')
        self.assertEqual(self.category.active_services_count, 1)
        self.assertIn('category=hair-care', self.category.get_absolute_url())

    def test_service_str_and_properties(self):
        self.assertIn('Hair Spa', str(self.service))
        self.assertEqual(self.service.duration_display, '1h')
        self.assertEqual(self.service.price_display, '₹1,200')
        self.assertEqual(self.service.get_absolute_url(), reverse('services:service_detail', kwargs={'slug': 'hair-spa'}))

    def test_service_list_view(self):
        response = self.client.get(reverse('services:service_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hair Spa')
        self.assertContains(response, 'Hair Care')

    def test_service_list_category_filter(self):
        response = self.client.get(reverse('services:service_list'), {'category': 'hair-care'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hair Spa')

    def test_service_detail_view(self):
        response = self.client.get(reverse('services:service_detail', kwargs={'slug': 'hair-spa'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hair Spa')
        self.assertContains(response, '₹1,200')
