"""
Development settings - unsuitable for production!
Think of this as your 'practice mode' settings.
"""

# Import everything from base settings
from .base import *

# In development, show detailed error pages
DEBUG = True

# In development, accept connections from any computer
ALLOWED_HOSTS = ['*']

# Add development-specific apps
# IMPORTANT: We're EXTENDING the INSTALLED_APPS from base.py, not replacing it
INSTALLED_APPS += [
    'django_extensions',  # Adds helpful commands
    'debug_toolbar',      # Visual debugging tool
]

# Here's the KEY PART - middleware order matters!
# We need to INSERT debug toolbar middleware in the right place
# Find where SecurityMiddleware is in the base MIDDLEWARE list
if 'django.middleware.security.SecurityMiddleware' in MIDDLEWARE:
    # Find its position
    sec_middleware_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    # Create a new middleware list with debug toolbar right after security
    MIDDLEWARE = (
        MIDDLEWARE[:sec_middleware_index + 1] +  # Everything up to and including SecurityMiddleware
        ['debug_toolbar.middleware.DebugToolbarMiddleware'] +  # Add debug toolbar
        MIDDLEWARE[sec_middleware_index + 1:]  # Everything else after
    )
else:
    # Fallback: just add it to the beginning
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Tell debug toolbar which IPs can see it
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Email configuration for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@caas.local'
FRONTEND_URL = 'http://localhost:3000'

# Use SQLite in development if no PostgreSQL is configured
if not env('DATABASE_URL', default=None):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security settings - relaxed for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True