from django.apps import AppConfig


class AuditConfig(AppConfig):
    """
    Configuration for the Audit app.
    Handles HIPAA-compliant audit logging of all system activities.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'  # Full Python path to this app
    verbose_name = 'Audit Logging'  # Human-readable name
    
    def ready(self):
        """
        We'll set up audit log signals here later.
        """
        pass