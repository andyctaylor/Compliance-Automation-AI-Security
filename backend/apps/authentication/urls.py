# backend/apps/authentication/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AuthViewSet,
    TwoFactorVerifyView,
    TwoFactorResendView,
)

app_name = 'authentication'

# Create router for viewset
router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = [
    # Include all viewset routes
    path('', include(router.urls)),
    
    # Additional 2FA endpoints (not part of viewset)
    path('auth/2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa-verify'),
    path('auth/2fa/resend/', TwoFactorResendView.as_view(), name='2fa-resend'),
    
    # JWT refresh endpoint (using simplejwt's view directly)
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

# This creates the following endpoints:
# POST /api/v1/auth/login/
# POST /api/v1/auth/logout/
# POST /api/v1/auth/register/
# POST /api/v1/auth/organization-register/  # NEW
# POST /api/v1/auth/refresh/
# GET  /api/v1/auth/user/
# GET  /api/v1/auth/me/
# POST /api/v1/auth/change-password/
# POST /api/v1/auth/2fa/verify/
# POST /api/v1/auth/2fa/resend/
# POST /api/v1/auth/token/refresh/