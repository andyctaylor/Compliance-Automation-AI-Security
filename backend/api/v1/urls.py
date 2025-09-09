"""
API v1 URL Configuration
Maps URL patterns to ViewSets
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.authentication.views import AuthViewSet
from . import views

# Create a router - this automatically generates URL patterns
router = DefaultRouter()

# Register our ViewSets
# basename is used to generate URL names like 'auth-list', 'auth-detail'
router.register(r'auth', AuthViewSet, basename='auth')

# URL patterns
urlpatterns = [
    # Keep our health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # Include all router-generated URLs
    path('', include(router.urls)),
]

# This generates:
# POST /api/v1/auth/login/
# POST /api/v1/auth/register/
# POST /api/v1/auth/logout/
# POST /api/v1/auth/refresh/
# GET  /api/v1/auth/me/
# POST /api/v1/auth/change-password/