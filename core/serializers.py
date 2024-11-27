from rest_framework import serializers
from django.core.exceptions import ValidationError
from .exceptions import BaseAPIException

class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer with common functionality.
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except ValidationError as e:
            raise BaseAPIException(str(e))

class TrackableModelSerializer(BaseModelSerializer):
    """
    Serializer for trackable models.
    """
    last_modified_by = serializers.PrimaryKeyRelatedField(read_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)

class AuditableModelSerializer(TrackableModelSerializer):
    """
    Serializer for auditable models.
    """
    is_active = serializers.BooleanField(read_only=True)
    deactivated_at = serializers.DateTimeField(read_only=True)
    deactivated_by = serializers.PrimaryKeyRelatedField(read_only=True)
