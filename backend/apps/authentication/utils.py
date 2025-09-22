# backend/apps/authentication/utils.py
# Create this new file

import secrets
import string
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

class TwoFactorAuthManager:
    """
    Manages 2FA code generation, storage, and validation.
    Think of this as the security guard who creates temporary access codes.
    """
    
    @staticmethod
    def generate_code():
        """
        Generate a secure 6-digit code.
        Uses cryptographically secure random number generator.
        
        Why use secrets instead of random?
        - secrets uses OS-level randomness (more secure)
        - random is predictable and shouldn't be used for security
        """
        # Create a pool of digits to choose from
        digits = string.digits  # '0123456789'
        
        # Generate a code of specified length
        # secrets.choice is like picking numbers from a lottery machine
        code = ''.join(secrets.choice(digits) for _ in range(settings.TWO_FACTOR_CODE_LENGTH))
        
        return code
    
    @staticmethod
    def store_code(user_id, code, token):
        """
        Store the 2FA code in Redis with user info.
        
        Args:
            user_id: The user's ID
            code: The 6-digit code
            token: Temporary token to link login attempt with 2FA verification
        
        Think of this like putting a time-locked safe deposit box in a bank.
        """
        # Create a unique key for this user's 2FA data
        cache_key = f'2fa:{token}'
        
        # Data to store (like a sealed envelope with multiple items)
        data = {
            'user_id': user_id,
            'code': code,
            'attempts': 0,  # Track failed attempts
            'created_at': timezone.now().isoformat(),
            'last_resend': None,  # Track when code was last resent
        }
        
        # Store in Redis with automatic expiration
        # After timeout, Redis automatically deletes this data (self-destructing message!)
        cache.set(cache_key, data, settings.TWO_FACTOR_CODE_TIMEOUT)
        
        return True
    
    @staticmethod
    def get_code_data(token):
        """
        Retrieve 2FA data from Redis.
        Returns None if expired or doesn't exist.
        """
        cache_key = f'2fa:{token}'
        return cache.get(cache_key)
    
    @staticmethod
    def increment_attempts(token):
        """
        Increment failed attempts counter.
        Like a bouncer keeping track of wrong passwords.
        """
        cache_key = f'2fa:{token}'
        data = cache.get(cache_key)
        
        if data:
            data['attempts'] += 1
            # Update with remaining time
            ttl = cache.ttl(cache_key)  # Get time-to-live
            if ttl > 0:
                cache.set(cache_key, data, ttl)
            return data['attempts']
        return 0
    
    @staticmethod
    def can_resend_code(token):
        """
        Check if enough time has passed since last resend.
        Prevents spam by enforcing cooldown period.
        """
        data = TwoFactorAuthManager.get_code_data(token)
        if not data:
            return False
            
        if not data['last_resend']:
            return True  # First resend is always allowed
            
        # Check if cooldown period has passed
        last_resend = datetime.fromisoformat(data['last_resend'])
        cooldown_end = last_resend + timedelta(seconds=settings.TWO_FACTOR_RESEND_COOLDOWN)
        
        return timezone.now() >= cooldown_end
    
    @staticmethod
    def update_last_resend(token):
        """
        Update the last resend timestamp.
        """
        cache_key = f'2fa:{token}'
        data = cache.get(cache_key)
        
        if data:
            data['last_resend'] = timezone.now().isoformat()
            ttl = cache.ttl(cache_key)
            if ttl > 0:
                cache.set(cache_key, data, ttl)
    
    @staticmethod
    def send_2fa_code(user, code):
        """
        Send 2FA code via email.
        In production, this would use a proper email service.
        
        For development, emails appear in the console.
        """
        subject = 'CAAS - Your Verification Code'
        
        # Plain text version (fallback for older email clients)
        message = f"""
        Your CAAS verification code is: {code}
        
        This code will expire in 5 minutes.
        
        If you didn't request this code, please ignore this email.
        """
        
        # HTML version (what most users will see)
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #034c81;">Your CAAS Verification Code</h2>
            <p>Hi {user.first_name or 'there'},</p>
            <p>Your verification code is:</p>
            <div style="background-color: #f5f5f5; padding: 20px; text-align: center; 
                        border-radius: 8px; margin: 20px 0;">
                <h1 style="color: #034c81; letter-spacing: 8px; margin: 0;">{code}</h1>
            </div>
            <p>This code will expire in 5 minutes.</p>
            <p style="color: #757575; font-size: 14px;">
                If you didn't request this code, please ignore this email.
            </p>
        </div>
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,  # In production, set to True to prevent crashes
        )
    
    @staticmethod
    def clear_code(token):
        """
        Manually clear a 2FA code (e.g., after successful verification).
        Like shredding the temporary access code after use.
        """
        cache_key = f'2fa:{token}'
        cache.delete(cache_key)