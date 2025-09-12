# backend/apps/authentication/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, LogoutView, CurrentUserView,
    TwoFactorVerifyView, TwoFactorResendView,
    ChangePasswordView, TwoFactorSetupView,
    health_check
)

app_name = 'authentication'

urlpatterns = [
    # Auth endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', CurrentUserView.as_view(), name='current-user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # 2FA endpoints
    path('2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa-verify'),
    path('2fa/resend/', TwoFactorResendView.as_view(), name='2fa-resend'),
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='2fa-setup'),
    
    # Password endpoints
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Health check
    path('health/', health_check, name='health-check'),
]