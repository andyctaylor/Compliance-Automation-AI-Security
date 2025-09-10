"""
Document ViewSets for CAAS Platform

TEACHING MOMENT: ViewSets handle the API endpoints.
They determine what happens when someone makes a request to:
- GET /api/v1/documents/ (list all)
- POST /api/v1/documents/ (create new)
- GET /api/v1/documents/1/ (get specific)
- etc.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Document
from .serializers import (
    DocumentListSerializer,
    DocumentDetailSerializer,
    DocumentUploadSerializer
)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents.
    
    TEACHING: ModelViewSet automatically provides:
    - list() - GET /documents/
    - create() - POST /documents/
    - retrieve() - GET /documents/{id}/
    - update() - PUT /documents/{id}/
    - destroy() - DELETE /documents/{id}/
    """
    permission_classes = [IsAuthenticated]  # Must be logged in
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'vendor__name']  # Can search by name or vendor
    ordering_fields = ['uploaded_at', 'expires_at']
    ordering = ['-uploaded_at']  # Newest first by default
    
    def get_queryset(self):
        """
        Filter documents based on user's organization.
        
        TEACHING: We don't want users seeing documents from other organizations!
        """
        user = self.request.user
        
        # Get all organizations the user belongs to
        user_orgs = user.organization_memberships.values_list(
            'organization', flat=True
        )
        
        # Only show documents from vendors in user's organizations
        return Document.objects.filter(
            vendor__organization__in=user_orgs
        ).select_related('vendor', 'uploaded_by')
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        
        TEACHING: We use lightweight serializer for lists,
        detailed for single document, and upload for creating.
        """
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DocumentUploadSerializer
        return DocumentDetailSerializer

    def perform_create(self, serializer):
        """
        Set the uploader when creating a document.
        
        TEACHING: perform_create runs after validation but before saving.
        Perfect place to set fields the user shouldn't control.
        """
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        Custom endpoint to get documents expiring in next 30 days.
        
        URL: GET /api/v1/documents/expiring_soon/
        
        TEACHING: @action decorator creates custom endpoints beyond CRUD.
        detail=False means it works on the collection, not a single item.
        """
        from datetime import datetime, timedelta
        
        # Get documents expiring in next 30 days
        thirty_days = datetime.now().date() + timedelta(days=30)
        expiring = self.get_queryset().filter(
            expires_at__isnull=False,
            expires_at__lte=thirty_days,
            status='active'
        )
        
        serializer = DocumentListSerializer(
            expiring, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'count': expiring.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get document counts grouped by type.
        
        URL: GET /api/v1/documents/by_type/
        """
        from django.db.models import Count
        
        counts = self.get_queryset().values('document_type').annotate(
            count=Count('id')
        ).order_by('document_type')
        
        # Convert to readable format
        result = {}
        for item in counts:
            doc_type = item['document_type']
            # Find the display name
            for choice in Document.DOCUMENT_TYPE_CHOICES:
                if choice[0] == doc_type:
                    result[choice[1]] = item['count']
                    break
        
        return Response(result)