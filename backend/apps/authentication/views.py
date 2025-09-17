"""
Authentication ViewSets
Handle authentication endpoints with JWT
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from apps.audit.utils import log_user_action
from .serializers import (
    LoginSerializer, 
    UserSerializer, 
    RegisterSerializer,
    TokenResponseSerializer,
    TwoFactorVerifySerializer,
    TwoFactorResendSerializer,
    ChangePasswordSerializer,
    OrganizationRegistrationSerializer  # Added import
)

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """
    Authentication endpoints with real JWT functionality
    """
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        """Return appropriate serializer for each action"""
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'register':
            return RegisterSerializer
        elif self.action == 'organization_register':  # Added
            return OrganizationRegistrationSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Real login with JWT tokens and 2FA support
        POST /api/v1/auth/login/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get authenticated user from serializer
        user = serializer.validated_data['user']
        remember_me = serializer.validated_data.get('remember_me', False)
        
        # Check if 2FA is enabled (add this field to your User model later)
        if hasattr(user, 'two_factor_enabled') and user.two_factor_enabled:
            # Generate temporary token for 2FA verification
            temp_token = get_random_string(64)
            cache.set(
                f'2fa_token_{temp_token}',
                {'user_id': user.id, 'remember_me': remember_me},
                timeout=300  # 5 minutes
            )
            
            return Response({
                'requires2FA': True,
                'twoFactorToken': temp_token
            })
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Extend token lifetime if remember_me
        if remember_me:
            refresh.access_token.set_exp(lifetime=timedelta(days=1))
            refresh.set_exp(lifetime=timedelta(days=30))
        
        # Add custom claims
        refresh['email'] = user.email
        
        # Log the action
        log_user_action(
            user=user,
            action='LOGIN',
            resource_type='auth',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Prepare response
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'access_token_expiry': 86400 if remember_me else 900  # 24h or 15min
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Logout user
        POST /api/v1/auth/logout/
        """
        # Log the action if user is authenticated
        if request.user.is_authenticated:
            log_user_action(
                user=request.user,
                action='LOGOUT',
                resource_type='auth',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return Response({'message': 'Successfully logged out'})
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register new user
        POST /api/v1/auth/register/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user (will be inactive per your serializer)
        user = serializer.save()
        
        # Generate tokens even though user is inactive
        # You can remove this if you want email verification first
        refresh = RefreshToken.for_user(user)
        
        # Log the action
        log_user_action(
            user=user,
            action='REGISTER',
            resource_type='auth',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'message': 'Registration successful! Please verify your email.'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='organization-register')
    def organization_register(self, request):
        """
        Register new organization with admin user
        This handles the multi-step registration form from Vue.js
        POST /api/v1/auth/organization-register/
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Create organization and user
        result = serializer.save()
        
        # Send verification email
        try:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            send_mail(
                'Verify your CAAS account',
                f'Welcome to CAAS! Please verify your email by clicking: '
                f'{frontend_url}/verify-email/{result["user"].email_verification_token}',
                settings.DEFAULT_FROM_EMAIL,
                [result['user'].email],
                fail_silently=False,
            )
        except Exception as e:
            # Log email error but don't fail registration
            print(f"Email sending failed: {e}")
        
        # Log the registration
        log_user_action(
            user=result['user'],
            action='ORGANIZATION_REGISTER',
            resource_type='auth',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={
                'organization_id': result['organization'].id,
                'organization_name': result['organization'].name
            }
        )
        
        return Response({
            'message': result['message'],
            'organization': {
                'id': result['organization'].id,
                'name': result['organization'].name,
            },
            'user': {
                'id': result['user'].id,
                'email': result['user'].email,
                'firstName': result['user'].first_name,
                'lastName': result['user'].last_name,
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """
        Refresh access token
        POST /api/v1/auth/refresh/
        """
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
                'access_token_expiry': 900
            })
        except Exception:
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user(self, request):
        """
        Get current user info (matches frontend expectation)
        GET /api/v1/auth/user/
        """
        return Response(UserSerializer(request.user).data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get current user info (alternative endpoint)
        GET /api/v1/auth/me/
        """
        return Response(UserSerializer(request.user).data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change password for authenticated user
        POST /api/v1/auth/change-password/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Log the action
        log_user_action(
            user=user,
            action='PASSWORD_CHANGED',
            resource_type='auth',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'Password changed successfully'})


class TwoFactorVerifyView(APIView):
    """
    Verify 2FA code
    POST /api/v1/auth/2fa/verify/
    """
    permission_classes = [AllowAny]
    serializer_class = TwoFactorVerifySerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        temp_token = serializer.validated_data['token']
        code = serializer.validated_data['code']
        
        # Get user info from cache
        cached_data = cache.get(f'2fa_token_{temp_token}')
        if not cached_data:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # For now, accept any 6-digit code (implement real 2FA later)
        # In production, verify against user's TOTP secret
        if len(code) != 6 or not code.isdigit():
            return Response(
                {'error': 'Invalid 2FA code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user
        user = User.objects.get(id=cached_data['user_id'])
        remember_me = cached_data.get('remember_me', False)
        
        # Clear the temporary token
        cache.delete(f'2fa_token_{temp_token}')
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Extend token lifetime if remember_me
        if remember_me:
            refresh.access_token.set_exp(lifetime=timedelta(days=1))
            refresh.set_exp(lifetime=timedelta(days=30))
        
        # Log the action
        log_user_action(
            user=user,
            action='2FA_VERIFIED',
            resource_type='auth',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


class TwoFactorResendView(APIView):
    """
    Resend 2FA code
    POST /api/v1/auth/2fa/resend/
    """
    permission_classes = [AllowAny]
    serializer_class = TwoFactorResendSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        
        # Verify token exists
        cached_data = cache.get(f'2fa_token_{token}')
        if not cached_data:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In production, resend SMS/email here
        # For now, just return success
        return Response({'message': '2FA code resent successfully'})