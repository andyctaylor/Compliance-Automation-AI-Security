"""
Authentication Serializers
These handle data validation and transformation for auth endpoints
Think of them as the security checkpoint at an airport
"""
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()  # This gets your custom User model


class LoginSerializer(serializers.Serializer):
    """
    Handles login validation
    Like a bouncer checking IDs at a club
    """
    # Email field - validates it's a real email format
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required to login',
            'invalid': 'Please enter a valid email address'
        }
    )
    
    # Password field - write_only means it won't be included in responses
    # (you never want to send passwords back to the frontend!)
    password = serializers.CharField(
        write_only=True,  # Critical: Never expose passwords in API responses
        required=True,
        style={'input_type': 'password'},  # Helps API documentation tools
        error_messages={
            'required': 'Password is required to login'
        }
    )
    
    # Remember me flag for extended sessions
    remember_me = serializers.BooleanField(default=False, required=False)
    
    def validate(self, data):
        """
        Custom validation method
        This runs after individual field validation
        Like a second security check after the metal detector
        """
        email = data.get('email')
        password = data.get('password')
        
        # Check if both fields are provided
        if email and password:
            # Django's authenticate expects username, but we use email
            # So we pass email as the username parameter
            user = authenticate(
                request=self.context.get('request'),  # Include request for security
                username=email,  # Django expects 'username' even if we use email
                password=password
            )
            
            # If authentication failed, user will be None
            if not user:
                # Generic error message (don't reveal if email exists!)
                # This prevents attackers from discovering valid emails
                raise serializers.ValidationError(
                    'Unable to login with provided credentials'
                )
                
            # Check if account is active
            if not user.is_active:
                raise serializers.ValidationError(
                    'Account has been deactivated. Contact support.'
                )
                
        else:
            # This shouldn't happen due to required=True above
            # But we're being extra careful (defense in depth)
            raise serializers.ValidationError(
                'Must include both email and password'
            )
            
        # Add the authenticated user to our validated data
        # This lets the view access the user object
        data['user'] = user
        return data


class TwoFactorVerifySerializer(serializers.Serializer):
    """
    Serializer for 2FA verification
    """
    token = serializers.CharField(required=True)  # Temporary token from login
    code = serializers.CharField(max_length=6, min_length=6, required=True)


class TwoFactorResendSerializer(serializers.Serializer):
    """
    Serializer for resending 2FA code
    """
    token = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Converts User model to JSON for API responses
    Simple version with only existing fields
    """
    # Add role and organization fields if they exist
    role = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name', 
            'last_name',
            'last_login',
            'date_joined',
            'role',
            'organization',
            'is_active',
            'is_staff'
        ]
        read_only_fields = ['id', 'last_login', 'date_joined']
    
    def get_role(self, obj):
        """Get user role - default to 'user' if not set"""
        return getattr(obj, 'role', 'user')
    
    def get_organization(self, obj):
        """Get user organization ID if it exists"""
        if hasattr(obj, 'organization'):
            return obj.organization.id if obj.organization else None
        return None


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    
    def validate_old_password(self, value):
        """Verify old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value
    
    def validate_new_password(self, value):
        """
        HIPAA-compliant password validation
        """
        # Check minimum length
        if len(value) < 8:
            raise serializers.ValidationError(
                'Password must be at least 8 characters long'
            )
            
        # Must contain at least one number
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one number'
            )
            
        # Must contain at least one uppercase letter
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one uppercase letter'
            )
            
        # Must contain at least one special character
        special_characters = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(char in special_characters for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one special character (!@#$%^&*...)'
            )
            
        return value


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration with HIPAA-compliant validation
    Like a detailed application form with multiple checks
    """
    # Password with strong validation
    password = serializers.CharField(
        write_only=True,  # Never send back in response
        required=True,
        min_length=8,  # Minimum length check
        max_length=128,  # Prevent DOS with huge passwords
        style={'input_type': 'password'},
        help_text='Minimum 8 characters with uppercase, number, and special character'
    )
    
    # Confirmation password (not saved to model)
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Enter the same password again'
    )
    
    # Agree to terms checkbox
    agree_to_terms = serializers.BooleanField(
        write_only=True,
        required=True,
        error_messages={
            'required': 'You must agree to the terms and conditions'
        }
    )
    
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'agree_to_terms'
        ]
        
    def validate_email(self, value):
        """
        Check if email is already registered
        Runs automatically when validating email field
        """
        # Make email lowercase to prevent duplicates
        email = value.lower()
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'An account with this email already exists'
            )
            
        return email
        
    def validate_password(self, value):
        """
        HIPAA-compliant password validation
        Enforces strong password requirements
        """
        # Check minimum length (redundant with min_length above, but explicit)
        if len(value) < 8:
            raise serializers.ValidationError(
                'Password must be at least 8 characters long'
            )
            
        # Must contain at least one number
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one number'
            )
            
        # Must contain at least one uppercase letter
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one uppercase letter'
            )
            
        # Must contain at least one special character
        special_characters = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(char in special_characters for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one special character (!@#$%^&*...)'
            )
            
        # Check for common passwords (you'd expand this list)
        common_passwords = ['Password123!', 'Admin123!', 'Welcome123!']
        if value in common_passwords:
            raise serializers.ValidationError(
                'This password is too common. Please choose a unique password.'
            )
            
        return value
        
    def validate(self, data):
        """
        Object-level validation
        Runs after all field validations pass
        """
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match"
            })
            
        # Verify terms were agreed to
        if not data.get('agree_to_terms'):
            raise serializers.ValidationError({
                'agree_to_terms': 'You must agree to the terms and conditions'
            })
            
        return data
        
    def create(self, validated_data):
        """
        Create the user account
        This is called when serializer.save() is called
        """
        # Remove fields that aren't part of User model
        validated_data.pop('password_confirm')
        validated_data.pop('agree_to_terms')
        
        # Extract password for special handling
        password = validated_data.pop('password')
        
        # Extract username (we'll use email for both)
        username = validated_data.get('username', validated_data['email'])
        
        # Create user with remaining data
        # Using create_user ensures password is hashed
        user = User.objects.create_user(
            username=username,
            password=password,  # This gets hashed automatically
            **validated_data  # All other fields
        )
        
        return user


class TokenResponseSerializer(serializers.Serializer):
    """
    Formats the login response with tokens and user data
    Like a welcome package for authenticated users
    """
    # JWT access token (short-lived, 15 minutes for HIPAA)
    access = serializers.CharField(
        help_text='JWT access token - expires in 15 minutes'
    )
    
    # Refresh token (longer-lived, 7 days)
    refresh = serializers.CharField(
        help_text='JWT refresh token - expires in 7 days'
    )
    
    # Include user data so frontend doesn't need another API call
    user = UserSerializer(
        help_text='Current user information'
    )
    
    # Token expiry information (helpful for frontend)
    access_token_expiry = serializers.IntegerField(
        help_text='Access token expiry time in seconds',
        default=900  # 15 minutes
    )