"""Custom views for the glownest project (error handlers)."""
from django.shortcuts import render


def custom_404(request, exception):
    """Custom 404 page."""
    return render(request, 'errors/404.html', status=404)
