"""
Global context processors for GlowNest Beauty Studio.
Makes common data available to all templates.
"""
from django.conf import settings


def global_context(request):
    return {
        'business_name': 'GlowNest Beauty Studio',
        'business_tagline': 'Where Beauty Meets Confidence',
        'business_phone': '+91 98765 43210',
        'business_email': 'hello@glownest.com',
        'business_address': '42, Rose Garden Lane, Koramangala, Bangalore - 560034, India',
        'business_city': 'Bangalore',
        'whatsapp_number': settings.WHATSAPP_NUMBER,
        'opening_hours': {
            'weekdays': '9:00 AM – 7:00 PM',
            'saturday': '9:00 AM – 8:00 PM',
            'sunday': '10:00 AM – 5:00 PM',
        },
        'social_links': {
            'instagram': '#',
            'facebook': '#',
            'twitter': '#',
            'youtube': '#',
        },
    }
