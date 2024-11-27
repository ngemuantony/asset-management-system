from rest_framework import serializers
from .models import AssetRequest, RequestType, RequestApproval
from apps.users.serializers import UserSerializer
from django.utils import timezone

class RequestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestType
        fields = '__all__'

class RequestApprovalSerializer(serializers.ModelSerializer):
    approver = UserSerializer(read_only=True)
    
    class Meta:
        model = RequestApproval
        fields = [
            'id', 'request', 'approver', 'approval_level',
            'status', 'comments', 'approval_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['approval_date', 'created_at', 'updated_at']

class AssetRequestSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    approvals = RequestApprovalSerializer(many=True, read_only=True)
    
    class Meta:
        model = AssetRequest
        fields = [
            'id', 'request_id', 'request_type', 'requester',
            'asset', 'title', 'description', 'priority',
            'status', 'desired_date', 'completion_date',
            'attachments', 'approvals', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'request_id', 'status', 'completion_date',
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        """
        Custom validation for asset requests
        """
        if data.get('desired_date'):
            if data['desired_date'] < timezone.now().date():
                raise serializers.ValidationError(
                    "Desired date cannot be in the past"
                )
        
        # Add more custom validation as needed
        
        return data 