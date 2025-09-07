from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import django


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring."""
    return JsonResponse({
        "status": "healthy",
        "version": django.get_version(),
        "service": "CAAS Backend API"
    })
