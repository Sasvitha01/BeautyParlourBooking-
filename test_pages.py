"""
Template and public page validation tests.
"""
from django.test import TestCase, Client
from services.models import Service, ServiceCategory


class PageRenderingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Hair Care',
            slug='hair-care',
            icon='✂️',
            is_active=True
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Deluxe Hair Spa',
            slug='deluxe-hair-spa',
            description='Relaxing spa for hair.',
            short_description='Hair treatment',
            price=1499.00,
            duration_minutes=60,
            is_active=True,
            is_featured=True
        )

    def test_public_pages_status_and_branding(self):
        pages = [
            ('/', 'Home'),
            ('/services/', 'Services'),
            ('/about/', 'About'),
            ('/contact/', 'Contact'),
            ('/book/', 'Book Appointment'),
            ('/check-booking/', 'Check Booking'),
            ('/privacy/', 'Privacy Policy'),
            ('/terms/', 'Terms'),
        ]
        for url, name in pages:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Page {name} ({url}) returned status {resp.status_code}")
            content = resp.content.decode('utf-8')
            self.assertIn('GlowNest', content)

    def test_service_detail_page_renders_with_image_and_price(self):
        resp = self.client.get(self.service.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        self.assertIn('Deluxe Hair Spa', content)
        self.assertIn('₹1,499', content)
        self.assertIn(self.service.image_url, content)
