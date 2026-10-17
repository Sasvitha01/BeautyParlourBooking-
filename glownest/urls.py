"""
URL configuration for GlowNest Beauty Studio project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from glownest.sitemaps import StaticPagesSitemap, ServiceDetailSitemap

sitemaps = {
    'static': StaticPagesSitemap,
    'services': ServiceDetailSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-admin/<path:subpath>', RedirectView.as_view(url='/admin/%(subpath)s', permanent=True)),
    path('django-admin/', RedirectView.as_view(url='/admin/', permanent=True)),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include('appointments.urls')),
    path('services/', include('services.urls')),
    path('admin-dashboard/', include('dashboard.urls')),
    path('api/', include('api.urls')),
]

# Serve media files in development and production fallback
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Custom error handlers
handler404 = 'glownest.views.custom_404'
handler500 = 'glownest.views.custom_500'
