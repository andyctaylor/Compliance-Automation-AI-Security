# backend/config/urls.py
"""
Main URL Configuration

The `urlpatterns` list routes URLs to views. Think of it as a table of contents
for your API - it tells Django where to find each endpoint.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Main URL patterns
urlpatterns = [
    # Django admin interface (for superusers only)
    path('admin/', admin.site.urls),
    
    # API v1 endpoints - all our API URLs start with /api/v1/
    path('api/v1/', include('api.v1.urls')),
    
    # We'll add more API versions later if needed
    # path('api/v2/', include('api.v2.urls')),
]

# In development, serve media and static files directly
# In production, these are served by nginx or CloudFront
if settings.DEBUG:
    # Import debug toolbar URLs
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Serve uploaded files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Serve static files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)