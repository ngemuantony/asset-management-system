from core.serializers import AuditableModelSerializer
from .models import Department
from rest_framework import serializers

class DepartmentSerializer(AuditableModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Department
        fields = ('id', 'name', 'description', 'code', 'parent', 'parent_name',
                 'member_count', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def validate_code(self, value):
        """
        Validate department code format.
        """
        if not value.isalnum():
            raise serializers.ValidationError("Department code must be alphanumeric")
        return value.upper() 