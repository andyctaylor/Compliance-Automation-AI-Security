"""
Organization Serializers for CAAS Platform

WHAT THIS FILE DOES:
- Takes your database data and converts it to JSON for the web
- Validates incoming data before saving to database
- Like a security checkpoint that checks all data going in/out

FILE LOCATION: backend/apps/organizations/serializers.py
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMembership

User = get_user_model()


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    """
    Handles data for organization memberships (who works where)
    """
    # These fields show user info instead of just IDs
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OrganizationMembership
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'role',
            'joined_at'
        ]
        read_only_fields = ['joined_at']


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Main serializer for Organization data
    """
    # Custom fields that calculate data
    member_count = serializers.SerializerMethodField()
    current_user_role = serializers.SerializerMethodField()
    
    # Slug validation
    slug = serializers.SlugField(
        required=True,
        help_text="URL-friendly identifier (lowercase, no spaces)"
    )
    
    class Meta:
        model = Organization
        fields = [
            'id',
            'name',
            'slug',
            'email',
            'phone',
            'address',
            'is_active',
            'hipaa_agreement_signed',
            'hipaa_agreement_date',
            'member_count',
            'current_user_role',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        """Count members in this organization"""
        return obj.memberships.count()
    
    def get_current_user_role(self, obj):
        """Get the current user's role"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.memberships.filter(user=request.user).first()
            return membership.role if membership else None
        return None
    
    def validate_slug(self, value):
        """Ensure slug is URL-friendly"""
        import re
        if not re.match(r'^[a-z0-9-]+$', value):
            raise serializers.ValidationError(
                "Slug can only contain lowercase letters, numbers, and hyphens"
            )
        return value
    
    def validate_hipaa_agreement_date(self, value):
        """Validate HIPAA date isn't in future"""
        from datetime import date
        if value and value > date.today():
            raise serializers.ValidationError(
                "HIPAA agreement date cannot be in the future"
            )
        return value


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """
    Special serializer just for creating organizations
    """
    class Meta:
        model = Organization
        fields = [
            'name',
            'slug',
            'email',
            'phone',
            'address',
            'hipaa_agreement_signed',
            'hipaa_agreement_date'
        ]
    
    def create(self, validated_data):
        """Create org and make creator an admin"""
        user = self.context['request'].user
        
        # Create the organization
        organization = Organization.objects.create(**validated_data)
        
        # Make creator an admin
        OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='admin'
        )
        
        return organization