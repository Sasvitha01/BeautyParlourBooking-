import sys
import traceback
from django.shortcuts import render
from django.http import HttpResponse


def custom_404(request, exception):
    """Custom 404 page."""
    try:
        return render(request, 'errors/404.html', status=404)
    except Exception:
        return HttpResponse("<h1>404 Page Not Found</h1>", status=404)


def custom_500(request):
    """Custom 500 page."""
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_value:
        sys.stderr.write(f"500 ERROR: {exc_type.__name__}: {exc_value}\n")
    try:
        return render(request, 'errors/500.html', status=500)
    except Exception:
        return HttpResponse("<h1>500 Internal Server Error</h1><p>Something went wrong. Please try again later.</p>", status=500)
