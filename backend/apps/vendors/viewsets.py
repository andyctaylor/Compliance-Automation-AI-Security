"""
Vendor ViewSets for CAAS Platform

TEACHING MOMENT: ViewSets are like restaurant managers - they handle:
1. Taking orders (receiving requests)
2. Checking if customers can order (permissions)
3. Preparing food (processing data)
4. Serving dishes (returning responses)

ViewSets automatically create these endpoints:
- GET /vendors/           → List all vendors
- POST /vendors/          → Create new vendor
- GET /vendors/{slug}/    → Get specific vendor
- PUT /vendors/{slug}/    → Update vendor
- DELETE /vendors/{slug}/ → Delete vendor
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Vendor, VendorContact
from .serializers import (
    VendorSerializer,
    VendorCreateSerializer,
    VendorListSerializer,
    VendorContactSerializer
)
from apps.organizations.models import OrganizationMembership


class VendorPermission(IsAuthenticated):
    """
    Custom permission class for vendor access.
    
    TEACHING: Permissions are like security guards at a building:
    1. First check: Are you even allowed in the building? (IsAuthenticated)
    2. Second check: Which floors can you access? (organization membership)
    3. Third check: What can you do on each floor? (role-based permissions)
    """
    
    def has_permission(self, request, view):
        """
        Check if user has permission to access vendors at all.
        
        This runs BEFORE checking specific object permissions.
        """
        # First, must be logged in (inherited from IsAuthenticated)
        if not super().has_permission(request, view):
            return False
        
        # User must belong to at least one organization
        return request.user.organization_memberships.exists()
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can access this specific vendor.
        
        TEACHING: This is like checking if you have the keycard
        for a specific office within the building.
        """
        # Get user's membership in the vendor's organization
        membership = OrganizationMembership.objects.filter(
            user=request.user,
            organization=obj.organization
        ).first()
        
        if not membership:
            return False  # Not a member of this organization
        
        # Read permissions for all members
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions based on role
        if request.method in ['POST', 'PUT', 'PATCH']:
            # Managers and admins can create/update
            return membership.role in ['admin', 'manager', 'staff']
        
        # Delete permissions for admins only
        if request.method == 'DELETE':
            return membership.role == 'admin'
        
        return False


class VendorViewSet(viewsets.ModelViewSet):
    """
    Main ViewSet for managing vendors.
    
    This is the control center for all vendor operations.
    Like an air traffic controller managing all vendor-related requests!
    
    URLS this creates:
    - GET    /api/v1/vendors/                 → List vendors
    - POST   /api/v1/vendors/                 → Create vendor
    - GET    /api/v1/vendors/{slug}/          → Get vendor details
    - PUT    /api/v1/vendors/{slug}/          → Update vendor
    - PATCH  /api/v1/vendors/{slug}/          → Partial update
    - DELETE /api/v1/vendors/{slug}/          → Delete vendor
    
    Plus custom actions we'll add below!
    """
    
    permission_classes = [VendorPermission]
    lookup_field = 'slug'  # Use slug in URLs instead of ID (prettier!)
    
    # TEACHING: These enable search and filtering in the API
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'services_provided', 'primary_contact_name']
    ordering_fields = ['name', 'risk_score', 'created_at']
    ordering = ['name']  # Default ordering
    
    def get_queryset(self):
        """
        Filter vendors to only those in user's organizations.
        
        TEACHING: This is the foundation of multi-tenancy!
        Users only see vendors from their own organizations.
        
        It's like having different TV channels - you only see
        the channels you're subscribed to.
        """
        user = self.request.user
        
        # Superusers see everything (like having all channels)
        if user.is_superuser:
            return Vendor.objects.all()
        
        # Get user's organizations
        user_orgs = user.organization_memberships.values_list(
            'organization', flat=True
        )
        
        # Filter vendors to only those organizations
        return Vendor.objects.filter(
            organization__in=user_orgs
        ).select_related('organization')  # Optimize database queries
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        
        TEACHING: Like having different forms for different purposes:
        - Job application form (create)
        - Employee update form (update)
        - Employee directory (list)
        - Employee full profile (retrieve)
        """
        if self.action == 'create':
            return VendorCreateSerializer
        elif self.action == 'list':
            return VendorListSerializer
        return VendorSerializer
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """
        Get all high-risk vendors (risk score >= 60).
        
        Custom endpoint: GET /api/v1/vendors/high_risk/
        
        TEACHING: @action decorator creates custom endpoints beyond CRUD.
        detail=False means it applies to the collection, not a specific item.
        """
        high_risk_vendors = self.get_queryset().filter(
            Q(risk_score__gte=60) | Q(risk_level__in=['high', 'critical'])
        )
        
        serializer = VendorListSerializer(
            high_risk_vendors, 
            many=True,
            context={'request': request}
        )
        
        return Response({
            'count': high_risk_vendors.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def expiring_baas(self, request):
        """
        Get vendors with BAAs expiring in the next 30 days.
        
        Custom endpoint: GET /api/v1/vendors/expiring_baas/
        
        Business Value: Helps compliance officers stay ahead of expiring agreements!
        """
        thirty_days_from_now = timezone.now().date() + timedelta(days=30)
        
        expiring = self.get_queryset().filter(
            baa_signed=True,
            baa_expiry_date__lte=thirty_days_from_now,
            baa_expiry_date__gte=timezone.now().date()
        )
        
        serializer = VendorSerializer(
            expiring,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'count': expiring.count(),
            'results': serializer.data,
            'message': f"{expiring.count()} vendors have BAAs expiring within 30 days"
        })
    
    @action(detail=False, methods=['get'])
    def compliance_summary(self, request):
        """
        Get compliance statistics for all vendors.
        
        Custom endpoint: GET /api/v1/vendors/compliance_summary/
        
        TEACHING: Aggregation queries let us calculate statistics
        across multiple records efficiently.
        """
        queryset = self.get_queryset()
        
        # Count vendors by compliance status
        summary = {
            'total_vendors': queryset.count(),
            'active_vendors': queryset.filter(is_active=True).count(),
            'critical_vendors': queryset.filter(is_critical=True).count(),
            'compliance_breakdown': {
                'compliant': queryset.filter(compliance_status='compliant').count(),
                'partial': queryset.filter(compliance_status='partial').count(),
                'non_compliant': queryset.filter(compliance_status='non_compliant').count(),
                'pending': queryset.filter(compliance_status='pending').count(),
                'expired': queryset.filter(compliance_status='expired').count(),
            },
            'risk_breakdown': {
                'critical': queryset.filter(risk_level='critical').count(),
                'high': queryset.filter(risk_level='high').count(),
                'medium': queryset.filter(risk_level='medium').count(),
                'low': queryset.filter(risk_level='low').count(),
                'minimal': queryset.filter(risk_level='minimal').count(),
            },
            'average_risk_score': queryset.aggregate(Avg('risk_score'))['risk_score__avg'],
            'vendors_handling_phi': queryset.filter(handles_phi=True).count(),
            'vendors_with_baa': queryset.filter(baa_signed=True).count(),
        }
        
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def update_risk_score(self, request, slug=None):
        """
        Update a vendor's risk score.
        
        Custom endpoint: POST /api/v1/vendors/{slug}/update_risk_score/
        
        TEACHING: detail=True means this action applies to a specific vendor.
        The URL includes the vendor's slug.
        """
        vendor = self.get_object()
        new_score = request.data.get('risk_score')
        
        # Validate the score
        if new_score is None:
            return Response(
                {'error': 'risk_score is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_score = int(new_score)
            if not 0 <= new_score <= 100:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'risk_score must be an integer between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the score (model's save method will update risk_level)
        vendor.risk_score = new_score
        vendor.save()
        
        serializer = VendorSerializer(vendor, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'], url_path='contacts')
    def contacts(self, request, slug=None):
        """
        Manage additional contacts for a vendor.
        
        GET  /api/v1/vendors/{slug}/contacts/ - List all contacts
        POST /api/v1/vendors/{slug}/contacts/ - Add new contact
        
        TEACHING: One endpoint, multiple HTTP methods = different actions!
        """
        vendor = self.get_object()
        
        if request.method == 'GET':
            # List all contacts for this vendor
            contacts = vendor.additional_contacts.all()
            serializer = VendorContactSerializer(
                contacts,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Create new contact
            serializer = VendorContactSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                # Associate the contact with this vendor
                serializer.save(vendor=vendor)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get vendors grouped by type.
        
        Custom endpoint: GET /api/v1/vendors/by_type/
        
        Useful for reports and analytics dashboards!
        """
        vendor_types = Vendor.VENDOR_TYPE_CHOICES
        
        results = {}
        for type_code, type_name in vendor_types:
            vendors = self.get_queryset().filter(vendor_type=type_code)
            results[type_code] = {
                'name': type_name,
                'count': vendors.count(),
                'vendors': VendorListSerializer(
                    vendors[:5],  # Top 5 for each type
                    many=True,
                    context={'request': request}
                ).data
            }
        
        return Response(results)
    
    def perform_create(self, serializer):
        """
        Hook that runs when creating a vendor.
        
        TEACHING: perform_* methods let us add custom logic
        during standard operations without overriding everything.
        """
        # The serializer handles organization assignment
        serializer.save()
        
        # Log the creation (you could add audit logging here)
        print(f"New vendor created: {serializer.instance.name}")
    
    def perform_destroy(self, instance):
        """
        Soft delete instead of hard delete.
        
        TEACHING: Sometimes we don't want to actually delete data
        (for audit trails), so we just mark it as inactive.
        """
        instance.is_active = False
        instance.save()
        
        # Log the soft deletion
        print(f"Vendor deactivated: {instance.name}")