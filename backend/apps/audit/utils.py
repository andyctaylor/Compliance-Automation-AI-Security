"""
Audit logging utilities for HIPAA compliance
Every data access must be logged and immutable
"""
import json
from django.utils import timezone
from .models import AuditLog


def log_user_action(user, action, resource_type, resource_id=None, 
                   ip_address=None, user_agent='', changes=None, details=None):
    """
    Create an audit log entry
    
    Args:
        user: The user performing the action
        action: The action type (LOGIN, CREATE, UPDATE, DELETE, etc.)
        resource_type: What type of resource (vendor, assessment, etc.)
        resource_id: ID of the specific resource
        ip_address: Client IP address
        user_agent: Browser/client information
        changes: Dict of what changed (for updates)
        details: Additional context
        
    This function never fails - audit logging must not break the app
    """
    try:
        # Create the log entry
        log_entry = AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=timezone.now(),
            ip_address=ip_address or 'unknown',
            user_agent=user_agent[:500],  # Truncate long user agents
            changes=json.dumps(changes) if changes else None,
            details=json.dumps(details) if details else None
        )
        
        # For critical actions, you might also send to external log service
        # if action in ['DELETE', 'PASSWORD_CHANGED', 'PERMISSION_CHANGED']:
        #     send_to_siem(log_entry)
        
        return log_entry
        
    except Exception as e:
        # Log to error tracking but don't crash the request
        # In production, use proper error tracking like Sentry
        print(f"Audit log failed: {str(e)}")
        # You might also try to write to a backup log file
        return None


def get_user_activity(user, days=30):
    """
    Get recent activity for a user
    Used for security reviews and user dashboards
    """
    since = timezone.now() - timezone.timedelta(days=days)
    
    return AuditLog.objects.filter(
        user=user,
        timestamp__gte=since
    ).order_by('-timestamp')


def get_resource_history(resource_type, resource_id):
    """
    Get complete history of changes to a resource
    Required for compliance audits
    """
    return AuditLog.objects.filter(
        resource_type=resource_type,
        resource_id=resource_id
    ).order_by('timestamp')