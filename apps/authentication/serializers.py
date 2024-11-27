import logging
from venv import logger
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from apps.authentication.models import CustomUser
from django.core.cache import cache
from core.serializers import BaseModelSerializer
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# ====================== Custom User Serializer =======================
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model to handle user data.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'firstName', 'lastName', 'date_joined']

    def to_representation(self, instance):
        """Cache the representation"""
        cache_key = f'user_repr_{instance.id}'
        cached_data = cache.get(cache_key)
        
        if not cached_data:
            cached_data = super().to_representation(instance)
            cache.set(cache_key, cached_data, timeout=3600)
        
        return cached_data

# ========================== USER MANAGEMENT SERIALIZERS MODULES =============================

# Serializer for user registration
class RegisterSerializer(BaseModelSerializer):
    """
    Serializer for registering a new user.
    """
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'firstName', 'lastName')

    def validate(self, attrs):
        """
        Validate that password and password2 match and check for unique email and username.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Check email format
        email = attrs.get('email', '').strip().lower()
        if not email:
            raise serializers.ValidationError({"email": "Email is required."})
        
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "User with that email already exists."})
        
        # Check username
        username = attrs.get('username', '').strip()
        if not username:
            raise serializers.ValidationError({"username": "Username is required."})
        
        if CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "User with that username already exists."})
        
        return attrs

    def create(self, validated_data):
        """
        Create a new user with the validated data.
        """
        validated_data.pop('password2')
        user = CustomUser.objects.create(
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        """
        Customize the representation of the user data, excluding the password fields.
        """
        response = super().to_representation(instance)
        response.pop('password', None)
        response.pop('password2', None)
        return response

# Serializer for user login
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login that accepts either username or email.
    """
    usernameOrEmail = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, attrs):
        usernameOrEmail = attrs.get('usernameOrEmail')
        password = attrs.get('password')

        if usernameOrEmail and password:
            # Try to authenticate with username
            user = authenticate(username=usernameOrEmail, password=password)
            
            # If authentication fails, try with email
            if not user:
                try:
                    user_obj = User.objects.get(email=usernameOrEmail)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username/email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

# ===================== User Changing Password ===============================
class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    oldPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)
    newPasswordConfirm = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate that new passwords match.
        """
        if data['newPassword'] != data['newPasswordConfirm']:
            raise serializers.ValidationError("New passwords do not match")
        return data

    def validate_oldPassword(self, value):
        """
        Validate that the old password is correct.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

# ================= Resetting User Password by Sending Reset Token to Email =================
class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset via email.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validate that the email exists in the system.
        """
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("There is no user registered with this email address.")
        return value

# ================ Confirm Password Reset =============================
class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset with a token.
    """
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(max_length=128, write_only=True)
    confirm_new_password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        """
        Validate that new passwords match.
        """
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        return attrs