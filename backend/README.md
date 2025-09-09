# backend CAAS Backend - Django REST API

## Overview

The CAAS backend provides a HIPAA-compliant REST API for vendor risk management, built with Django 5.2.6 LTS and Django REST Framework.

## Development Setup

### Using Docker (Recommended)
See main README.md for Docker setup instructions.

### Local Development

1. **Create virtual environment**
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Mac/Linux

2. **Install dependencies**
   pip install -r requirements/development.txt

3. **Set up environment variables**
   cp ../.env.example ../.env
   Edit .env with your database credentials

4. **Run migrations**
   python manage.py migrate

5. **Create superuser**
   python manage.py createsuperuser

6. **Start development server**
   python manage.py runserver

## Project Structure
backend/
├── api/
│   └── v1/              # API version 1 endpoints
│       ├── urls.py      # API URL routing
│       └── views.py     # API views (health check)
├── apps/                # Django applications
│   ├── authentication/  # JWT auth with 2FA
│   ├── audit/          # HIPAA audit logging
│   └── organizations/  # Multi-tenant support
├── config/             # Project configuration
│   ├── settings/       # Environment-specific settings
│   │   ├── base.py     # Common settings
│   │   └── development.py # Dev settings
│   ├── urls.py         # Root URL configuration
│   └── wsgi.py         # WSGI application
├── requirements/       # Dependencies by environment
│   ├── base.txt        # Core dependencies
│   ├── development.txt # Dev tools
│   └── production.txt  # Production deps
├── static/             # Static files
├── media/              # User uploads
├── logs/               # Application logs
└── manage.py           # Django management

## Key Django Apps

### Authentication (apps.authentication)

* JWT token authentication
* Two-factor authentication (2FA)
* Session management with 15-minute timeout (HIPAA)
* Password complexity requirements

### Audit (apps.audit)

* HIPAA-compliant audit logging
* Tracks all data access and modifications
* Immutable audit trail
* Exportable audit reports

### Organizations (apps.organizations)

* Multi-tenant architecture
* Organization-level data isolation
* Role-based access control (RBAC)
* Vendor-organization relationships

## API Endpoints

### Health Check

* GET /api/v1/health/ - System health status

```json
{
  "status": "healthy",
  "version": "5.2.6",
  "service": "CAAS Backend API"
}
```

### Authentication (Coming Soon)

* POST /api/v1/auth/login/ - User login
* POST /api/v1/auth/logout/ - User logout
* POST /api/v1/auth/refresh/ - Refresh JWT token
* POST /api/v1/auth/2fa/verify/ - Verify 2FA code

## Management Commands

### Database
```bash
python manage.py migrate                  # Run migrations
python manage.py makemigrations          # Create migrations
python manage.py dbshell                 # Database shell

# User Management
python manage.py createsuperuser         # Create admin user
python manage.py changepassword <user>   # Change password

# Development
python manage.py runserver               # Start dev server
python manage.py shell_plus              # Enhanced shell
python manage.py show_urls               # Display all URLs

# Testing
python manage.py test                    # Run all tests
python manage.py test apps.authentication # Test specific app

# Static Files
python manage.py collectstatic           # Collect static files
```

## Environment Variables
```bash
Required in .env file:
env# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=caas_db
DB_USER=caas_user
DB_PASSWORD=secure_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000
SESSION_COOKIE_AGE=900  # 15 minutes
``` 

## Development Tools

### Django Extensions

* python manage.py shell_plus - Auto-imports all models
* python manage.py show_urls - Display URL patterns
* python manage.py graph_models - Generate model diagrams

### Django Debug Toolbar

* Available in development at /__debug__/
* Shows SQL queries, templates, cache usage
* Performance profiling

## Testing
Run tests with coverage:
```bash
python manage.py test --coverage
```

## Security Features

1. #### Encryption

* All sensitive fields encrypted at rest
* TLS 1.3 for data in transit
* AES-256 encryption for files

2. #### Authentication

* JWT with short expiration (15 min)
* Refresh tokens (7 days)
* 2FA required for sensitive operations

3. #### Audit Logging

* Every data access logged
* Immutable audit trail
* HIPAA-compliant retention

4. #### Input Validation

* DRF serializers for all inputs
* SQL injection protection
* XSS prevention

## Code Style

* Follow PEP 8
* Use Black for formatting: black .
* Sort imports with isort: isort .
* Type hints where beneficial