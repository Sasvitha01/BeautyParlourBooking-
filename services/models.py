"""
Models for the Services app.
Defines ServiceCategory and Service models for GlowNest Beauty Studio.
"""
from django.db import models
from django.urls import reverse


class ServiceCategory(models.Model):
    """Category grouping for beauty services (e.g., Hair Care, Skin Care)."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or emoji")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('services:service_list')}?category={self.slug}"

    @property
    def active_services_count(self):
        return self.services.filter(is_active=True).count()


class Service(models.Model):
    """Individual beauty service offered by the studio."""
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={'slug': self.slug})

    @property
    def duration_display(self):
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours and minutes:
            return f"{hours}h {minutes}min"
        elif hours:
            return f"{hours}h"
        return f"{minutes} min"

    @property
    def price_display(self):
        return f"₹{self.price:,.0f}"

    @property
    def image_url(self):
        """Return URL for service image with static fallback for all services."""
        if self.image:
            try:
                import os
                if os.path.exists(self.image.path):
                    return self.image.url
            except Exception:
                pass
        slug_to_static = {
            'deluxe-hair-spa': 'images/svc-deluxe-hair-spa.jpg',
            'keratin-smoothing': 'images/svc-keratin-smoothing.jpg',
            'layered-cut-blowout': 'images/svc-layered-cut.jpg',
            'glow-radiance-gold-facial': 'images/svc-gold-facial.jpg',
            'oxygen-infusion-cleanup': 'images/svc-oxygen-cleanup.jpg',
            'anti-aging-collagen': 'images/svc-collagen-rejuv.jpg',
            'glam-party-hd-makeup': 'images/makeup.jpg',
            'soft-glam-daytime': 'images/makeup.jpg',
            'royal-bridal-makeover': 'images/bridal.jpg',
            'pre-bridal-radiance': 'images/bridal.jpg',
            'swedish-aromatherapy': 'images/spa.jpg',
            'deep-tissue-herbal': 'images/spa.jpg',
            'rose-gel-pedicure': 'images/nails.jpg',
            'sculpted-gel-extensions': 'images/nails.jpg',
        }
        category_to_static = {
            'hair-care': 'images/hair.jpg',
            'skin-care': 'images/skin.jpg',
            'makeup': 'images/makeup.jpg',
            'bridal': 'images/bridal.jpg',
            'spa-wellness': 'images/spa.jpg',
            'nail-bar': 'images/nails.jpg',
        }
        from django.templatetags.static import static
        if self.slug in slug_to_static:
            return static(slug_to_static[self.slug])
        cat_slug = getattr(self.category, 'slug', '')
        if cat_slug in category_to_static:
            return static(category_to_static[cat_slug])
        return static('images/salon-hero.jpg')
