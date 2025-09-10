"""
Document Models for CAAS Platform

TEACHING MOMENT: In healthcare, document management is critical:
- Business Associate Agreements (BAAs) must be current
- Insurance certificates need expiration tracking
- Everything needs audit trails for HIPAA
- Categories and tags help organize hundreds of documents
- Version control ensures you always have document history
"""

from django.db import models
from django.utils import timezone
from apps.vendors.models import Vendor
from apps.authentication.models import User
from apps.organizations.models import Organization
from django.core.validators import FileExtensionValidator
import os
import uuid


class DocumentCategory(models.Model):
    """
    Categories for organizing documents (like folders)
    Examples: Insurance, Contracts, Certifications
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='mdi-folder')  # Material Design icon
    color = models.CharField(max_length=7, default='#034c81')  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Document Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DocumentTag(models.Model):
    """
    Tags for flexible document labeling
    Examples: urgent, expires-soon, verified
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#2ca3fa')  # Tag color
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """
    Main document model for vendor compliance documents.
    Enhanced with categories, tags, and version control.
    """
    # Document type choices - common healthcare documents
    DOCUMENT_TYPE_CHOICES = [
        ('baa', 'Business Associate Agreement'),
        ('insurance_coi', 'Certificate of Insurance'),
        ('license', 'Professional License'),
        ('certification', 'Certification'),
        ('contract', 'Contract'),
        ('other', 'Other'),
    ]
    
    # Link to vendor and organization
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,  # If vendor deleted, delete their docs
        related_name='documents'   # Allows vendor.documents.all()
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    # Basic document info
    name = models.CharField(
        max_length=255,
        help_text="Descriptive name for the document"
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text="Type of compliance document"
    )
    
    # NEW: Category and tags for organization
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        help_text="Document category for organization"
    )
    
    tags = models.ManyToManyField(
        DocumentTag,
        blank=True,
        related_name='documents',
        help_text="Tags for flexible filtering"
    )
    
    # The actual file
    file = models.FileField(
        upload_to='documents/%Y/%m/',  # Organizes by year/month
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'png', 'xlsx']
            )
        ],
        help_text="Upload document (PDF, Word, Excel, or image files)"
    )
    
    # Track file size for storage management
    file_size = models.PositiveBigIntegerField(
        help_text="File size in bytes",
        editable=False  # We'll calculate this automatically
    )
    
    # NEW: Version control fields
    version = models.IntegerField(
        default=1, 
        help_text="Document version number"
    )
    
    is_latest = models.BooleanField(
        default=True, 
        help_text="Is this the current version?"
    )
    
    parent_document = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='versions',
        help_text="Link to parent document for versioning"
    )
    
    version_notes = models.TextField(
        blank=True,
        help_text="What changed in this version?"
    )
    
    # Status tracking
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending_review', 'Pending Review'),
        ('rejected', 'Rejected'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_review',  # New docs need review
        help_text="Current status of the document"
    )
    
    # Dates and expiration
    document_date = models.DateField(
        help_text="Date on the document itself"
    )
    
    expires_at = models.DateField(
        null=True,
        blank=True,  # Not all documents expire
        help_text="When this document expires (if applicable)"
    )
    
    # Tracking fields
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # Can't delete user if they have uploads
        related_name='uploaded_documents'
    )
    
    # Optional fields
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this document"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Has this document been verified by admin?"
    )
    
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    
    verified_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Override save to handle file size and versioning."""
        # If there's a file, capture its size
        if self.file:
            self.file_size = self.file.size
        
        # Check if document is expired
        if self.expires_at and self.expires_at < timezone.now().date():
            self.status = 'expired'
        
        # Handle version control
        if self.pk is None and self.parent_document:
            # This is a new version of an existing document
            # Mark all other versions as not latest
            Document.objects.filter(
                parent_document=self.parent_document
            ).update(is_latest=False)
            
            # Set version number
            latest_version = Document.objects.filter(
                parent_document=self.parent_document
            ).order_by('-version').first()
            
            if latest_version:
                self.version = latest_version.version + 1
            else:
                self.version = 2  # Parent is version 1
        
        # Call the parent save method
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if document is expired."""
        if not self.expires_at:
            return False
        return self.expires_at < timezone.now().date()
    
    @property
    def days_until_expiration(self):
        """Calculate days until expiration."""
        if not self.expires_at:
            return None
        delta = self.expires_at - timezone.now().date()
        return delta.days
    
    @property
    def file_url(self):
        """Get the full URL for the file."""
        if self.file:
            return self.file.url
        return None
    
    @property
    def file_extension(self):
        """Get file extension for icon display."""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None
    
    def get_all_versions(self):
        """Get all versions of this document."""
        if self.parent_document:
            # This is a child version
            base_doc = self.parent_document
        else:
            # This might be the parent
            base_doc = self
        
        return Document.objects.filter(
            models.Q(pk=base_doc.pk) | models.Q(parent_document=base_doc)
        ).order_by('-version')

    class Meta:
        ordering = ['-uploaded_at']  # Newest documents first
        indexes = [
            models.Index(fields=['vendor', 'document_type']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['organization', '-uploaded_at']),
            models.Index(fields=['is_latest', '-uploaded_at']),
        ]
        unique_together = [
            ['parent_document', 'version']  # Ensure version numbers are unique per document
        ]
    
    def __str__(self):
        version_str = f" v{self.version}" if self.version > 1 else ""
        return f"{self.vendor.name} - {self.name}{version_str}"


class DocumentAccessLog(models.Model):
    """
    HIPAA-compliant access logging for documents.
    Tracks who accessed what document and when.
    These logs are IMMUTABLE - they cannot be edited or deleted.
    """
    ACCESS_TYPES = [
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('share', 'Shared'),
        ('upload', 'Uploaded'),
        ('verify', 'Verified'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_access_logs'
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='document_access_logs'
    )
    
    access_type = models.CharField(
        max_length=20, 
        choices=ACCESS_TYPES
    )
    
    # Security tracking
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(
        help_text="Browser/client information"
    )
    
    # HIPAA compliance fields
    access_reason = models.TextField(
        blank=True,
        help_text="Reason for accessing PHI (if applicable)"
    )
    
    # Additional metadata
    session_id = models.CharField(
        max_length=40,
        blank=True,
        help_text="Django session ID for tracking"
    )
    
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    # For tracking what changed in updates
    changes_made = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON record of what was changed"
    )
    
    class Meta:
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['document', '-accessed_at']),
            models.Index(fields=['user', '-accessed_at']),
            models.Index(fields=['organization', '-accessed_at']),
            models.Index(fields=['access_type', '-accessed_at']),
        ]
        # Prevent any modifications to logs
        permissions = [
            ("can_view_all_logs", "Can view all access logs"),
            ("can_export_logs", "Can export access logs"),
        ]
    
    def __str__(self):
        return f"{self.user.email} {self.get_access_type_display()} {self.document.name} at {self.accessed_at}"
    
    def save(self, *args, **kwargs):
        # Override save to handle file size and versioning
        # If there's a file, capture its size
        if self.file:
            self.file_size = self.file.size
        
        # Check if document is expired
        if self.expires_at and self.expires_at < timezone.now().date():
            self.status = 'expired'
        
        # Handle version control - FIXED VERSION
        if self.pk is None and self.parent_document:
            # This is a new version of an existing document
            # Get the base document
            base_doc = self.parent_document if self.parent_document.parent_document is None else self.parent_document.parent_document
            
            # Mark ALL versions (including parent) as not latest
            Document.objects.filter(
                models.Q(pk=base_doc.pk) | models.Q(parent_document=base_doc)
            ).update(is_latest=False)
            
            # Set version number
            latest_version = Document.objects.filter(
                models.Q(pk=base_doc.pk) | models.Q(parent_document=base_doc)
            ).order_by('-version').first()
            
            if latest_version:
                self.version = latest_version.version + 1
            else:
                self.version = 2  # Parent is version 1
            
            # This new one will be latest
            self.is_latest = True
        
        # Call the parent save method
        super().save(*args, **kwargs)

    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion."""
        raise ValueError("Access logs cannot be deleted per HIPAA requirements")