"""
Authentication Serializers
These handle data validation and transformation for auth endpoints
Think of them as the security checkpoint at an airport
"""
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from apps.organizations.models import Organization, OrganizationMembership
from django.db import transaction
import hashlib
from django.utils.text import slugify
import json

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


class OrganizationRegistrationSerializer(serializers.Serializer):
    """
    Serializer for the multi-step organization registration process.
    Handles organization creation and admin user setup.
    This is used by the Vue.js multi-step registration form.
    """
    # Step 1: Organization Info
    orgName = serializers.CharField(max_length=255)
    orgType = serializers.CharField(max_length=50, required=False)  # Made optional since not in model
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    adminEmail = serializers.EmailField()
    phoneNumber = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Step 2: Admin Account
    firstName = serializers.CharField(max_length=150)
    lastName = serializers.CharField(max_length=150)
    jobTitle = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=12)  # HIPAA requires 12 chars
    confirmPassword = serializers.CharField(write_only=True)
    mobilePhone = serializers.CharField(max_length=20)
    securityQuestion = serializers.CharField(max_length=255)
    securityAnswer = serializers.CharField(write_only=True)
    
    # Step 3: Terms
    acceptTerms = serializers.BooleanField()
    acceptBAA = serializers.BooleanField()
    acceptMarketing = serializers.BooleanField(required=False)
    
    def validate_adminEmail(self, value):
        """Ensure email is not already registered"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    def validate_password(self, value):
        """
        Enhanced HIPAA-compliant password validation (12 chars minimum)
        """
        # Check minimum length (12 for HIPAA in registration form)
        if len(value) < 12:
            raise serializers.ValidationError(
                'Password must be at least 12 characters long (HIPAA requirement)'
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
            
        # Must contain at least one lowercase letter
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one lowercase letter'
            )
            
        # Must contain at least one special character
        special_characters = '!@#$%^&*(),.?":{}|<>'
        if not any(char in special_characters for char in value):
            raise serializers.ValidationError(
                'Password must contain at least one special character (!@#$%^&*...)'
            )
            
        return value
    
    def validate(self, data):
        """Validate the entire registration data"""
        # Check password confirmation
        if data['password'] != data['confirmPassword']:
            raise serializers.ValidationError({
                'confirmPassword': 'Passwords do not match.'
            })
        
        # Ensure terms are accepted
        if not data['acceptTerms']:
            raise serializers.ValidationError({
                'acceptTerms': 'You must accept the Terms of Service.'
            })
        
        if not data['acceptBAA']:
            raise serializers.ValidationError({
                'acceptBAA': 'You must accept the Business Associate Agreement.'
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create organization and admin user in a transaction.
        This ensures either both are created or neither (atomicity).
        """
        # Create a slug from the organization name
        org_slug = slugify(validated_data['orgName'])
        # Make sure slug is unique
        counter = 1
        while Organization.objects.filter(slug=org_slug).exists():
            org_slug = f"{slugify(validated_data['orgName'])}-{counter}"
            counter += 1
        
        # Extract organization data (only fields that exist in the model)
        org_data = {
            'name': validated_data['orgName'],
            'slug': org_slug,
            'email': validated_data['adminEmail'],
            'phone': validated_data.get('phoneNumber', ''),
            'address': f"{validated_data.get('city', '')}, {validated_data.get('state', '')}",
            'hipaa_agreement_signed': validated_data['acceptBAA'],
        }
        
        # Set HIPAA agreement date if accepted
        if validated_data['acceptBAA']:
            from django.utils import timezone
            org_data['hipaa_agreement_date'] = timezone.now().date()
        
        # Create organization
        organization = Organization.objects.create(**org_data)
        
        # Hash security answer
        security_answer_hash = hashlib.sha256(
            validated_data['securityAnswer'].lower().encode()
        ).hexdigest()
        
        # Create admin user - only add fields that exist in your User model
        user_data = {
            'username': validated_data['adminEmail'],  # Use email as username
            'email': validated_data['adminEmail'],
            'first_name': validated_data['firstName'],
            'last_name': validated_data['lastName'],
        }
        
        # Only add these fields if they exist in your User model
        if hasattr(User, 'job_title'):
            user_data['job_title'] = validated_data['jobTitle']
        if hasattr(User, 'mobile_phone'):
            user_data['mobile_phone'] = validated_data['mobilePhone']
        if hasattr(User, 'security_question'):
            user_data['security_question'] = validated_data['securityQuestion']
        if hasattr(User, 'security_answer_hash'):
            user_data['security_answer_hash'] = security_answer_hash
            
        user = User.objects.create_user(
            password=validated_data['password'],
            **user_data
        )
        
        # Create organization membership as admin
        # Remove is_primary since it doesn't exist in the model
        OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            role='admin'
        )
        
        # Log the registration in audit log
        from apps.audit.models import AuditLog
        AuditLog.objects.create(
            user=user,
            action='create',
            content_type='Organization',  # Changed from model_name to content_type
            object_id=str(organization.id),
            details=json.dumps({  # Changed from changes to details and using json.dumps
                'event': 'organization_registered',
                'org_name': organization.name,
                'admin_email': user.email,
                'user_agent': self.context.get('request').META.get('HTTP_USER_AGENT', '') if self.context.get('request') else ''
            }),
            ip_address=self.context.get('request').META.get('REMOTE_ADDR') if self.context.get('request') else None,
        )
        
        return {
            'user': user,
            'organization': organization,
            'message': 'Registration successful! Please check your email to verify your account.'
        }


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