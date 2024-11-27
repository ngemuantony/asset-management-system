from rest_framework import serializers
from .models import Asset, AssetMaintenance, AssetAssignment, AssetRequest
from apps.categories.serializers import CategorySerializer
from apps.departments.serializers import DepartmentSerializer
from apps.users.serializers import UserProfileSerializer
from apps.tags.serializers import TagSerializer

class AssetMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetMaintenance
        fields = '__all__'

class AssetAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetAssignment
        fields = '__all__'

class AssetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    assigned_to = UserProfileSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    current_value = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    maintenance_records = AssetMaintenanceSerializer(
        many=True, 
        read_only=True
    )
    assignment_history = AssetAssignmentSerializer(
        many=True, 
        read_only=True
    )

    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ('asset_id', 'created_at', 'updated_at')

class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ('asset_id', 'created_at', 'updated_at')

    def validate(self, data):
        if data.get('purchase_price', 0) < 0:
            raise serializers.ValidationError(
                "Purchase price cannot be negative"
            )
        return data

class AssetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetRequest
        fields = '__all__'
        read_only_fields = ('request_status', 'approved_by', 'response_date')

    def validate(self, data):
        if data['asset'].asset_status != 'AVAILABLE':
            raise serializers.ValidationError(
                "This asset is not available for request"
            )
        return data
