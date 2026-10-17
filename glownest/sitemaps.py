"""
Sitemaps for GlowNest Beauty Studio.

Includes only public pages accessible without authentication.
Excludes admin, dashboard, booking confirmation (contains personal data),
and any login-required pages.

The canonical domain is read from settings.SITE_DOMAIN (set via the
SITE_DOMAIN environment variable on Render) so the sitemap always emits
correct absolute URLs regardless of the Django Sites framework DB record.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings

from services.models import Service

# Canonical production domain used in every sitemap <loc> element.
# Set the SITE_DOMAIN environment variable on Render to override.
_CANONICAL_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'beautyparlourbooking-2.onrender.com')


class GlowNestSitemapBase(Sitemap):
    """Base sitemap that always uses the canonical production domain."""
    protocol = 'https'

    def get_domain(self, site=None):
        """Return the canonical domain, ignoring the Sites framework DB record."""
        return _CANONICAL_DOMAIN


class StaticPagesSitemap(GlowNestSitemapBase):
    """Sitemap for static public pages."""

    # (url_name, priority, changefreq)
    _static_urls = [
        ('appointments:home',             1.0, 'daily'),
        ('services:service_list',         0.9, 'weekly'),
        ('appointments:book_appointment', 0.8, 'weekly'),
        ('appointments:about',            0.7, 'monthly'),
        ('appointments:contact',          0.7, 'monthly'),
        ('appointments:check_booking',    0.6, 'monthly'),
        ('appointments:privacy',          0.3, 'monthly'),
        ('appointments:terms',            0.3, 'monthly'),
    ]

    def items(self):
        return self._static_urls

    def location(self, item):
        url_name, _priority, _changefreq = item
        return reverse(url_name)

    def priority(self, item):
        _url_name, prio, _cf = item
        return prio

    def changefreq(self, item):
        _url_name, _prio, cf = item
        return cf


class ServiceDetailSitemap(GlowNestSitemapBase):
    """Sitemap for individual active service detail pages."""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Service.objects.filter(is_active=True).order_by('display_order', 'name')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
