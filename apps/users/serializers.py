from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, UserActivityLog
from apps.departments.models import Department
from core.constants import ROLE_CHOICES, ROLE_USER
import json

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'firstName', 'lastName', 'is_active')
        read_only_fields = ('id',)
        extra_kwargs = {
            'firstName': {'required': False, 'allow_blank': True},
            'lastName': {'required': False, 'allow_blank': True},
            'email': {'required': False}
        }

    def validate_email(self, value):
        """Validate email is unique"""
        if not value:  # Allow empty email
            return value
            
        # Check if email exists for other users
        user = self.instance  # Get current user if updating
        if User.objects.exclude(pk=user.pk if user else None).filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def to_internal_value(self, data):
        """Handle JSON parsing errors"""
        try:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    raise serializers.ValidationError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Error processing data: {str(e)}")
        return super().to_internal_value(data)

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = UserProfile
        fields = (
            'id', 
            'user', 
            'role', 
            'department', 
            'employee_id', 
            'phone_number',
            'status',
            'is_active'
        )
        read_only_fields = ('id', 'employee_id')

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value in [None, '', 'null']:  # Handle various empty values
            return None
            
        # Convert to string and clean
        try:
            value = str(value)
            cleaned_number = ''.join(filter(str.isdigit, value))
            
            if not cleaned_number:
                return None
                
            if len(cleaned_number) < 9 or len(cleaned_number) > 15:
                raise serializers.ValidationError(
                    "Phone number must be between 9 and 15 digits"
                )
                
            return cleaned_number
        except Exception as e:
            raise serializers.ValidationError(f"Invalid phone number format: {str(e)}")

    def to_internal_value(self, data):
        """Handle JSON parsing errors"""
        try:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    raise serializers.ValidationError(f"Invalid JSON format: {str(e)}")
            
            # Handle nested user data
            if 'user' in data and isinstance(data['user'], str):
                try:
                    data['user'] = json.loads(data['user'])
                except json.JSONDecodeError as e:
                    raise serializers.ValidationError(f"Invalid user data format: {str(e)}")
                    
        except Exception as e:
            raise serializers.ValidationError(f"Error processing data: {str(e)}")
            
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        """Custom update to handle phone number and user data"""
        try:
            # Handle user data updates if provided
            user_data = self.context.get('request').data.get('user', {})
            if user_data:
                if isinstance(user_data, str):
                    try:
                        user_data = json.loads(user_data)
                    except json.JSONDecodeError as e:
                        raise serializers.ValidationError(f"Invalid user data format: {str(e)}")

                user_serializer = UserSerializer(
                    instance.user,
                    data=user_data,
                    partial=True
                )
                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    raise serializers.ValidationError(user_serializer.errors)

            # Handle phone number
            if 'phone_number' in validated_data:
                phone = validated_data.get('phone_number')
                instance.phone_number = phone

            # Update other fields
            for attr, value in validated_data.items():
                if attr != 'phone_number' and value is not None:
                    setattr(instance, attr, value)

            instance.save()
            return instance
            
        except Exception as e:
            raise serializers.ValidationError(f"Update failed: {str(e)}")

class UserActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for UserActivityLog model"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserActivityLog
        fields = [
            'id', 'username', 'action', 'ip_address', 
            'user_agent', 'action_details', 'status', 'timestamp'
        ]
        read_only_fields = fields