import sys
import traceback


def custom_404(request, exception):
    """Custom 404 page."""
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """Custom 500 page."""
    exc_type, exc_value, exc_tb = sys.exc_info()
    response = render(request, 'errors/500.html', status=500)
    if exc_value:
        sys.stderr.write(f"500 ERROR: {exc_type.__name__}: {exc_value}\n")
        traceback.print_exc()
        response['X-Error-Type'] = str(getattr(exc_type, '__name__', 'Unknown'))
        response['X-Error-Msg'] = str(exc_value).replace('\r', ' ').replace('\n', ' ')[:250]
        if exc_tb:
            tb_lines = traceback.format_tb(exc_tb)
            if tb_lines:
                response['X-Error-Trace'] = tb_lines[-1].replace('\r', ' ').replace('\n', ' ')[:250]
    return response
