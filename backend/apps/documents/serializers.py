"""
Document Serializers for CAAS Platform

TEACHING MOMENT: Serializers are like forms for your API.
They validate data coming in and format data going out.
"""

from rest_framework import serializers
from .models import Document


class DocumentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing documents (lightweight).
    
    When showing a list of many documents, we don't need all details.
    This saves bandwidth and makes the API faster.
    """
    # Add vendor name as a read-only field
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    
    # Add calculated fields from our model
    is_expired = serializers.ReadOnlyField()
    days_until_expiration = serializers.ReadOnlyField()
    
    class Meta:
        model = Document
        fields = [
            'id',
            'name',
            'vendor_name',
            'document_type',
            'status',
            'expires_at',
            'is_expired',
            'days_until_expiration',
            'uploaded_at'
        ]

class DocumentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed document view.
    
    When viewing a single document, we can show all information.
    """
    # Include related object details
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.get_full_name', 
        read_only=True
    )
    
    # Include calculated fields
    is_expired = serializers.ReadOnlyField()
    days_until_expiration = serializers.ReadOnlyField()
    
    # Show file URL
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = '__all__'  # Include all fields for detail view
        read_only_fields = ['file_size', 'uploaded_at', 'updated_at']
    
    def get_file_url(self, obj):
        """Generate the full URL for file download."""
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None


class DocumentUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading new documents.
    
    TEACHING: This handles file uploads and validation.
    """
    class Meta:
        model = Document
        fields = [
            'vendor',
            'name',
            'document_type',
            'file',
            'document_date',
            'expires_at',
        ]
    
    def validate_file(self, value):
        """
        Custom validation for uploaded files.
        
        TEACHING: Always validate file uploads for security!
        """
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "File size cannot exceed 10MB"
            )
        return value
    
    def validate(self, data):
        """
        Cross-field validation.
        
        Example: Insurance certificates MUST have expiration dates.
        """
        doc_type = data.get('document_type')
        expires_at = data.get('expires_at')
        
        # These document types require expiration dates
        requires_expiration = ['baa', 'insurance_coi', 'license']
        
        if doc_type in requires_expiration and not expires_at:
            raise serializers.ValidationError({
                'expires_at': f'{doc_type} documents require an expiration date'
            })
        
        return data
