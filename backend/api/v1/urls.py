"""
API Version 1 URL Configuration
This file defines all the endpoints for version 1 of our API.
Think of it as the menu for our API restaurant!
"""
from django.urls import path
from . import views

# URL patterns for our API
urlpatterns = [
    # Health check endpoint - lets monitoring tools know we're alive
    # GET /api/v1/health/
    path('health/', views.health_check, name='health_check'),
    
    # We'll add more endpoints here like:
    # path('auth/login/', views.login, name='login'),
    # path('vendors/', views.vendor_list, name='vendor_list'),
    # etc.
]