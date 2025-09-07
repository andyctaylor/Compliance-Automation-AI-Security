from django.apps import AppConfig


class OrganizationsConfig(AppConfig):
    """
    Configuration for the Organizations app.
    Handles multi-tenancy - multiple healthcare organizations using the platform.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.organizations'  # Full Python path to this app
    verbose_name = 'Healthcare Organizations'
    
    def ready(self):
        """
        We'll set up organization-specific middleware here later.
        """
        pass