from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.organizations.models import Organization


class Vendor(models.Model):
    """
    Represents a vendor/supplier that provides services to healthcare organizations.
    This is a key model for vendor risk management.
    """
    
    # Link to organization (multi-tenancy)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='vendors',
        help_text="The healthcare organization this vendor serves"
    )
    
    # Basic vendor information
    name = models.CharField(
        max_length=255,
        help_text="Vendor company name"
    )
    
    slug = models.SlugField(
        help_text="URL-friendly identifier for the vendor"
    )
    
    # Vendor type choices
    VENDOR_TYPE_CHOICES = [
        ('medical_device', 'Medical Device Supplier'),
        ('pharmaceutical', 'Pharmaceutical'),
        ('it_services', 'IT Services'),
        ('facility_services', 'Facility Services'),
        ('consulting', 'Consulting'),
        ('staffing', 'Staffing Agency'),
        ('other', 'Other'),
    ]
    
    vendor_type = models.CharField(
        max_length=50,
        choices=VENDOR_TYPE_CHOICES,
        default='other',
        help_text="Type of vendor/service provider"
    )
    
    # Contact information
    primary_contact_name = models.CharField(
        max_length=255,
        help_text="Primary contact person at vendor"
    )
    
    email = models.EmailField(
        help_text="Primary contact email"
    )
    
    phone = models.CharField(
        max_length=20,
        help_text="Primary contact phone"
    )
    
    address = models.TextField(
        help_text="Vendor's business address"
    )
    
    website = models.URLField(
        blank=True,
        help_text="Vendor's website"
    )
    
    # Risk assessment fields
    risk_score = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall risk score (0-100, lower is better)"
    )
    
    RISK_LEVEL_CHOICES = [
        ('critical', 'Critical Risk'),
        ('high', 'High Risk'),
        ('medium', 'Medium Risk'),
        ('low', 'Low Risk'),
        ('minimal', 'Minimal Risk'),
    ]
    
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='medium',
        help_text="Overall risk classification"
    )
    
    # HIPAA compliance fields
    handles_phi = models.BooleanField(
        default=False,
        help_text="Does this vendor handle Protected Health Information?"
    )
    
    baa_signed = models.BooleanField(
        default=False,
        help_text="Business Associate Agreement signed?"
    )
    
    baa_signed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date BAA was signed"
    )
    
    baa_expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="BAA expiration date"
    )
    
    # Compliance status
    COMPLIANCE_STATUS_CHOICES = [
        ('compliant', 'Fully Compliant'),
        ('partial', 'Partially Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('pending', 'Pending Review'),
        ('expired', 'Compliance Expired'),
    ]
    
    compliance_status = models.CharField(
        max_length=20,
        choices=COMPLIANCE_STATUS_CHOICES,
        default='pending',
        help_text="Current compliance status"
    )
    
    last_assessment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last risk assessment"
    )
    
    next_assessment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scheduled date for next assessment"
    )
    
    # Service description
    services_provided = models.TextField(
        help_text="Description of services this vendor provides"
    )
    
    # Critical vendor flag
    is_critical = models.BooleanField(
        default=False,
        help_text="Is this a critical vendor that could impact patient care?"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this vendor currently active?"
    )
    
    # Notes
    internal_notes = models.TextField(
        blank=True,
        help_text="Internal notes about this vendor (not visible to vendor)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['organization', 'slug']  # Unique slug per organization
        
    def __str__(self):
        return f"{self.name} - {self.organization.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate risk level based on risk score
        """
        # Auto-calculate risk level from risk score
        if self.risk_score >= 80:
            self.risk_level = 'critical'
        elif self.risk_score >= 60:
            self.risk_level = 'high'
        elif self.risk_score >= 40:
            self.risk_level = 'medium'
        elif self.risk_score >= 20:
            self.risk_level = 'low'
        else:
            self.risk_level = 'minimal'
            
        super().save(*args, **kwargs)


class VendorContact(models.Model):
    """
    Additional contacts for a vendor (beyond the primary contact)
    """
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='additional_contacts'
    )
    
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Is this the primary contact?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'name']
        
    def __str__(self):
        return f"{self.name} - {self.vendor.name}"