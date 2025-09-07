from django.db import models
from django.contrib.auth import get_user_model


class Organization(models.Model):
    """
    Represents a healthcare organization (hospital, clinic, etc.)
    This is the core of our multi-tenancy model.
    """
    name = models.CharField(
        max_length=255,
        help_text="Organization name"
    )
    
    # Unique identifier for the organization
    slug = models.SlugField(
        unique=True,
        help_text="URL-friendly unique identifier"
    )
    
    # Contact information
    email = models.EmailField(
        help_text="Primary contact email"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Primary contact phone"
    )
    
    # Address
    address = models.TextField(
        help_text="Full address"
    )
    
    # HIPAA compliance fields
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this organization can access the system"
    )
    hipaa_agreement_signed = models.BooleanField(
        default=False,
        help_text="Has signed HIPAA Business Associate Agreement"
    )
    hipaa_agreement_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date HIPAA BAA was signed"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    """
    Links users to organizations with specific roles.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff Member'),
        ('viewer', 'Read-Only Viewer'),
    ]
    
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer'
    )
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'organization']  # One membership per user per org
        ordering = ['organization', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"