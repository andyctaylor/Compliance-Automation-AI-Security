from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration for the Authentication app.
    Handles user authentication, 2FA, and session management.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'  # Full Python path to this app
    verbose_name = 'Authentication'  # Human-readable name for admin
    
    def ready(self):
        """
        This method is called when Django starts.
        We'll use it later for signals and other initialization.
        """
        pass