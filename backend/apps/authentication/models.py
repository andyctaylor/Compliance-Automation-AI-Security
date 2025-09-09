"""
Custom User model for HIPAA compliance
We'll build this incrementally to avoid errors
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model - extends Django's built-in User
    For now, we'll keep it simple and add fields gradually
    """
    # Override email to be unique and required
    email = models.EmailField(
        unique=True,
        help_text='Primary email for login and notifications'
    )
    
    # We'll add more fields once basic auth is working
    # organization = models.ForeignKey(...) - Added later
    # role = models.CharField(...) - Added later
    # is_2fa_enabled = models.BooleanField(...) - Added later
    
    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Required for createsuperuser
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'