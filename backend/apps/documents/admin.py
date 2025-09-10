"""
Document Admin Configuration

TEACHING MOMENT: Django Admin is a free interface for managing data.
Perfect for staff to verify documents without building custom pages.
Enhanced with categories, tags, and audit logging for better organization.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Document, DocumentCategory, DocumentTag, DocumentAccessLog


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    """Admin for document categories - like folders for organizing."""
    list_display = ['name', 'color_preview', 'icon', 'document_count', 'created_at']
    search_fields = ['name', 'description']
    
    def color_preview(self, obj):
        """Show a preview of the category color."""
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; '
            'border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def document_count(self, obj):
        """Count how many documents are in this category."""
        return obj.documents.count()
    document_count.short_description = 'Documents'


@admin.register(DocumentTag)
class DocumentTagAdmin(admin.ModelAdmin):
    """Admin for document tags - flexible labels."""
    list_display = ['name', 'color_preview', 'document_count', 'created_at']
    search_fields = ['name']
    
    def color_preview(self, obj):
        """Show the tag with its color."""
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 12px;">{}</span>',
            obj.color, obj.name
        )
    color_preview.short_description = 'Tag Preview'
    
    def document_count(self, obj):
        """Count documents with this tag."""
        return obj.documents.count()
    document_count.short_description = 'Used In'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Enhanced admin for documents with categories and version control."""
    
    # What columns to show in the list
    list_display = [
        'name',
        'vendor',
        'category',
        'document_type',
        'status_badge',
        'version',
        'is_latest',
        'expires_at',
        'days_until_expiration',
        'is_verified',
        'uploaded_at'
    ]
    
    # Add filters on the right side - now with more options
    list_filter = [
        'status', 
        'document_type', 
        'category',
        'is_latest',
        'is_verified',
        'expires_at',
        'tags'
    ]
    
    # Make the list searchable
    search_fields = ['name', 'vendor__name', 'notes']
    
    # Allow bulk actions
    actions = ['mark_verified', 'mark_active', 'mark_expired']
    
    # Organize the form into sections
    fieldsets = (
        ('Document Information', {
            'fields': (
                'organization',
                'vendor', 
                'name', 
                'document_type', 
                'category',
                'tags',
                'file'
            )
        }),
        ('Version Control', {
            'fields': (
                'parent_document',
                'version',
                'is_latest',
                'version_notes'
            ),
            'classes': ['collapse'],  # Collapsible section
            'description': 'Leave blank for new documents. Fill for new versions.'
        }),
        ('Dates', {
            'fields': ('document_date', 'expires_at')
        }),
        ('Status & Verification', {
            'fields': (
                'status',
                'is_verified',
                'verified_by',
                'verified_at'
            )
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ['collapse']
        }),
        ('Upload Information', {
            'fields': (
                'uploaded_by',
                'uploaded_at',
                'updated_at',
                'file_size'
            ),
            'classes': ['collapse'],
            'description': 'Automatically captured information'
        }),
    )
    
    # Make some fields read-only
    readonly_fields = [
        'uploaded_at', 
        'updated_at', 
        'file_size',
        'version',  # Auto-calculated
        'days_until_expiration'
    ]
    
    # Inline display of access logs
    class AccessLogInline(admin.TabularInline):
        model = DocumentAccessLog
        extra = 0
        can_delete = False
        can_add = False
        readonly_fields = ['user', 'access_type', 'accessed_at', 'ip_address']
        
        def has_add_permission(self, request, obj=None):
            return False
    
    inlines = [AccessLogInline]
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'active': 'green',
            'expired': 'red',
            'pending_review': 'orange',
            'rejected': 'gray'
        }
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'blue'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def days_until_expiration(self, obj):
        """Show days until expiration with color coding."""
        days = obj.days_until_expiration
        if days is None:
            return '-'
        
        if days < 0:
            color = 'red'
            text = f'Expired {abs(days)} days ago'
        elif days <= 30:
            color = 'orange'
            text = f'{days} days'
        else:
            color = 'green'
            text = f'{days} days'
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text
        )
    days_until_expiration.short_description = 'Expires In'
    
    # Custom admin actions
    def mark_verified(self, request, queryset):
        """Bulk verify documents."""
        count = queryset.update(
            is_verified=True,
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{count} documents marked as verified.')
    mark_verified.short_description = 'Mark selected documents as verified'
    
    def mark_active(self, request, queryset):
        """Bulk mark documents as active."""
        count = queryset.update(status='active')
        self.message_user(request, f'{count} documents marked as active.')
    mark_active.short_description = 'Mark selected documents as active'
    
    def mark_expired(self, request, queryset):
        """Bulk mark documents as expired."""
        count = queryset.update(status='expired')
        self.message_user(request, f'{count} documents marked as expired.')
    mark_expired.short_description = 'Mark selected documents as expired'
    
    def save_model(self, request, obj, form, change):
        """Override to set uploaded_by on creation."""
        if not change:  # New document
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
        
        # Log the action
        if obj.file:
            DocumentAccessLog.objects.create(
                document=obj,
                user=request.user,
                organization=obj.organization,
                access_type='upload' if not change else 'update',
                ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
                user_agent=request.META.get('HTTP_USER_AGENT', 'Django Admin'),
                session_id=request.session.session_key or '',
                changes_made={'action': 'created' if not change else 'updated'}
            )


@admin.register(DocumentAccessLog)
class DocumentAccessLogAdmin(admin.ModelAdmin):
    """
    Read-only admin for HIPAA-compliant access logs.
    These logs cannot be edited or deleted!
    """
    list_display = [
        'accessed_at',
        'user',
        'document',
        'access_type',
        'ip_address',
        'organization'
    ]
    
    list_filter = [
        'access_type',
        'accessed_at',
        'organization',
        'user'
    ]
    
    search_fields = [
        'document__name',
        'user__email',
        'ip_address'
    ]
    
    readonly_fields = [
        'document',
        'user',
        'organization',
        'access_type',
        'ip_address',
        'user_agent',
        'accessed_at',
        'access_reason',
        'session_id',
        'changes_made'
    ]
    
    # Order newest first
    ordering = ['-accessed_at']
    
    # Disable all modifications
    def has_add_permission(self, request):
        """Prevent manual creation - logs should only be created programmatically."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """HIPAA logs should never be deleted."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Logs are immutable."""
        return False
    
    # Custom display for better readability
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related(
            'document', 'user', 'organization'
        )