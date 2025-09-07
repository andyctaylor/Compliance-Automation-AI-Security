from django.db import models
from django.contrib.auth.models import AbstractUser


# We'll extend Django's built-in User model later
# For now, we'll just use the default User model

class TwoFactorSettings(models.Model):
    """
    Stores 2FA settings for each user.
    HIPAA requires strong authentication.
    """
    user = models.OneToOneField(
        'auth.User',  # Reference to Django's User model
        on_delete=models.CASCADE,
        related_name='two_factor_settings'
    )
    is_enabled = models.BooleanField(
        default=False,
        help_text="Whether 2FA is enabled for this user"
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text="Phone number for SMS-based 2FA"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Two-Factor Settings"
        verbose_name_plural = "Two-Factor Settings"
    
    def __str__(self):
        return f"2FA Settings for {self.user.username}"