"""
Vendor Serializers for CAAS Platform

TEACHING MOMENT: Serializers handle 3 main jobs:
1. VALIDATION - Is the incoming data correct?
2. TRANSFORMATION - Convert between Python objects and JSON
3. PRESENTATION - Control what data users see

Think of them as security guards + translators + presenters all in one!
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Vendor, VendorContact
from apps.organizations.models import Organization


class VendorContactSerializer(serializers.ModelSerializer):
    """
    Handles additional vendor contacts.
    
    TEACHING: ModelSerializer automatically creates fields based on your model.
    It's like having a form that auto-generates based on your database table!
    """
    
    class Meta:
        model = VendorContact
        fields = [
            'id',
            'name',
            'title',
            'email', 
            'phone',
            'is_primary',
            'created_at'
        ]
        read_only_fields = ['created_at']  # Users can't manually set creation time


class VendorSerializer(serializers.ModelSerializer):
    """
    Main serializer for Vendor model.
    
    This is like a Swiss Army knife - it handles:
    - Creating new vendors
    - Updating existing vendors
    - Displaying vendor data
    - Validating all vendor information
    """
    
    # TEACHING: SerializerMethodField lets us add calculated fields
    # These don't exist in the database but are computed on the fly
    organization_name = serializers.CharField(
        source='organization.name', 
        read_only=True,
        help_text="Name of the parent organization"
    )
    
    # Show if BAA (Business Associate Agreement) is expiring soon
    baa_expiring_soon = serializers.SerializerMethodField(
        help_text="Is the BAA expiring within 30 days?"
    )
    
    # Show if assessment is overdue
    assessment_overdue = serializers.SerializerMethodField(
        help_text="Is the risk assessment overdue?"
    )
    
    # Count of additional contacts
    contact_count = serializers.SerializerMethodField(
        help_text="Number of contacts for this vendor"
    )
    
    # Risk score with color coding
    risk_color = serializers.SerializerMethodField(
        help_text="Color code for risk visualization"
    )
    
    # TEACHING: SlugField validates that the slug is URL-friendly
    # Example: "ABC Medical, Inc." → "abc-medical-inc"
    slug = serializers.SlugField(
        required=True,
        help_text="URL-friendly identifier (lowercase, hyphens only)"
    )
    
    class Meta:
        model = Vendor
        fields = [
            # Identity fields
            'id',
            'name',
            'slug',
            'vendor_type',
            
            # Organization relationship
            'organization',
            'organization_name',
            
            # Contact information
            'primary_contact_name',
            'email',
            'phone',
            'address',
            'website',
            
            # Risk assessment
            'risk_score',
            'risk_level',
            'risk_color',
            
            # HIPAA compliance
            'handles_phi',
            'baa_signed',
            'baa_signed_date',
            'baa_expiry_date',
            'baa_expiring_soon',
            
            # Compliance tracking
            'compliance_status',
            'last_assessment_date',
            'next_assessment_date',
            'assessment_overdue',
            
            # Service details
            'services_provided',
            'is_critical',
            'is_active',
            
            # Additional info
            'internal_notes',
            'contact_count',
            
            # Timestamps
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'risk_level']  # Auto-calculated
        
    def get_baa_expiring_soon(self, obj):
        """
        Check if BAA expires within 30 days.
        
        TEACHING: This method runs for each vendor when serializing.
        The 'obj' parameter is the Vendor instance being serialized.
        """
        if obj.baa_expiry_date:
            days_until_expiry = (obj.baa_expiry_date - timezone.now().date()).days
            return 0 <= days_until_expiry <= 30  # True if expiring within 30 days
        return False
    
    def get_assessment_overdue(self, obj):
        """
        Check if risk assessment is overdue.
        
        Business Logic: If next_assessment_date is in the past, it's overdue!
        """
        if obj.next_assessment_date:
            return obj.next_assessment_date < timezone.now().date()
        return False
    
    def get_contact_count(self, obj):
        """
        Count additional contacts for this vendor.
        
        TEACHING: 'related_name' in our model lets us access reverse relationships.
        vendor.additional_contacts.count() counts all VendorContacts for this vendor.
        """
        return obj.additional_contacts.count()
    
    def get_risk_color(self, obj):
        """
        Return color code based on risk level for UI visualization.
        
        This helps the frontend display risk levels with appropriate colors:
        - Red for danger
        - Yellow for caution  
        - Green for safe
        """
        color_map = {
            'critical': '#D32F2F',  # Red
            'high': '#F57C00',      # Orange
            'medium': '#FFA000',    # Amber
            'low': '#FDD835',       # Yellow
            'minimal': '#4CAF50',   # Green
        }
        return color_map.get(obj.risk_level, '#9E9E9E')  # Gray if unknown
    
    def validate_slug(self, value):
        """
        Ensure slug is lowercase and URL-friendly.
        
        TEACHING: Custom validation methods are called automatically.
        They must either:
        1. Return the (possibly modified) value if valid
        2. Raise serializers.ValidationError if invalid
        """
        import re
        
        # Check if slug contains only lowercase letters, numbers, and hyphens
        if not re.match(r'^[a-z0-9-]+$', value):
            raise serializers.ValidationError(
                "Slug can only contain lowercase letters, numbers, and hyphens. "
                "Example: 'abc-medical-supplies'"
            )
        return value
    
    def validate_risk_score(self, value):
        """
        Ensure risk score is between 0 and 100.
        
        Even though the model has validators, it's good practice to validate
        in the serializer too for better error messages.
        """
        if not 0 <= value <= 100:
            raise serializers.ValidationError(
                "Risk score must be between 0 and 100"
            )
        return value
    
    def validate_baa_expiry_date(self, value):
        """
        Ensure BAA expiry date is in the future when creating/updating.
        
        Business Rule: You can't set an already-expired BAA!
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError(
                "BAA expiry date cannot be in the past"
            )
        return value
    
    def validate(self, data):
        """
        Object-level validation - check multiple fields together.
        
        TEACHING: This runs after all field-level validations pass.
        Use it when you need to validate relationships between fields.
        """
        # If vendor handles PHI, they MUST have a signed BAA
        if data.get('handles_phi') and not data.get('baa_signed'):
            raise serializers.ValidationError({
                'baa_signed': "Vendors handling PHI must have a signed BAA"
            })
        
        # If BAA is signed, must have a signed date
        if data.get('baa_signed') and not data.get('baa_signed_date'):
            raise serializers.ValidationError({
                'baa_signed_date': "Please provide the date the BAA was signed"
            })
        
        return data


class VendorCreateSerializer(serializers.ModelSerializer):
    """
    Special serializer just for creating vendors.
    
    TEACHING: Why a separate create serializer?
    1. Different fields might be required for creation vs update
    2. We can auto-set fields like organization based on the user
    3. Simpler validation rules for initial creation
    """
    
    class Meta:
        model = Vendor
        fields = [
            'name',
            'slug',
            'vendor_type',
            'primary_contact_name',
            'email',
            'phone',
            'address',
            'website',
            'services_provided',
            'handles_phi',
            'is_critical',
        ]
    
    def create(self, validated_data):
        """
        Create vendor with automatic organization assignment.
        
        TEACHING: The 'context' contains the request object,
        which has the current user. We use this to determine
        which organization the vendor belongs to.
        """
        # Get the user's organization
        user = self.context['request'].user
        
        # Find which organization the user belongs to
        # ASSUMPTION: User belongs to at least one organization
        organization_membership = user.organization_memberships.first()
        
        if not organization_membership:
            raise serializers.ValidationError(
                "You must belong to an organization to create vendors"
            )
        
        # Add the organization to the vendor data
        validated_data['organization'] = organization_membership.organization
        
        # Set default assessment date to 90 days from now
        validated_data['next_assessment_date'] = (
            timezone.now().date() + timedelta(days=90)
        )
        
        # Create and return the vendor
        return Vendor.objects.create(**validated_data)


class VendorListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing vendors.
    
    TEACHING: When displaying lists of many items, use a minimal serializer
    to improve performance. Only include fields needed for the list view!
    """
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    risk_color = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = [
            'id',
            'name',
            'slug',
            'vendor_type',
            'risk_score',
            'risk_level',
            'risk_color',
            'compliance_status',
            'last_assessment_date',
            'is_active',
            'organization_name',
        ]
    
    def get_risk_color(self, obj):
        """Reuse the same color logic for consistency"""
        color_map = {
            'critical': '#D32F2F',
            'high': '#F57C00',
            'medium': '#FFA000',
            'low': '#FDD835',
            'minimal': '#4CAF50',
        }
        return color_map.get(obj.risk_level, '#9E9E9E')