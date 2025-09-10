from django.apps import AppConfig


class VendorsConfig(AppConfig):
    """
    Configuration for the Vendors app.
    
    TEACHING MOMENT: When Django apps live in subdirectories (like apps/vendors),
    the 'name' must be the full Python path from the project root.
    
    Think of it like giving directions:
    - Wrong: "Go to the store" (Django: Where? Which store?)
    - Right: "Go to apps folder, then vendors folder" (Django: Got it!)
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vendors'  # MUST include 'apps.' prefix for Django to find it!