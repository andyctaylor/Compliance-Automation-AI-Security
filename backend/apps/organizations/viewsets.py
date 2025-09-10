"""
Organization ViewSets for CAAS Platform

WHAT THIS FILE DOES:
- Handles all web requests for organizations
- Like a waiter that takes orders (requests) and brings back food (data)
- Controls who can see/edit what (permissions)

FILE LOCATION: backend/apps/organizations/viewsets.py
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Organization, OrganizationMembership
from .serializers import (
    OrganizationSerializer,
    OrganizationCreateSerializer,
    OrganizationMembershipSerializer
)

User = get_user_model()


class OrganizationPermission(IsAuthenticated):
    """
    Security guard that checks if users can access organizations
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access this specific organization"""
        # Everyone can view their own organizations
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return obj.memberships.filter(user=request.user).exists()
        
        # Only admins and managers can edit
        if request.method in ['PUT', 'PATCH']:
            membership = obj.memberships.filter(user=request.user).first()
            return membership and membership.role in ['admin', 'manager']
        
        # Only admins can delete
        if request.method == 'DELETE':
            membership = obj.memberships.filter(user=request.user).first()
            return membership and membership.role == 'admin'
        
        return False


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Main controller for all organization operations
    
    URLS THIS CREATES:
    - GET    /api/v1/organizations/           (list all)
    - POST   /api/v1/organizations/           (create new)
    - GET    /api/v1/organizations/{slug}/    (get one)
    - PUT    /api/v1/organizations/{slug}/    (update)
    - DELETE /api/v1/organizations/{slug}/    (delete)
    """
    
    serializer_class = OrganizationSerializer
    permission_classes = [OrganizationPermission]
    lookup_field = 'slug'  # Use slug in URL instead of ID
    
    def get_queryset(self):
        """Filter to only show user's organizations"""
        if self.request.user.is_superuser:
            return Organization.objects.all()
        
        return Organization.objects.filter(
            memberships__user=self.request.user
        ).distinct()
    
    def get_serializer_class(self):
        """Use different serializer for creating"""
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    @action(detail=True, methods=['get', 'post'], url_path='members')
    def members(self, request, slug=None):
        """
        Manage organization members
        GET  /api/v1/organizations/{slug}/members/
        POST /api/v1/organizations/{slug}/members/
        """
        organization = self.get_object()
        
        if request.method == 'GET':
            # List all members
            memberships = organization.memberships.all()
            serializer = OrganizationMembershipSerializer(
                memberships, 
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Check permissions
            user_membership = organization.memberships.filter(
                user=request.user
            ).first()
            
            if not user_membership or user_membership.role not in ['admin', 'manager']:
                return Response(
                    {'error': 'Only admins and managers can add members'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Add new member
            user_email = request.data.get('email')
            role = request.data.get('role', 'viewer')
            
            try:
                user_to_add = User.objects.get(email=user_email)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if already member
            if organization.memberships.filter(user=user_to_add).exists():
                return Response(
                    {'error': 'User is already a member'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create membership
            membership = OrganizationMembership.objects.create(
                user=user_to_add,
                organization=organization,
                role=role
            )
            
            serializer = OrganizationMembershipSerializer(
                membership,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
    
    @action(detail=False, methods=['get'])
    def my_organizations(self, request):
        """
        Get current user's organizations
        GET /api/v1/organizations/my_organizations/
        """
        memberships = request.user.organization_memberships.all()
        organizations = [m.organization for m in memberships]
        serializer = OrganizationSerializer(
            organizations, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)