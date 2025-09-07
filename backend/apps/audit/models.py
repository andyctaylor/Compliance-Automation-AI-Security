from django.db import models
from django.contrib.auth import get_user_model


class AuditLog(models.Model):
    """
    Tracks all actions in the system for HIPAA compliance.
    These logs must be retained for 7 years.
    """
    # Who performed the action
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,  # Keep log even if user is deleted
        null=True,
        blank=True
    )
    
    # What action was performed
    action = models.CharField(
        max_length=255,
        help_text="What action was performed (e.g., 'viewed_patient_record')"
    )
    
    # Which model/table was affected
    content_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="The type of object that was affected"
    )
    
    # ID of the affected object
    object_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID of the affected object"
    )
    
    # Additional details
    details = models.TextField(
        blank=True,
        help_text="JSON field for additional audit details"
    )
    
    # Network information
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )
    
    # When did this happen
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True  # Index for faster queries
    )
    
    class Meta:
        ordering = ['-timestamp']  # Most recent first
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"