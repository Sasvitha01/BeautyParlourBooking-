"""
Views for the Services app.
Handles public service listing and detail pages.
"""
from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceCategory


def service_list(request):
    """Display all active services grouped by category."""
    active_category = request.GET.get('category', '')
    try:
        categories = list(ServiceCategory.objects.filter(is_active=True).prefetch_related('services'))
        if active_category:
            services = list(Service.objects.filter(
                is_active=True, category__slug=active_category
            ).select_related('category'))
        else:
            services = list(Service.objects.filter(is_active=True).select_related('category'))
    except Exception as e:
        import sys
        sys.stderr.write(f"[service_list DB warning]: {e}\n")
        categories = []
        services = []

    return render(request, 'public/services.html', {
        'categories': categories,
        'services': services,
        'active_category': active_category,
        'page_title': 'Our Services',
    })


def service_detail(request, slug):
    """Display detail page for a single service."""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    related_services = Service.objects.filter(
        category=service.category, is_active=True
    ).exclude(pk=service.pk)[:4]

    return render(request, 'public/service_detail.html', {
        'service': service,
        'related_services': related_services,
        'page_title': service.name,
    })
