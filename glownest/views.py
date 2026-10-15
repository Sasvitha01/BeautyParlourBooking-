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
    """Custom 500 page with diagnostic response headers."""
    exc_type, exc_value, exc_tb = sys.exc_info()
    if not exc_value and hasattr(request, '_view_exception'):
        exc_value = request._view_exception
        exc_type = type(exc_value)

    if exc_value:
        sys.stderr.write(f"500 ERROR: {exc_type.__name__}: {exc_value}\n")

    try:
        response = render(request, 'errors/500.html', status=500)
    except Exception:
        response = HttpResponse("<h1>500 Internal Server Error</h1><p>Something went wrong. Please try again later.</p>", status=500)

    if exc_value:
        response['X-Error-Type'] = str(getattr(exc_type, '__name__', 'Unknown'))
        response['X-Error-Msg'] = str(exc_value).replace('\r', ' ').replace('\n', ' ')[:250]
        if exc_tb:
            tb_lines = traceback.format_tb(exc_tb)
            if tb_lines:
                response['X-Error-Trace'] = tb_lines[-1].replace('\r', ' ').replace('\n', ' ')[:250]
    return response


class DiagnosticExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        import sys, traceback
        sys.stderr.write(f"UNHANDLED EXCEPTION: {type(exception).__name__}: {exception}\n")
        traceback.print_exc()
        request._view_exception = exception
        return None
