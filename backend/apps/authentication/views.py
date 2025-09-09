"""
Authentication ViewSets
Handle authentication endpoints with JWT
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from .serializers import (
    LoginSerializer, 
    UserSerializer, 
    RegisterSerializer,
    TokenResponseSerializer
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
        return UserSerializer
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Real login with JWT tokens
        POST /api/v1/auth/login/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get authenticated user from serializer
        user = serializer.validated_data['user']
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        refresh['email'] = user.email
        
        # Prepare response
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'access_token_expiry': 900  # 15 minutes
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
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
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'message': 'Registration successful! Please verify your email.'
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
    def me(self, request):
        """
        Get current user info
        GET /api/v1/auth/me/
        """
        return Response(UserSerializer(request.user).data)