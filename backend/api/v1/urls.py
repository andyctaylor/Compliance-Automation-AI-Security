"""
API v1 URL Configuration
Maps URL patterns to ViewSets
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.authentication.views import AuthViewSet
from apps.organizations.viewsets import OrganizationViewSet 
from apps.vendors.viewsets import VendorViewSet 
from apps.assessments.viewsets import AssessmentTemplateViewSet, AssessmentViewSet 
from apps.documents.viewsets import DocumentViewSet
from . import views

# Create a router - this automatically generates URL patterns
router = DefaultRouter()

# Register our ViewSets
# basename is used to generate URL names like 'auth-list', 'auth-detail'
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'vendors', VendorViewSet, basename='vendor') 
router.register(r'assessment-templates', AssessmentTemplateViewSet, basename='assessment-template')  # ADD THIS
router.register(r'assessments', AssessmentViewSet, basename='assessment') 
router.register(r'documents', DocumentViewSet, basename='document')

# URL patterns
urlpatterns = [
    # Keep our health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # Include all router-generated URLs
    path('', include(router.urls)),
]

# This generates:
# POST /api/v1/auth/login/
# POST /api/v1/auth/register/
# POST /api/v1/auth/logout/
# POST /api/v1/auth/refresh/
# GET  /api/v1/auth/me/
# POST /api/v1/auth/change-password/

# NEW URLS ADDED:
# GET    /api/v1/organizations/                    - List all organizations
# POST   /api/v1/organizations/                    - Create new organization
# GET    /api/v1/organizations/{slug}/             - Get specific organization
# PUT    /api/v1/organizations/{slug}/             - Update organization
# DELETE /api/v1/organizations/{slug}/             - Delete organization
# GET    /api/v1/organizations/{slug}/members/     - List organization members
# POST   /api/v1/organizations/{slug}/members/     - Add member to organization
# GET    /api/v1/organizations/my_organizations/   - Get user's organizations