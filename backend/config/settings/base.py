# backend/config/settings/base.py
"""
Base settings for CAAS project.
These settings are common to all environments (dev, staging, production).
Environment-specific settings go in their respective files.
"""
import os
from pathlib import Path
import environ
from datetime import timedelta

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Custom user model
AUTH_USER_MODEL = 'authentication.User'

# Build paths inside the project
# Path(__file__) = this file's location
# .resolve() = absolute path
# .parent.parent.parent = go up 3 directories to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# django-environ helps us read environment variables safely
# It provides type conversion and defaults
env = environ.Env(
    # Set default values and types for variables
    DEBUG=(bool, False),  # DEBUG is a boolean, defaults to False
    ALLOWED_HOSTS=(list, []),  # ALLOWED_HOSTS is a list, defaults to empty
)

# Read .env file if it exists
# This is where your secrets live (and should NEVER be in Git)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: This key is used for cryptographic signing
# In production, this MUST be a long, random string
SECRET_KEY = env('SECRET_KEY', default='CHANGE-ME-IN-PRODUCTION')

# Debug mode shows detailed error pages - NEVER use in production!
DEBUG = env('DEBUG')

# List of hostnames/domains this Django site can serve
# In production, this prevents Host header attacks
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition - the order matters!
DJANGO_APPS = [
    'django.contrib.admin',      # Django's admin interface
    'django.contrib.auth',       # Authentication system
    'django.contrib.contenttypes',  # Content type system
    'django.contrib.sessions',   # Session management
    'django.contrib.messages',   # Message framework
    'django.contrib.staticfiles',  # Static file serving
]

THIRD_PARTY_APPS = [
    'rest_framework',  # Django REST Framework for APIs
    'corsheaders',     # Handle Cross-Origin Resource Sharing
]

# Our custom applications
LOCAL_APPS = [
    'apps.authentication',  # User auth and 2FA
    'apps.audit',          # HIPAA audit logging
    'apps.organizations',   # Multi-tenancy support
    'apps.vendors',        # Vendor management
    'apps.assessments',    # Security assessments
    'apps.documents',  # Documents management
    'drf_spectacular',  # OpenAPI/Swagger support
]

# Combine all apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware is like a pipeline - each request goes through these in order
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Security headers
    'corsheaders.middleware.CorsMiddleware',  # CORS handling (must be early)
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session management
    'django.middleware.common.CommonMiddleware',  # Common utilities
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Attach user to request
    'django.contrib.messages.middleware.MessageMiddleware',  # Message support
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
]

# URL configuration - points to our main URL file
ROOT_URLCONF = 'config.urls'

# Templates configuration (we won't use much since we're API-focused)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application path
WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration
# env.db() reads DATABASE_URL and parses it
# Format: postgres://user:password@host:port/dbname
DATABASES = {
    'default': env.db(default='sqlite:///db.sqlite3')
}

# Password validation - these ensure strong passwords
AUTH_PASSWORD_VALIDATORS = [
    {
        # Prevents passwords too similar to user info
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Requires minimum password length
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # HIPAA recommends strong passwords
        }
    },
    {
        # Prevents common passwords like "password123"
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Prevents all-numeric passwords
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'  # Always use UTC in database, convert in UI
USE_I18N = True    # Enable translations
USE_TZ = True      # Use timezone-aware datetimes

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'  # URL prefix for static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Where collected static files go

# Media files (user uploads)
MEDIA_URL = '/media/'  # URL prefix for media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Where uploaded files are stored

# Default primary key field type
# BigAutoField supports larger datasets than regular AutoField
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework configuration
REST_FRAMEWORK = {
    # How users authenticate to the API
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # We'll add JWT authentication later
    ],
    
    # Who can access the API
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Must be logged in
    ],
    
    # API response format
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # JSON only, no HTML
    ],
    
    # Pagination settings
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,  # Max items per page
    
    # Throttling (rate limiting) - we'll configure this later
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',   # Anonymous users: 100 requests/hour
        'user': '1000/hour',  # Authenticated users: 1000 requests/hour
    },
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# API Documentation settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'CAAS API Documentation',
    'DESCRIPTION': 'HIPAA-compliant vendor risk management platform API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY': [{'bearerAuth': []}],
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
}


# HIPAA-specific security settings
# These ensure data protection and secure communication
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS filtering
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME sniffing
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking

# In production, these MUST be True
if not DEBUG:
    SESSION_COOKIE_SECURE = True  # Only send session cookie over HTTPS
    CSRF_COOKIE_SECURE = True     # Only send CSRF cookie over HTTPS
    SECURE_SSL_REDIRECT = True    # Redirect all HTTP to HTTPS

# Logging configuration for HIPAA compliance
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'audit.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,  # Don't send audit logs to other handlers
        },
    },
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
]

CORS_ALLOW_CREDENTIALS = True